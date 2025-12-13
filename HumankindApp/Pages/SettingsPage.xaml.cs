using System.Windows;
using System.Windows.Controls;

namespace HumankindApp.Pages;

public partial class SettingsPage : Page
{
    public SettingsPage()
    {
        InitializeComponent();
        var vm = ((App)Application.Current).ViewModel;
        DataContext = vm;
        ApiKeyBox.Password = vm.GeminiApiKey;
    }

    private void ApiKeyBox_OnPasswordChanged(object sender, RoutedEventArgs e)
    {
        var vm = ((App)Application.Current).ViewModel;
        vm.GeminiApiKey = ApiKeyBox.Password;
    }
}
