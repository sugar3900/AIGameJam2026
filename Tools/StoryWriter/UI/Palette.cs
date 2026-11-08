using Avalonia.Media;
using StoryWriter.Model;

namespace StoryWriter.UI;

public static class Palette
{
	static SolidColorBrush B(string hex) => new(Color.Parse(hex));

	public static readonly IBrush Canvas = B("#17141B");
	public static readonly IBrush GridDot = B("#2C2633");
	public static readonly IBrush Panel = B("#211D26");
	public static readonly IBrush PanelAlt = B("#2A2530");
	public static readonly IBrush Card = B("#2E2836");
	public static readonly IBrush CardBorder = B("#463D50");
	public static readonly IBrush Text = B("#EEE7F2");
	public static readonly IBrush Muted = B("#A396AE");
	public static readonly IBrush Faint = B("#6F6479");
	/// <summary>Locked (condition false) choices: readable, but clearly not the live ones.</summary>
	public static readonly IBrush LockedText = B("#D6C9DE");
	public static readonly IBrush LockedFill = B("#3A2F3C");

	public static readonly IBrush Story = B("#6E8FE0");
	public static readonly IBrush Hypertext = B("#FF5FA8");
	public static readonly IBrush Ending = B("#F2C14E");
	public static readonly IBrush Start = B("#5FCF93");
	public static readonly IBrush Condition = B("#E8A33D");
	public static readonly IBrush ConditionFill = B("#3A2C17");
	public static readonly IBrush Error = B("#FF5D5D");
	public static readonly IBrush Warn = B("#E8C33D");
	public static readonly IBrush Selection = B("#FFFFFF");
	public static readonly IBrush PreviewHere = B("#5FCF93");

	public static readonly IBrush EdgeGoto = B("#7C7088");
	public static readonly IBrush EdgeChoice = B("#B3A7C0");
	public static readonly IBrush EdgeTopic = B("#FF5FA8");
	public static readonly IBrush EdgeEntry = B("#5FCF93");

	public static readonly IBrush Him = B("#EEE7F2");
	public static readonly IBrush You = B("#7FD1FF");
	public static readonly IBrush Narration = B("#B9A8C9");
	public static readonly IBrush Substitution = B("#66D9C2");

	public static readonly IBrush Romance = B("#FF5FA8");
	public static readonly IBrush Friendship = B("#5FCF93");
	public static readonly IBrush Friction = B("#FF8A3D");

	public static IBrush ForSpeaker(Speaker s) => s switch { Speaker.You => You, Speaker.Narration => Narration, _ => Him };
	public static IBrush ForKind(NodeKind k) => k switch { NodeKind.Hypertext => Hypertext, NodeKind.Ending => Ending, _ => Story };

	public static IBrush ForStat(string key)
	{
		var k = key.ToLowerInvariant();
		if (k.EndsWith("romance")) return Romance;
		if (k.EndsWith("friendship")) return Friendship;
		if (k.EndsWith("friction")) return Friction;
		return Condition;
	}
}
