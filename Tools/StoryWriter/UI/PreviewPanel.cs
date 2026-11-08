using Avalonia;
using Avalonia.Controls;
using Avalonia.Input;
using Avalonia.Layout;
using Avalonia.Media;
using Avalonia.Threading;
using StoryWriter.Model;
using StoryWriter.Runtime;

namespace StoryWriter.UI;

/// <summary>
/// Plays a conversation the way the game does (same rules as FixHimDialogueSubsystem), with a scrolling transcript,
/// clickable [topic] words, choices (locked ones shown with their condition), fx and ending cards.
/// </summary>
public sealed class PreviewPanel : Grid
{
	readonly Func<string, DialogueDocument?> _find;
	public DialogueRunner Runner { get; }
	public PreviewState State { get; }

	readonly TextBlock _title = Ui.Label("Preview", 16, Palette.Text, FontWeight.Bold);
	readonly TextBlock _subtitle = Ui.Label("", 12, Palette.Muted);
	readonly TextBlock _where = Ui.Label("", 11, Palette.Faint);
	readonly StackPanel _meters = new() { Orientation = Orientation.Horizontal, Spacing = 14 };
	readonly StackPanel _transcript = new() { Spacing = 10, Margin = new Thickness(14, 10, 14, 14) };
	readonly ScrollViewer _scroll;
	readonly StackPanel _choices = new() { Spacing = 6 };
	readonly Button _continue;
	readonly StackPanel _endActions = new() { Orientation = Orientation.Horizontal, Spacing = 8 };
	readonly Border _overlay = new() { IsVisible = false, Background = new SolidColorBrush(Colors.Black, 0.92) };

	// Audio: the character's loop plays while previewing; the dropdown auditions the other tracks (menu, explore, finale).
	readonly CheckBox _voiceToggle = new() { Content = "Voice", IsChecked = true, FontSize = 12 };
	readonly CheckBox _musicToggle = new() { Content = "Music", IsChecked = true, FontSize = 12 };
	readonly TextBlock _track = Ui.Label("no music", 11, Palette.Muted);
	readonly ComboBox _auditionBox = new() { FontSize = 11, MinHeight = 0, Padding = new Thickness(6, 1), MinWidth = 120 };
	const string CharacterMusic = "(character music)";
	readonly Dictionary<string, MusicTrack> _auditionTracks = new();
	List<MusicTrack> _tracks = new();
	MusicTrack? _audition;
	bool _fillingTracks;

	string? _hunkId;
	string? _startNode;
	PreviewState? _snapshot;
	Control? _liveLine;

	public event Action<string, string>? NodeEntered;
	public event Action<string, string>? ConversationEnded;
	public event Action? ConversationStarted;
	/// <summary>Raised when the transcript's node marker is clicked.</summary>
	public event Action<string, string>? NodeLinkClicked;

	public string? HunkId => _hunkId;
	public bool IsPlaying => Runner.IsActive;

	public PreviewPanel(Func<string, DialogueDocument?> find, PreviewState state)
	{
		_find = find;
		State = state;
		Runner = new DialogueRunner(state, find);
		Focusable = true;
		Background = Palette.Panel;

		RowDefinitions = new RowDefinitions("Auto,*,Auto");
		var header = new Border
		{
			Background = Palette.PanelAlt,
			Padding = new Thickness(14, 10),
			Child = Ui.Col(4, _title, _subtitle, _meters, _where, BuildAudioBar()),
		};
		Children.Add(header);

		_scroll = new ScrollViewer { Content = _transcript, HorizontalScrollBarVisibility = Avalonia.Controls.Primitives.ScrollBarVisibility.Disabled };
		ScrollViewer.SetAllowAutoHide(_scroll, false);
		_scroll.VerticalScrollBarVisibility = Avalonia.Controls.Primitives.ScrollBarVisibility.Visible;
		SetRow(_scroll, 1);
		Children.Add(_scroll);

		_continue = Ui.Btn("Continue ▸", () => Runner.Advance(), "Space / Enter", accent: true);
		_continue.HorizontalAlignment = HorizontalAlignment.Right;
		var footer = new Border
		{
			Background = Palette.PanelAlt,
			Padding = new Thickness(14, 10),
			Child = Ui.Col(8, _choices, _continue, _endActions),
		};
		SetRow(footer, 2);
		Children.Add(footer);

		SetRowSpan(_overlay, 3);
		Children.Add(_overlay);

		Runner.ViewChanged += OnView;
		Runner.NodeEntered += (h, n) =>
		{
			AddNodeMarker(h, n);
			NodeEntered?.Invoke(h, n);
		};
		Runner.EffectsApplied += (_, fx) => AddEffects(fx);
		Runner.Warning += (_, n, msg) => AddNote("⚠ " + msg, Palette.Error);
		Runner.Ended += OnEnded;
		State.Changed += UpdateMeters;
		AudioService.Changed += SyncAudioToggles;
		AudioService.MusicChanged += () => Dispatcher.UIThread.Post(UpdateTrackLabel);
		DetachedFromVisualTree += (_, _) => StopAudio();
	}

	// ------------------------------------------------------------ Audio

	Control BuildAudioBar()
	{
		_voiceToggle.IsCheckedChanged += (_, _) => AudioService.VoiceEnabled = _voiceToggle.IsChecked == true;
		_musicToggle.IsCheckedChanged += (_, _) =>
		{
			AudioService.MusicEnabled = _musicToggle.IsChecked == true;
			ApplyMusic();
		};
		ToolTip.SetTip(_voiceToggle, "Play the voice-over clip of each spoken line (Art Source/Audio/VO)");
		ToolTip.SetTip(_musicToggle, "Loop the character's background music while previewing (Art Source/Audio/BGM)");
		ToolTip.SetTip(_auditionBox, "Audition a track that isn't tied to a character");
		_auditionBox.SelectionChanged += (_, _) =>
		{
			if (_fillingTracks) return;
			_audition = _auditionBox.SelectedItem is string n && _auditionTracks.TryGetValue(n, out var t) ? t : null;
			if (_audition == null) AudioService.StopMusic(this);
			ApplyMusic();
		};
		_auditionBox.DropDownOpened += (_, _) => RefreshTracks();
		if (!AudioService.Available)
		{
			foreach (var c in new Control[] { _voiceToggle, _musicToggle, _auditionBox })
			{
				c.IsEnabled = false;
				ToolTip.SetTip(c, AudioService.UnavailableReason);
				ToolTip.SetShowOnDisabled(c, true);
			}
			_voiceToggle.IsChecked = _musicToggle.IsChecked = false;
		}
		RefreshTracks();
		var row = new WrapPanel { Margin = new Thickness(0, 2, 0, 0) };
		foreach (var c in new Control[] { _voiceToggle, _musicToggle, _auditionBox, _track })
		{
			c.Margin = new Thickness(0, 0, 10, 0);
			row.Children.Add(c);
		}
		return row;
	}

	void SyncAudioToggles()
	{
		if (AudioService.Available)
		{
			_voiceToggle.IsChecked = AudioService.VoiceEnabled;
			_musicToggle.IsChecked = AudioService.MusicEnabled;
		}
		UpdateTrackLabel();
	}

	void RefreshTracks()
	{
		_tracks = AudioLibrary.ScanMusic(ProjectPaths.MusicDir());
		_fillingTracks = true;
		_auditionTracks.Clear();
		var items = new List<string> { CharacterMusic };
		// Tracks named after a conversation play with it; the rest (MainMenu, Explore, Finale) are offered here.
		foreach (var t in _tracks.Where(t => _find(t.Name.ToLowerInvariant()) == null))
		{
			items.Add(t.Name);
			_auditionTracks[t.Name] = t;
		}
		_auditionBox.ItemsSource = items;
		_auditionBox.SelectedItem = _audition != null && _auditionTracks.ContainsKey(_audition.Name) ? _audition.Name : CharacterMusic;
		_fillingTracks = false;
		if (_tracks.Count == 0 && AudioService.Available)
			ToolTip.SetTip(_auditionBox, "No music found in " + ProjectPaths.MusicRelative);
	}

	/// <summary>Plays the auditioned track, else the loop of the conversation being previewed; stops ours otherwise.</summary>
	void ApplyMusic()
	{
		if (!AudioService.Available || !AudioService.MusicEnabled)
		{
			UpdateTrackLabel();
			return;
		}
		var track = _audition ?? (Runner.IsActive ? AudioLibrary.MatchMusic(_tracks, _hunkId) : null);
		if (track != null) AudioService.PlayMusic(this, track.Path);
		else AudioService.StopMusic(this);
		UpdateTrackLabel();
	}

	void UpdateTrackLabel()
	{
		var path = AudioService.CurrentMusic;
		var playing = path == null ? null : _tracks.FirstOrDefault(t => t.Path == path);
		_track.Text = !AudioService.Available ? "audio unavailable" : playing != null ? "♪ " + playing.Name : _tracks.Count == 0 ? "no music" : "no music for this conversation";
		_track.Foreground = playing != null ? Palette.Friendship : Palette.Muted;
	}

	void StopAudio()
	{
		AudioService.StopVoice();
		AudioService.StopMusic(this);
	}

	/// <summary>Plays the clip for a freshly shown spoken line (if it has one), stopping whatever played before.</summary>
	void PlayLineVoice(DialogueView v)
	{
		AudioService.StopVoice();
		if (!AudioService.VoiceEnabled || !AudioService.Available) return;
		var clip = ClipFor(v);
		if (clip != null) AudioService.PlayVoice(clip);
	}

	static string? ClipFor(DialogueView v)
	{
		if (!AudioLibrary.IsSpoken(v.Speaker)) return null;
		var p = AudioLibrary.VoicePath(ProjectPaths.VoiceDir(), v.HunkId, v.NodeId, v.LineIndex);
		return p != null && File.Exists(p) && AudioLibrary.IsVoiceable(v.Text) ? p : null;
	}

	// ------------------------------------------------------------ Control

	public void Start(string hunkId, string? nodeId = null)
	{
		AudioService.StopVoice();
		_snapshot = State.Clone();
		_hunkId = hunkId;
		_startNode = nodeId;
		_transcript.Children.Clear();
		_endActions.Children.Clear();
		_overlay.IsVisible = false;
		var doc = _find(hunkId);
		_title.Text = doc?.Name ?? hunkId;
		_subtitle.Text = doc == null ? "" : string.Join(" · ", new[] { Dialogue.Str(doc.Root["malady"]), Dialogue.Str(doc.Root["room"]) }.Where(x => !string.IsNullOrWhiteSpace(x)));
		_subtitle.IsVisible = _subtitle.Text.Length > 0;
		var visits = State.Hunk(hunkId).Visits;
		AddNote(nodeId == null ? $"Visit {visits + 1} — starting from entries" : $"Starting at node '{nodeId}' (visit {visits + 1})", Palette.Faint);
		ConversationStarted?.Invoke();
		if (!Runner.Start(hunkId, nodeId))
		{
			AddNote(nodeId == null ? "No entry condition matched the current state." : $"Node '{nodeId}' not found.", Palette.Error);
			ShowIdle(null);
		}
		UpdateMeters();
		RefreshTracks();
		ApplyMusic();
		Focus();
	}

	/// <summary>Restore the state from before this run and play it again.</summary>
	public void Restart()
	{
		if (_hunkId == null) return;
		if (_snapshot != null) State.CopyFrom(_snapshot);
		Start(_hunkId, _startNode);
	}

	public void Stop()
	{
		Runner.Abort();
		AudioService.StopVoice();
		if (_audition == null) AudioService.StopMusic(this);
		UpdateTrackLabel();
		ShowIdle("Preview stopped.");
	}

	/// <summary>Buttons shown once the conversation is over (supplied by the host).</summary>
	public void SetEndActions(params Control[] actions)
	{
		_endActions.Children.Clear();
		foreach (var a in actions) _endActions.Children.Add(a);
	}

	void ShowIdle(string? message)
	{
		_choices.Children.Clear();
		_continue.IsVisible = false;
		_where.Text = "";
		if (message != null) AddNote(message, Palette.Muted);
	}

	// ------------------------------------------------------------ View

	void OnView(DialogueView v)
	{
		_where.Text = $"node {v.NodeId} · line {v.LineIndex + 1}/{v.LineCount}{(v.InTangent ? " · link" : "")}";
		// Coming back from a hypertext link (or a refresh) re-presents the node's options without printing its text again.
		if (!v.IsReturn)
		{
			if (_liveLine != null) _liveLine.Opacity = 0.75;
			var speakerName = v.Speaker switch { Speaker.You => State.PlayerName, Speaker.Narration => "", _ => v.HunkName };
			var text = RichLine.Build(v.Text, v.Speaker, v.ActiveTopics, t => Runner.ClickTopic(t));
			var clip = ClipFor(v);
			Control body = text;
			if (speakerName.Length > 0)
			{
				var head = new Grid { ColumnDefinitions = new ColumnDefinitions("*,Auto") };
				head.Children.Add(Ui.Caption(speakerName.ToUpperInvariant()));
				if (clip != null)
				{
					var btn = AudioUi.ClipButton(clip);
					Grid.SetColumn(btn, 1);
					head.Children.Add(btn);
				}
				body = Ui.Col(2, head, text);
			}
			var card = new Border
			{
				Background = v.Speaker == Speaker.Narration ? null : Palette.Card,
				CornerRadius = new CornerRadius(8),
				Padding = new Thickness(12, 8),
				Margin = v.Speaker == Speaker.You ? new Thickness(40, 0, 0, 0) : new Thickness(0, 0, 20, 0),
				Child = body,
			};
			_transcript.Children.Add(card);
			_liveLine = card;
			PlayLineVoice(v);
		}
		else AudioService.StopVoice();

		if (v.Fx == "hearts") ShowHearts();
		else if (v.Fx == "fade") ShowFade(v.FxText);

		_choices.Children.Clear();
		int n = 0;
		foreach (var c in v.Choices)
		{
			var label = c.Visible ? $"{++n}.  {c.Text}" : $"⊘  {c.Text}";
			var content = new StackPanel { Spacing = 3 };
			content.Children.Add(new TextBlock { Text = label, TextWrapping = TextWrapping.Wrap, FontSize = 13.5, Foreground = c.Visible ? Palette.Text : Palette.LockedText });
			var chips = new WrapPanel();
			if (!c.Visible) chips.Children.Add(Ui.Chip("if " + c.Condition, Palette.Error));
			else if (!Dialogue.IsTrivialCondition(c.Condition)) chips.Children.Add(Ui.Chip("if " + c.Condition, Palette.Condition));
			if (c.Effects != null)
				foreach (var (k, val) in c.Effects)
					chips.Children.Add(Ui.Chip($"{k} {(Dialogue.Num(val) >= 0 ? "+" : "")}{Dialogue.Num(val)}", Palette.ForStat(k)));
			if (chips.Children.Count > 0) content.Children.Add(chips);
			var b = new Button
			{
				Content = content,
				HorizontalAlignment = HorizontalAlignment.Stretch,
				HorizontalContentAlignment = HorizontalAlignment.Left,
				Padding = new Thickness(10, 6),
			};
			if (!c.Visible)
			{
				// Locked: shown, grayed out and not clickable.
				b.Background = Palette.LockedFill;
				b.IsEnabled = false;
				b.Opacity = 0.7;
				ToolTip.SetTip(b, "Locked: the condition is false right now.");
				ToolTip.SetShowOnDisabled(b, true);
			}
			var choice = c;
			b.Click += (_, _) => Pick(choice);
			_choices.Children.Add(b);
		}
		bool waitingOnChoice = v.VisibleChoices.Any();
		_continue.IsVisible = !waitingOnChoice;
		_continue.Content = v.WillEnd ? "End conversation ■" : v.IsLastLine ? (v.InTangent ? "Back ▸" : "Continue ▸ (next node)") : "Continue ▸";
		ScrollToEnd();
		if (!IsKeyboardFocusWithin) Focus();
	}

	void Pick(ChoiceView c)
	{
		AudioService.StopVoice();
		AddPick(c.Text, !c.Visible);
		Runner.ChooseRaw(c.Index);
	}

	void OnEnded(string hunk, string ending)
	{
		_choices.Children.Clear();
		_continue.IsVisible = false;
		_where.Text = "";
		AudioService.StopVoice();
		if (_audition == null) AudioService.StopMusic(this);
		UpdateTrackLabel();
		var p = State.Hunk(hunk);
		AddNote($"— Conversation over · visits = {p.Visits}{(p.Fixed ? " · fixed" : "")} —", Palette.Muted);
		if (!string.IsNullOrEmpty(ending)) ShowEndingCard(hunk, ending);
		ConversationEnded?.Invoke(hunk, ending);
		ScrollToEnd();
		// The choice button that was just clicked is gone; take the keyboard back so Enter / Space reach the end actions.
		Dispatcher.UIThread.Post(() => Focus(), DispatcherPriority.Background);
	}

	// ------------------------------------------------------------ Transcript pieces

	void AddNodeMarker(string hunk, string node)
	{
		var t = new TextBlock
		{
			Text = "◇ " + node,
			FontSize = 10.5,
			Foreground = Palette.Faint,
			Cursor = new Cursor(StandardCursorType.Hand),
		};
		ToolTip.SetTip(t, "Show in graph");
		t.PointerPressed += (_, _) => NodeLinkClicked?.Invoke(hunk, node);
		_transcript.Children.Add(t);
	}

	void AddPick(string text, bool forced)
	{
		_transcript.Children.Add(new Border
		{
			Margin = new Thickness(40, 0, 0, 0),
			Child = new TextBlock
			{
				Text = (forced ? "⊘ (forced) " : "→ ") + text,
				FontSize = 13.5,
				FontWeight = FontWeight.SemiBold,
				Foreground = Palette.You,
				TextWrapping = TextWrapping.Wrap,
			},
		});
	}

	void AddEffects(List<string> fx)
	{
		var w = new WrapPanel();
		foreach (var f in fx) w.Children.Add(Ui.Chip(f, Palette.ForStat(f.Split(' ')[0])));
		_transcript.Children.Add(w);
	}

	void AddNote(string text, IBrush color) =>
		_transcript.Children.Add(new TextBlock { Text = text, FontSize = 12, Foreground = color, TextWrapping = TextWrapping.Wrap, HorizontalAlignment = HorizontalAlignment.Center });

	void ScrollToEnd() => Dispatcher.UIThread.Post(() => _scroll.ScrollToEnd(), DispatcherPriority.Background);

	void UpdateMeters()
	{
		_meters.Children.Clear();
		if (_hunkId == null) return;
		var p = State.Hunk(_hunkId);
		Control Meter(string name, int v, IBrush color) => Ui.Row(5,
			Ui.Label(name, 11, Palette.Muted),
			new ProgressBar { Minimum = 0, Maximum = 10, Value = Math.Clamp(v, 0, 10), Width = 60, Height = 6, MinWidth = 40, Foreground = color },
			Ui.Label(v.ToString(), 12, color, FontWeight.Bold));
		_meters.Children.Add(Meter("♥\uFE0E", p.Romance, Palette.Romance));
		_meters.Children.Add(Meter("☺", p.Friendship, Palette.Friendship));
		_meters.Children.Add(Meter("ϟ", p.Friction, Palette.Friction));
		_meters.Children.Add(Ui.Label($"visits {p.Visits}", 11, Palette.Muted));
	}

	// ------------------------------------------------------------ Overlays

	void ShowHearts()
	{
		var hearts = new TextBlock
		{
			Text = "♥\uFE0E  ♥\uFE0E  ♥\uFE0E",
			FontSize = 54,
			Foreground = Palette.Romance,
			HorizontalAlignment = HorizontalAlignment.Center,
			VerticalAlignment = VerticalAlignment.Center,
		};
		_overlay.Background = new SolidColorBrush(Color.Parse("#40FF5FA8"));
		_overlay.Child = hearts;
		_overlay.IsVisible = true;
		_overlay.IsHitTestVisible = false;
		var timer = new DispatcherTimer { Interval = TimeSpan.FromMilliseconds(40) };
		int tick = 0;
		timer.Tick += (_, _) =>
		{
			tick++;
			hearts.Opacity = 1 - tick / 30.0;
			hearts.Margin = new Thickness(0, 0, 0, tick * 3);
			if (tick >= 30)
			{
				timer.Stop();
				if (_overlay.Child == hearts) _overlay.IsVisible = false;
			}
		};
		timer.Start();
	}

	void ShowFade(string text)
	{
		_overlay.Background = new SolidColorBrush(Colors.Black, 0.95);
		_overlay.IsHitTestVisible = true;
		_overlay.Child = Ui.Col(18,
			new TextBlock { Text = string.IsNullOrEmpty(text) ? "…" : text, FontSize = 18, FontStyle = FontStyle.Italic, Foreground = Palette.Text, TextWrapping = TextWrapping.Wrap, TextAlignment = TextAlignment.Center, MaxWidth = 380 },
			new TextBlock { Text = "fade to black · click to continue", FontSize = 11, Foreground = Palette.Faint, HorizontalAlignment = HorizontalAlignment.Center });
		((StackPanel)_overlay.Child).VerticalAlignment = VerticalAlignment.Center;
		((StackPanel)_overlay.Child).HorizontalAlignment = HorizontalAlignment.Center;
		_overlay.IsVisible = true;
		_overlay.PointerPressed -= DismissOverlay;
		_overlay.PointerPressed += DismissOverlay;
	}

	void ShowEndingCard(string hunk, string ending)
	{
		var doc = _find(hunk);
		var card = doc?.EndingCards[ending] as System.Text.Json.Nodes.JsonObject;
		var title = Dialogue.Str(card?["title"]) ?? "";
		var text = Dialogue.Str(card?["text"]) ?? "(no ending card)";
		var label = ending.Replace('_', ' ').ToUpperInvariant();
		_overlay.Background = new SolidColorBrush(Color.Parse("#F01A1420"));
		_overlay.IsHitTestVisible = true;
		var panel = Ui.Col(12,
			Ui.Label(label, 12, Palette.Ending, FontWeight.Bold),
			Ui.Label(string.IsNullOrEmpty(title) ? "(untitled ending)" : title, 22, Palette.Text, FontWeight.Bold),
			Ui.Label(text, 14, Palette.Muted),
			Ui.Label("click to close", 11, Palette.Faint));
		panel.Margin = new Thickness(30);
		panel.VerticalAlignment = VerticalAlignment.Center;
		panel.MaxWidth = 420;
		_overlay.Child = new Border
		{
			BorderBrush = Palette.Ending,
			BorderThickness = new Thickness(2),
			CornerRadius = new CornerRadius(12),
			Background = Palette.Panel,
			Margin = new Thickness(20),
			VerticalAlignment = VerticalAlignment.Center,
			Child = panel,
		};
		_overlay.IsVisible = true;
		_overlay.PointerPressed -= DismissOverlay;
		_overlay.PointerPressed += DismissOverlay;
	}

	void DismissOverlay(object? sender, PointerPressedEventArgs e)
	{
		_overlay.IsVisible = false;
		Focus();
	}

	protected override void OnKeyDown(KeyEventArgs e)
	{
		base.OnKeyDown(e);
		if (e.Handled || e.Source is TextBox) return;
		if (_overlay.IsVisible && _overlay.IsHitTestVisible && e.Key is Key.Space or Key.Enter or Key.Escape)
		{
			_overlay.IsVisible = false;
			e.Handled = true;
			return;
		}
		if (!Runner.IsActive)
		{
			// Conversation over: Enter / Space press the primary end action ("Next visit", "Continue to …").
			if (e.Key is Key.Space or Key.Enter && _endActions.Children.OfType<Button>().FirstOrDefault(b => b.IsVisible && b.IsEnabled) is { } next)
			{
				next.RaiseEvent(new Avalonia.Interactivity.RoutedEventArgs(Button.ClickEvent));
				e.Handled = true;
			}
			return;
		}
		if (e.Key is Key.Space or Key.Enter or Key.Right)
		{
			Runner.Advance();
			e.Handled = true;
		}
		else if (e.Key >= Key.D1 && e.Key <= Key.D9 && Runner.View is { } v)
		{
			var vis = v.VisibleChoices.ToList();
			int i = e.Key - Key.D1;
			if (i < vis.Count)
			{
				Pick(vis[i]);
				e.Handled = true;
			}
		}
	}
}
