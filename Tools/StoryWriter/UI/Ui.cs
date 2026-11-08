using Avalonia;
using Avalonia.Controls;
using Avalonia.Controls.Primitives;
using Avalonia.Input;
using Avalonia.Layout;
using Avalonia.Media;

namespace StoryWriter.UI;

/// <summary>Small helpers for building UI in code.</summary>
public static class Ui
{
	public static Button Btn(string text, Action onClick, string? tip = null, bool accent = false)
	{
		var b = new Button { Content = text, Padding = new Thickness(10, 4), VerticalAlignment = VerticalAlignment.Center };
		if (accent) b.Classes.Add("accent");
		b.Click += (_, _) => onClick();
		if (tip != null) ToolTip.SetTip(b, tip);
		return b;
	}

	public static TextBlock Label(string text, double size = 13, IBrush? color = null, FontWeight weight = FontWeight.Normal) => new()
	{
		Text = text,
		FontSize = size,
		Foreground = color ?? Palette.Text,
		FontWeight = weight,
		VerticalAlignment = VerticalAlignment.Center,
		TextWrapping = TextWrapping.Wrap,
	};

	public static TextBlock Caption(string text) => Label(text, 11, Palette.Muted, FontWeight.SemiBold);

	public static StackPanel Row(double spacing, params Control[] children)
	{
		var p = new StackPanel { Orientation = Orientation.Horizontal, Spacing = spacing };
		foreach (var c in children) p.Children.Add(c);
		return p;
	}

	public static StackPanel Col(double spacing, params Control[] children)
	{
		var p = new StackPanel { Orientation = Orientation.Vertical, Spacing = spacing };
		foreach (var c in children) p.Children.Add(c);
		return p;
	}

	public static Border Chip(string text, IBrush color) => new()
	{
		Background = new SolidColorBrush(((ISolidColorBrush)color).Color, 0.18),
		BorderBrush = color,
		BorderThickness = new Thickness(1),
		CornerRadius = new CornerRadius(8),
		Padding = new Thickness(6, 1),
		Margin = new Thickness(0, 0, 4, 0),
		VerticalAlignment = VerticalAlignment.Center,
		Child = new TextBlock { Text = text, FontSize = 11, Foreground = color },
	};

	public static Control Field(string caption, Control input, string? tip = null)
	{
		var c = Col(2, Caption(caption), input);
		if (tip != null) ToolTip.SetTip(c, tip);
		return c;
	}

	public static bool IsCommand(KeyModifiers m) => m.HasFlag(KeyModifiers.Meta) || m.HasFlag(KeyModifiers.Control);

	// ------------------------------------------------------------ Dialogs

	static Window DialogShell(string title, Control body, double width = 420) => new()
	{
		Title = title,
		Width = width,
		SizeToContent = SizeToContent.Height,
		CanResize = false,
		WindowStartupLocation = WindowStartupLocation.CenterOwner,
		Background = Palette.Panel,
		Content = new Border { Padding = new Thickness(18), Child = body },
	};

	/// <summary>Returns the index of the clicked button (or -1 if the window was closed).</summary>
	public static async Task<int> Ask(Window owner, string title, string message, params string[] buttons)
	{
		int result = -1;
		Window? w = null;
		var row = new StackPanel { Orientation = Orientation.Horizontal, Spacing = 8, HorizontalAlignment = HorizontalAlignment.Right };
		for (int i = 0; i < buttons.Length; i++)
		{
			int idx = i;
			row.Children.Add(Btn(buttons[i], () => { result = idx; w!.Close(); }, accent: i == 0));
		}
		w = DialogShell(title, Col(16, Label(message, 13), row));
		await w.ShowDialog(owner);
		return result;
	}

	public static async Task<string?> Prompt(Window owner, string title, string message, string initial = "", Func<string, string?>? validate = null)
	{
		string? result = null;
		Window? w = null;
		var box = new TextBox { Text = initial };
		var err = Label("", 12, Palette.Error);
		void Ok()
		{
			var v = box.Text?.Trim() ?? "";
			var e = validate?.Invoke(v);
			if (e != null) { err.Text = e; return; }
			result = v;
			w!.Close();
		}
		box.KeyDown += (_, e) =>
		{
			if (e.Key == Key.Enter) { Ok(); e.Handled = true; }
			if (e.Key == Key.Escape) w!.Close();
		};
		var row = Row(8, Btn("OK", Ok, accent: true), Btn("Cancel", () => w!.Close()));
		row.HorizontalAlignment = HorizontalAlignment.Right;
		w = DialogShell(title, Col(10, Label(message), box, err, row));
		w.Opened += (_, _) => { box.Focus(); box.SelectAll(); };
		await w.ShowDialog(owner);
		return result;
	}

	/// <summary>Guided condition dialog. Returns null if cancelled, "" for "no condition".</summary>
	public static async Task<string?> EditCondition(Window owner, string title, string message, IEnumerable<string> vars, string? initial)
	{
		string? result = null;
		Window? w = null;
		var editor = new ConditionEditor(vars, initial);
		var err = Label("", 12, Palette.Error);
		void Ok()
		{
			if (editor.Error is { } e) { err.Text = e; return; }
			result = editor.Value;
			w!.Close();
		}
		var row = Row(8, Btn("OK", Ok, accent: true), Btn("Cancel", () => w!.Close()));
		row.HorizontalAlignment = HorizontalAlignment.Right;
		w = DialogShell(title, Col(10, Label(message), editor, err, row), 560);
		await w.ShowDialog(owner);
		return result;
	}
}
