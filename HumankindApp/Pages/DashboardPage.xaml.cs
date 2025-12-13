using System.Windows;
using System.Windows.Controls;
using HumankindApp.ViewModels;

namespace HumankindApp.Pages;

public partial class DashboardPage : Page
{
    public DashboardPage()
    {
        InitializeComponent();
        DataContext = ((App)Application.Current).ViewModel;
    }
}
