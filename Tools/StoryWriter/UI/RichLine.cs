using Avalonia.Controls;
using Avalonia.Controls.Documents;
using Avalonia.Input;
using Avalonia.Media;
using StoryWriter.Model;

namespace StoryWriter.UI;

/// <summary>Renders a dialogue line like the game: [topic] words become highlighted, clickable links.</summary>
public static class RichLine
{
	public sealed class TopicSpan
	{
		public int Start, Length;
		public string TopicId = "";
		public bool Active;
	}

	/// <param name="onTopic">Null for history lines (not clickable).</param>
	public static TextBlock Build(string text, Speaker speaker, ISet<string>? activeTopics, Action<string>? onTopic, double size = 15, bool substituteHints = false)
	{
		var tb = new TextBlock
		{
			TextWrapping = TextWrapping.Wrap,
			FontSize = size,
			Foreground = Palette.ForSpeaker(speaker),
			FontStyle = speaker == Speaker.Narration ? FontStyle.Italic : FontStyle.Normal,
			Inlines = new InlineCollection(),
		};
		var spans = new List<TopicSpan>();
		int pos = 0, plain = 0;
		foreach (var t in Dialogue.Topics(text))
		{
			if (t.Start > pos) plain += AddPlain(tb, text[pos..t.Start], substituteHints);
			bool active = activeTopics == null || activeTopics.Contains(t.TopicId);
			tb.Inlines!.Add(new Run(t.Shown)
			{
				Foreground = active ? Palette.Hypertext : Palette.Faint,
				FontWeight = FontWeight.Bold,
				TextDecorations = active && onTopic != null ? TextDecorations.Underline : null,
			});
			spans.Add(new TopicSpan { Start = plain, Length = t.Shown.Length, TopicId = t.TopicId, Active = active });
			plain += t.Shown.Length;
			pos = t.Start + t.Length;
		}
		if (pos < text.Length) AddPlain(tb, text[pos..], substituteHints);

		if (onTopic != null && spans.Count > 0)
		{
			TopicSpan? Hit(PointerEventArgs e)
			{
				// Test against the rectangles the link's characters occupy rather than a caret position, which
				// lands one past the last character when the pointer is on its right half.
				var pt = e.GetPosition(tb);
				foreach (var s in spans)
					if (s.Active && tb.TextLayout.HitTestTextRange(s.Start, s.Length).Any(rc => rc.Inflate(1).Contains(pt))) return s;
				return null;
			}
			tb.PointerMoved += (_, e) => tb.Cursor = Hit(e) != null ? new Cursor(StandardCursorType.Hand) : Cursor.Default;
			tb.PointerPressed += (_, e) =>
			{
				if (Hit(e) is { } s)
				{
					e.Handled = true;
					onTopic(s.TopicId);
				}
			};
			ToolTip.SetTip(tb, "Click a pink word to ask about it");
		}
		return tb;
	}

	static int AddPlain(TextBlock tb, string s, bool substituteHints)
	{
		if (!substituteHints)
		{
			tb.Inlines!.Add(new Run(s));
			return s.Length;
		}
		// Editor preview: show {player}/{name} tokens in teal instead of substituting.
		int i = 0;
		while (i < s.Length)
		{
			int a = s.IndexOf('{', i);
			int b = a >= 0 ? s.IndexOf('}', a) : -1;
			if (a < 0 || b < 0)
			{
				tb.Inlines!.Add(new Run(s[i..]));
				break;
			}
			if (a > i) tb.Inlines!.Add(new Run(s[i..a]));
			tb.Inlines!.Add(new Run(s[a..(b + 1)]) { Foreground = Palette.Substitution });
			i = b + 1;
		}
		return s.Length;
	}
}
