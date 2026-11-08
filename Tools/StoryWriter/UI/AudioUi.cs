using Avalonia;
using Avalonia.Controls;
using Avalonia.Layout;
using Avalonia.Media;
using StoryWriter.Runtime;

namespace StoryWriter.UI;

/// <summary>Little speaker widgets shared by the preview and the node editor.</summary>
static class AudioUi
{
	/// <summary>A "♪ ▶" button that plays the clip and turns into "♪ ■" (stop) while that clip is playing.</summary>
	public static Button ClipButton(string clipPath, string? tip = null)
	{
		var b = new Button
		{
			Padding = new Thickness(6, 1),
			MinHeight = 0,
			FontSize = 11,
			VerticalAlignment = VerticalAlignment.Center,
		};
		ToolTip.SetTip(b, tip ?? AudioLibrary.DescribeClip(clipPath));
		void Refresh()
		{
			bool playing = AudioService.CurrentVoice == clipPath;
			b.Content = playing ? "♪ ■" : "♪ ▶";
			b.Foreground = playing ? Palette.Friendship : Palette.Muted;
		}
		b.Click += (_, _) =>
		{
			if (AudioService.CurrentVoice == clipPath) AudioService.StopVoice();
			else AudioService.PlayVoice(clipPath);
		};
		if (!AudioService.Available)
		{
			b.IsEnabled = false;
			ToolTip.SetTip(b, AudioService.UnavailableReason);
			ToolTip.SetShowOnDisabled(b, true);
		}
		Action changed = Refresh;
		b.AttachedToVisualTree += (_, _) => { AudioService.VoiceChanged += changed; Refresh(); };
		b.DetachedFromVisualTree += (_, _) => AudioService.VoiceChanged -= changed;
		Refresh();
		return b;
	}

	/// <summary>Shown on spoken lines that have no recording yet.</summary>
	public static Control NoClip(string key) => new TextBlock
	{
		Text = "♪ no clip",
		FontSize = 11,
		Foreground = Palette.Faint,
		VerticalAlignment = VerticalAlignment.Center,
		Cursor = new Avalonia.Input.Cursor(Avalonia.Input.StandardCursorType.Arrow),
		[ToolTip.TipProperty] = $"No voice clip ({key}.wav). Run Tools/Audio/generate_vo.py after saving; clips are matched by node and line position.",
	};
}
