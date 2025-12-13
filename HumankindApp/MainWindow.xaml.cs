using System;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Input;
using System.Windows.Media.Animation;
using System.Windows.Navigation;
using HumankindApp.Pages;

namespace HumankindApp;

public partial class MainWindow : Window
{
    private string? _currentPageTag;

    public MainWindow()
    {
        InitializeComponent();
        DataContext = ((App)Application.Current).ViewModel;
        Loaded += OnLoaded;
    }

    private void OnLoaded(object sender, RoutedEventArgs e)
    {
        Loaded -= OnLoaded;
        _currentPageTag = "Dashboard";
        MainFrame.Navigate(new DashboardPage());
        LogActivity("Application started");
    }

    private void TitleBar_MouseLeftButtonDown(object sender, MouseButtonEventArgs e)
    {
        if (e.ClickCount == 2)
        {
            MaximizeButton_Click(sender, e);
        }
        else
        {
            try
            {
                DragMove();
            }
            catch
            {
            }
        }
    }

    private void MinimizeButton_Click(object sender, RoutedEventArgs e)
    {
        WindowState = WindowState.Minimized;
    }

    private void MaximizeButton_Click(object sender, RoutedEventArgs e)
    {
        WindowState = WindowState == WindowState.Maximized ? WindowState.Normal : WindowState.Maximized;
    }

    private void CloseButton_Click(object sender, RoutedEventArgs e)
    {
        Close();
    }

    private void NavButton_Checked(object sender, RoutedEventArgs e)
    {
        if (sender is not RadioButton rb || rb.Tag is not string tag || MainFrame == null)
            return;

        if (_currentPageTag == tag)
            return;

        _currentPageTag = tag;
        
        Page? page = tag switch
        {
            "Dashboard" => new DashboardPage(),
            "Calibration" => new CalibrationPage(),
            "Run" => new RunPage(),
            "Settings" => new SettingsPage(),
            _ => null
        };

        if (page != null)
        {
            MainFrame.Navigate(page);
            LogActivity($"Navigated to {tag}");
        }
    }

    public void LogActivity(string message)
    {
        if (ActivityLog != null)
        {
            var timestamp = DateTime.Now.ToString("HH:mm:ss");
            var line = $"[{timestamp}] {message}\n";
            ActivityLog.Text += line;
        }
    }

    public void SetStatus(string text, bool isOnline = false)
    {
        if (StatusText != null)
        {
            StatusText.Text = text;
        }
    }

    private void MainFrame_Navigated(object sender, NavigationEventArgs e)
    {
        if (sender is Frame frame && frame.Content is FrameworkElement content)
        {
            content.Opacity = 0;
            var fadeIn = new DoubleAnimation
            {
                From = 0,
                To = 1,
                Duration = TimeSpan.FromMilliseconds(250),
                EasingFunction = new CubicEase { EasingMode = EasingMode.EaseOut }
            };
            content.BeginAnimation(OpacityProperty, fadeIn);
        }
    }

    private void ContentArea_MouseMove(object sender, MouseEventArgs e)
    {
        var pos = e.GetPosition(ContentArea);
        
        // Update mouse glow position using Canvas positioning (centered on cursor)
        Canvas.SetLeft(MouseGlow, pos.X - MouseGlow.Width / 2);
        Canvas.SetTop(MouseGlow, pos.Y - MouseGlow.Height / 2);
        
        // Fade in glow smoothly
        if (MouseGlow.Opacity < 0.5)
        {
            var fadeIn = new DoubleAnimation
            {
                To = 0.5,
                Duration = TimeSpan.FromMilliseconds(150),
                EasingFunction = new CubicEase { EasingMode = EasingMode.EaseOut }
            };
            MouseGlow.BeginAnimation(OpacityProperty, fadeIn);
        }
    }

    private void ContentArea_MouseLeave(object sender, MouseEventArgs e)
    {
        // Fade out the glow when mouse leaves
        var fadeOut = new DoubleAnimation
        {
            To = 0,
            Duration = TimeSpan.FromMilliseconds(400),
            EasingFunction = new CubicEase { EasingMode = EasingMode.EaseOut }
        };
        MouseGlow.BeginAnimation(OpacityProperty, fadeOut);
    }
}
