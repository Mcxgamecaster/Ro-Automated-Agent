using System.Windows;
using System.Windows.Controls;

namespace HumankindApp.Pages;

public partial class CalibrationPage : Page
{
    public CalibrationPage()
    {
        InitializeComponent();
        DataContext = ((App)Application.Current).ViewModel;
    }
}
