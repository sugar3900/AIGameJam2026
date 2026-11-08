using System.Runtime.InteropServices;
using Avalonia;

namespace StoryWriter;

static class Program
{
	[STAThread]
	public static int Main(string[] args)
	{
		if (args.Length > 0 && args[0] == "--selftest") return SelfTest.Run(args.Length > 1 ? args[1] : null);
		WaitForDisplayOnMac();
		return BuildAvaloniaApp().StartWithClassicDesktopLifetime(args);
	}

	public static AppBuilder BuildAvaloniaApp() => AppBuilder.Configure<App>().UsePlatformDetect().LogToTrace();

	[DllImport("/System/Library/Frameworks/CoreVideo.framework/CoreVideo")]
	static extern int CVDisplayLinkCreateWithActiveCGDisplays(out IntPtr link);

	[DllImport("/System/Library/Frameworks/CoreVideo.framework/CoreVideo")]
	static extern void CVDisplayLinkRelease(IntPtr link);

	/// <summary>
	/// Avalonia's macOS render timer needs an awake display (CVDisplayLink) at startup and throws
	/// "not able to start the RenderTimer (-6661)" otherwise, e.g. when launched while the screen is asleep.
	/// Wait for a display instead of crashing. See AvaloniaUI/Avalonia#18895.
	/// </summary>
	static void WaitForDisplayOnMac()
	{
		if (!OperatingSystem.IsMacOS()) return;
		for (int attempt = 0; ; attempt++)
		{
			int err;
			try { err = CVDisplayLinkCreateWithActiveCGDisplays(out var link); if (err == 0) CVDisplayLinkRelease(link); }
			catch { return; } // can't probe; let Avalonia try
			if (err == 0) return;
			if (attempt == 0) Console.Error.WriteLine("I Can Fix Him - Story Writer: waiting for a display to wake up…");
			Thread.Sleep(1000);
		}
	}
}
