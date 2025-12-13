using System.Windows;
using System.Windows.Controls;

namespace HumankindApp.Pages;

public partial class RunPage : Page
{
    public RunPage()
    {
        InitializeComponent();
        DataContext = ((App)Application.Current).ViewModel;
    }
}
