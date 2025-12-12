using System;
using System.ComponentModel;
using System.Diagnostics;
using System.IO;
using System.Text;
using System.Threading.Tasks;
using System.Windows;
using System.Windows.Input;

namespace HumankindApp;

public partial class MainWindow : Window
{
    private readonly MainViewModel _viewModel = new();

    public MainWindow()
    {
        InitializeComponent();
        DataContext = _viewModel;
    }

    protected override void OnClosed(EventArgs e)
    {
        _viewModel.Dispose();
        base.OnClosed(e);
    }
}

public class MainViewModel : INotifyPropertyChanged, IDisposable
{
    private string _configPath = "configs/humankind3.yaml";
    private string _profile = "windowed";
    private string _pythonExecutable = "python";
    private string _outputLog = string.Empty;
    private Process? _process;
    private bool _isRunning;
    private readonly ICommand _runCalibrationCommand;
    private readonly ICommand _stopCalibrationCommand;

    public event PropertyChangedEventHandler? PropertyChanged;

    public MainViewModel()
    {
        _runCalibrationCommand = new RelayCommand(async _ => await RunCalibrationAsync(), _ => !_isRunning);
        _stopCalibrationCommand = new RelayCommand(_ => StopCalibration(), _ => _isRunning);
    }

    public string ConfigPath
    {
        get => _configPath;
        set
        {
            if (_configPath != value)
            {
                _configPath = value;
                OnPropertyChanged(nameof(ConfigPath));
            }
        }
    }

    public string Profile
    {
        get => _profile;
        set
        {
            if (_profile != value)
            {
                _profile = value;
                OnPropertyChanged(nameof(Profile));
            }
        }
    }

    public string PythonExecutable
    {
        get => _pythonExecutable;
        set
        {
            if (_pythonExecutable != value)
            {
                _pythonExecutable = value;
                OnPropertyChanged(nameof(PythonExecutable));
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

    public ICommand RunCalibrationCommand => _runCalibrationCommand;
    public ICommand StopCalibrationCommand => _stopCalibrationCommand;

    public async Task RunCalibrationAsync()
    {
        if (_isRunning)
        {
            return;
        }

        var startInfo = new ProcessStartInfo
        {
            FileName = PythonExecutable,
            Arguments = $"-m hk3_bot.calibration --config \"{ConfigPath}\" --profile {Profile}",
            RedirectStandardOutput = true,
            RedirectStandardError = true,
            UseShellExecute = false,
            CreateNoWindow = true,
            StandardOutputEncoding = Encoding.UTF8,
            StandardErrorEncoding = Encoding.UTF8
        };

        if (string.IsNullOrWhiteSpace(ConfigPath) || !File.Exists(ConfigPath))
        {
            AppendLine("Config file was not found. Check the path before starting.");
            return;
        }

        AppendLine($"Starting calibration with profile '{Profile}'...");

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
            _isRunning = false;
            AppendLine("Calibration finished or exited.");
            CommandManager.InvalidateRequerySuggested();
        };

        try
        {
            _isRunning = _process.Start();
            CommandManager.InvalidateRequerySuggested();
            _process.BeginOutputReadLine();
            _process.BeginErrorReadLine();
            await _process.WaitForExitAsync();
        }
        catch (Exception ex)
        {
            AppendLine($"Failed to start calibration: {ex.Message}");
            _isRunning = false;
            CommandManager.InvalidateRequerySuggested();
        }
    }

    public void StopCalibration()
    {
        if (_process == null || _process.HasExited)
        {
            AppendLine("No calibration run is active.");
            _isRunning = false;
            CommandManager.InvalidateRequerySuggested();
            return;
        }

        try
        {
            _process.Kill();
            _process.Dispose();
            AppendLine("Calibration stopped by user.");
        }
        catch (Exception ex)
        {
            AppendLine($"Unable to stop process: {ex.Message}");
        }
        finally
        {
            _isRunning = false;
            CommandManager.InvalidateRequerySuggested();
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
                    _process.Kill();
                }
            }
            catch
            {
                // ignore
            }

            _process.Dispose();
        }
    }
}

public class RelayCommand : ICommand
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
