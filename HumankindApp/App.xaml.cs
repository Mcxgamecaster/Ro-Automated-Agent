using System;
using System.IO;
using System.Threading.Tasks;
using System.Windows;
using System.Windows.Threading;
using HumankindApp.ViewModels;

namespace HumankindApp;

public partial class App : Application
{
    public AppViewModel? ViewModel { get; private set; }

    protected override void OnStartup(StartupEventArgs e)
    {
        DispatcherUnhandledException += OnDispatcherUnhandledException;
        AppDomain.CurrentDomain.UnhandledException += OnDomainUnhandledException;
        TaskScheduler.UnobservedTaskException += OnUnobservedTaskException;

        try
        {
            ViewModel = new AppViewModel();
        }
        catch (Exception ex)
        {
            HandleFatalException(ex);
            Shutdown(-1);
            return;
        }

        base.OnStartup(e);
    }

    protected override void OnExit(ExitEventArgs e)
    {
        ViewModel?.Dispose();
        base.OnExit(e);
    }

    private void OnDispatcherUnhandledException(object sender, DispatcherUnhandledExceptionEventArgs e)
    {
        HandleFatalException(e.Exception);
        e.Handled = true;
        Shutdown(-1);
    }

    private void OnDomainUnhandledException(object? sender, UnhandledExceptionEventArgs e)
    {
        if (e.ExceptionObject is Exception ex)
        {
            HandleFatalException(ex);
        }
        Shutdown(-1);
    }

    private void OnUnobservedTaskException(object? sender, UnobservedTaskExceptionEventArgs e)
    {
        HandleFatalException(e.Exception);
        e.SetObserved();
        Shutdown(-1);
    }

    private static void HandleFatalException(Exception ex)
    {
        string logPath;

        try
        {
            logPath = WriteCrashLog(ex);
        }
        catch
        {
            logPath = "(unable to write crash log)";
        }

        MessageBox.Show(
            $"HumankindApp crashed on startup.\n\n{ex.GetType().Name}: {ex.Message}\n\nCrash log:\n{logPath}",
            "HumankindApp",
            MessageBoxButton.OK,
            MessageBoxImage.Error
        );
    }

    private static string WriteCrashLog(Exception ex)
    {
        var dir = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.ApplicationData), "HumankindApp");
        Directory.CreateDirectory(dir);
        var path = Path.Combine(dir, "crash.log");

        var text = $"[{DateTime.Now:O}] {ex}\n\n";

        try
        {
            AppendAllTextShared(path, text);
            return path;
        }
        catch
        {
            var fallback = Path.Combine(dir, $"crash_{DateTime.Now:yyyyMMdd_HHmmss_fff}.log");
            AppendAllTextShared(fallback, text);
            return fallback;
        }
    }

    private static void AppendAllTextShared(string path, string text)
    {
        using var stream = new FileStream(path, FileMode.Append, FileAccess.Write, FileShare.ReadWrite);
        using var writer = new StreamWriter(stream);
        writer.Write(text);
    }
}
