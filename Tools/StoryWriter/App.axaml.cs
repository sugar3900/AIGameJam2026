using Avalonia;
using Avalonia.Controls.ApplicationLifetimes;
using Avalonia.Markup.Xaml;
using StoryWriter.UI;

namespace StoryWriter;

public partial class App : Application
{
	public override void Initialize() => AvaloniaXamlLoader.Load(this);

	public override void OnFrameworkInitializationCompleted()
	{
		if (ApplicationLifetime is IClassicDesktopStyleApplicationLifetime d)
		{
			var folder = d.Args?.FirstOrDefault(a => !a.StartsWith("--"));
			d.MainWindow = new MainWindow(folder);
		}
		base.OnFrameworkInitializationCompleted();
	}
}
