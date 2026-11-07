using Avalonia;
using Avalonia.Controls.ApplicationLifetimes;
using Avalonia.Markup.Xaml;
using Avalonia.Threading;
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
			var main = new MainWindow(folder);
			d.MainWindow = main;

			// An editor shouldn't take unsaved work down with it: report UI errors instead of quitting.
			bool showing = false;
			Dispatcher.UIThread.UnhandledException += (_, e) =>
			{
				e.Handled = true;
				LogError(e.Exception);
				if (showing) return;
				showing = true;
				Dispatcher.UIThread.Post(async () =>
				{
					await Ui.Ask(main, "Something went wrong",
						$"{e.Exception.GetType().Name}: {e.Exception.Message}\n\nYour work is still open; save it if you can. Details were written to {LogPath}.", "OK");
					showing = false;
				});
			};
		}
		base.OnFrameworkInitializationCompleted();
	}

	static string LogPath => Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.ApplicationData), "StoryWriter", "errors.log");

	static void LogError(Exception ex)
	{
		try
		{
			Directory.CreateDirectory(Path.GetDirectoryName(LogPath)!);
			File.AppendAllText(LogPath, $"[{DateTime.Now:u}] {ex}\n\n");
		}
		catch
		{
			// Nowhere else to report it.
		}
	}
}
