using System;
using System.ComponentModel;
using System.Diagnostics;
using System.IO;
using System.Text;
using System.Threading.Tasks;
using System.Windows;
using System.Windows.Input;
using HumankindApp.Services;

namespace HumankindApp.ViewModels;

public sealed class AppViewModel : INotifyPropertyChanged, IDisposable
{
    private readonly SettingsStore _store = new();
    private AppSettings _settings;

    private string _outputLog = string.Empty;
    private Process? _process;
    private bool _isRunning;

    public event PropertyChangedEventHandler? PropertyChanged;

    public AppViewModel()
    {
        _settings = _store.Load();
        _geminiApiKey = SettingsStore.UnprotectString(_settings.EncryptedGeminiApiKey) ?? string.Empty;

        RunCalibrationCommand = new RelayCommand(async _ => await RunCalibrationAsync(), _ => !_isRunning);
        RunAgentCommand = new RelayCommand(async _ => await RunAgentAsync(), _ => !_isRunning);
        StopCommand = new RelayCommand(_ => Stop(), _ => _isRunning);
        SaveSettingsCommand = new RelayCommand(_ => SaveSettings(), _ => true);
        SaveLogCommand = new RelayCommand(_ => SaveLog());
        ClearOutputCommand = new RelayCommand(_ => ClearOutput());
    }

    public string ConfigPath
    {
        get => _settings.ConfigPath;
        set
        {
            if (_settings.ConfigPath != value)
            {
                _settings.ConfigPath = value;
                OnPropertyChanged(nameof(ConfigPath));
            }
        }
    }

    public string Profile
    {
        get => _settings.Profile;
        set
        {
            if (_settings.Profile != value)
            {
                _settings.Profile = value;
                OnPropertyChanged(nameof(Profile));
            }
        }
    }

    public string PythonExecutable
    {
        get => _settings.PythonExecutable;
        set
        {
            if (_settings.PythonExecutable != value)
            {
                _settings.PythonExecutable = value;
                OnPropertyChanged(nameof(PythonExecutable));
            }
        }
    }

    public string Planner
    {
        get => _settings.Planner;
        set
        {
            if (_settings.Planner != value)
            {
                _settings.Planner = value;
                OnPropertyChanged(nameof(Planner));
            }
        }
    }

    public string GeminiModel
    {
        get => _settings.GeminiModel;
        set
        {
            if (_settings.GeminiModel != value)
            {
                _settings.GeminiModel = value;
                OnPropertyChanged(nameof(GeminiModel));
            }
        }
    }

    public double GeminiIntervalSeconds
    {
        get => _settings.GeminiIntervalSeconds;
        set
        {
            if (Math.Abs(_settings.GeminiIntervalSeconds - value) > 0.0001)
            {
                _settings.GeminiIntervalSeconds = value;
                OnPropertyChanged(nameof(GeminiIntervalSeconds));
            }
        }
    }

    public bool GeminiSendVision
    {
        get => _settings.GeminiSendVision;
        set
        {
            if (_settings.GeminiSendVision != value)
            {
                _settings.GeminiSendVision = value;
                OnPropertyChanged(nameof(GeminiSendVision));
            }
        }
    }

    public bool AssistMode
    {
        get => _settings.AssistMode;
        set
        {
            if (_settings.AssistMode != value)
            {
                _settings.AssistMode = value;
                OnPropertyChanged(nameof(AssistMode));
            }
        }
    }

    public bool DebugMode
    {
        get => _settings.DebugMode;
        set
        {
            if (_settings.DebugMode != value)
            {
                _settings.DebugMode = value;
                OnPropertyChanged(nameof(DebugMode));
            }
        }
    }

    public int? FpsOverride
    {
        get => _settings.FpsOverride;
        set
        {
            if (_settings.FpsOverride != value)
            {
                _settings.FpsOverride = value;
                OnPropertyChanged(nameof(FpsOverride));
            }
        }
    }

    public bool DryRun
    {
        get => _settings.DryRun;
        set
        {
            if (_settings.DryRun != value)
            {
                _settings.DryRun = value;
                OnPropertyChanged(nameof(DryRun));
            }
        }
    }

    private string _geminiApiKey;

    public string GeminiApiKey
    {
        get => _geminiApiKey;
        set
        {
            if (_geminiApiKey != value)
            {
                _geminiApiKey = value;
                OnPropertyChanged(nameof(GeminiApiKey));
            }
        }
    }

    public string OutputLog
    {
        get => _outputLog;
        set
        {
            if (_outputLog != value)
            {
                _outputLog = value;
                OnPropertyChanged(nameof(OutputLog));
            }
        }
    }

    public bool IsRunning
    {
        get => _isRunning;
        private set
        {
            if (_isRunning != value)
            {
                _isRunning = value;
                OnPropertyChanged(nameof(IsRunning));
                CommandManager.InvalidateRequerySuggested();
            }
        }
    }

    public ICommand RunCalibrationCommand { get; }
    public ICommand RunAgentCommand { get; }
    public ICommand StopCommand { get; }
    public ICommand SaveSettingsCommand { get; }
    public ICommand SaveLogCommand { get; }
    public ICommand ClearOutputCommand { get; }

    public void SaveSettings()
    {
        if (!string.IsNullOrWhiteSpace(GeminiApiKey))
        {
            _settings.EncryptedGeminiApiKey = SettingsStore.ProtectString(GeminiApiKey);
        }
        else
        {
            _settings.EncryptedGeminiApiKey = null;
        }

        _store.Save(_settings);
        AppendLine("Settings saved.");
    }

    private void SaveLog()
    {
        try
        {
            var logsDir = Path.Combine(AppDomain.CurrentDomain.BaseDirectory, "logs");
            Directory.CreateDirectory(logsDir);
            var filename = $"session_{DateTime.Now:yyyyMMdd_HHmmss}.log";
            var filepath = Path.Combine(logsDir, filename);
            File.WriteAllText(filepath, OutputLog);
            AppendLine($"Log saved to: {filepath}");
        }
        catch (Exception ex)
        {
            AppendLine($"Failed to save log: {ex.Message}");
        }
    }

    private void ClearOutput()
    {
        OutputLog = string.Empty;
    }

    private static string? FindRepoRoot()
    {
        var dir = AppDomain.CurrentDomain.BaseDirectory;
        var current = new DirectoryInfo(dir);
        while (current != null)
        {
            var src = Path.Combine(current.FullName, "src");
            var configs = Path.Combine(current.FullName, "configs");
            if (Directory.Exists(src) && Directory.Exists(configs))
            {
                return current.FullName;
            }
            current = current.Parent;
        }
        return null;
    }

    private static string ResolveRepoPath(string repoRoot, string path)
    {
        if (Path.IsPathRooted(path))
        {
            return path;
        }
        return Path.Combine(repoRoot, path);
    }

    private ProcessStartInfo BuildPythonProcessStart(string args)
    {
        var repoRoot = FindRepoRoot();
        if (repoRoot == null)
        {
            throw new InvalidOperationException("Unable to locate repo root. Make sure the EXE is inside the repo folder tree.");
        }

        var configFull = ResolveRepoPath(repoRoot, ConfigPath);
        if (!File.Exists(configFull))
        {
            throw new FileNotFoundException("Config file was not found.", configFull);
        }

        var startInfo = new ProcessStartInfo
        {
            FileName = PythonExecutable,
            Arguments = args,
            RedirectStandardOutput = true,
            RedirectStandardError = true,
            UseShellExecute = false,
            CreateNoWindow = true,
            StandardOutputEncoding = Encoding.UTF8,
            StandardErrorEncoding = Encoding.UTF8,
            WorkingDirectory = repoRoot,
        };

        startInfo.Environment["PYTHONPATH"] = Path.Combine(repoRoot, "src");
        startInfo.Environment["PYTHONIOENCODING"] = "utf-8";

        if (!string.IsNullOrWhiteSpace(GeminiApiKey))
        {
            startInfo.Environment["GEMINI_API_KEY"] = GeminiApiKey;
        }

        return startInfo;
    }

    public async Task RunCalibrationAsync()
    {
        if (IsRunning)
        {
            return;
        }

        try
        {
            AppendLine("Starting calibration...");
            var args = $"-m hk3_bot.calibration --config \"{ConfigPath}\" --profile {Profile}";
            var startInfo = BuildPythonProcessStart(args);
            await StartProcessAsync(startInfo);
        }
        catch (Exception ex)
        {
            AppendLine($"Failed to start calibration: {ex.Message}");
            IsRunning = false;
        }
    }

    public async Task RunAgentAsync()
    {
        if (IsRunning)
        {
            return;
        }

        try
        {
            AppendLine("Starting agent runner...");

            var sb = new StringBuilder();
            sb.Append("-m hk3_bot.run ");
            sb.Append($"--config \"{ConfigPath}\" ");
            sb.Append($"--profile {Profile} ");
            sb.Append($"--planner {Planner} ");

            if (AssistMode)
            {
                sb.Append("--assist ");
            }
            if (DebugMode)
            {
                sb.Append("--debug ");
            }
            if (DryRun)
            {
                sb.Append("--dry-run ");
            }
            if (FpsOverride.HasValue)
            {
                sb.Append($"--fps {FpsOverride.Value} ");
            }

            if (string.Equals(Planner, "gemini", StringComparison.OrdinalIgnoreCase))
            {
                sb.Append($"--gemini-model {GeminiModel} ");
                sb.Append($"--gemini-interval {GeminiIntervalSeconds} ");
                if (!GeminiSendVision)
                {
                    sb.Append("--gemini-no-vision ");
                }
            }

            var startInfo = BuildPythonProcessStart(sb.ToString());
            await StartProcessAsync(startInfo);
        }
        catch (Exception ex)
        {
            AppendLine($"Failed to start agent: {ex.Message}");
            IsRunning = false;
        }
    }

    private async Task StartProcessAsync(ProcessStartInfo startInfo)
    {
        _process = new Process { StartInfo = startInfo, EnableRaisingEvents = true };
        _process.OutputDataReceived += (_, args) =>
        {
            if (args.Data != null)
            {
                AppendLine(args.Data);
            }
        };
        _process.ErrorDataReceived += (_, args) =>
        {
            if (args.Data != null)
            {
                AppendLine($"[error] {args.Data}");
            }
        };
        _process.Exited += (_, _) =>
        {
            IsRunning = false;
            AppendLine("Process exited.");
        };

        IsRunning = _process.Start();
        _process.BeginOutputReadLine();
        _process.BeginErrorReadLine();
        await _process.WaitForExitAsync();
    }

    public void Stop()
    {
        if (_process == null || _process.HasExited)
        {
            AppendLine("No process is running.");
            IsRunning = false;
            return;
        }

        try
        {
            _process.Kill(entireProcessTree: true);
            _process.Dispose();
            AppendLine("Stopped.");
        }
        catch (Exception ex)
        {
            AppendLine($"Unable to stop process: {ex.Message}");
        }
        finally
        {
            IsRunning = false;
        }
    }

    private void AppendLine(string message)
    {
        var timestamp = DateTime.Now.ToString("HH:mm:ss");
        var line = $"[{timestamp}] {message}";

        if (Application.Current?.Dispatcher != null)
        {
            Application.Current.Dispatcher.Invoke(() => OutputLog += line + Environment.NewLine);
        }
        else
        {
            OutputLog += line + Environment.NewLine;
        }
    }

    private void OnPropertyChanged(string propertyName) =>
        PropertyChanged?.Invoke(this, new PropertyChangedEventArgs(propertyName));

    public void Dispose()
    {
        if (_process != null)
        {
            try
            {
                if (!_process.HasExited)
                {
                    _process.Kill(entireProcessTree: true);
                }
            }
            catch
            {
            }

            _process.Dispose();
        }
    }
}

public sealed class RelayCommand : ICommand
{
    private readonly Predicate<object?>? _canExecute;
    private readonly Func<object?, Task>? _asyncExecute;
    private readonly Action<object?>? _syncExecute;

    public RelayCommand(Func<object?, Task> execute, Predicate<object?>? canExecute = null)
    {
        _asyncExecute = execute;
        _canExecute = canExecute;
    }

    public RelayCommand(Action<object?> execute, Predicate<object?>? canExecute = null)
    {
        _syncExecute = execute;
        _canExecute = canExecute;
    }

    public event EventHandler? CanExecuteChanged
    {
        add => CommandManager.RequerySuggested += value;
        remove => CommandManager.RequerySuggested -= value;
    }

    public bool CanExecute(object? parameter) => _canExecute?.Invoke(parameter) ?? true;

    public async void Execute(object? parameter)
    {
        if (_asyncExecute != null)
        {
            await _asyncExecute(parameter);
            return;
        }

        _syncExecute?.Invoke(parameter);
    }
}
