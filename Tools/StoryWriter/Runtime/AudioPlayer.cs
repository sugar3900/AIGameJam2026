using System.Collections.Concurrent;
using System.Diagnostics;
using System.Runtime.InteropServices;
using System.Text;
using Avalonia.Threading;

namespace StoryWriter.Runtime;

/// <summary>One playing sound. <see cref="Stop"/> is safe to call any number of times, from any thread.</summary>
public interface IAudioHandle
{
	void Stop();
}

/// <summary>Plays files without any audio library: each OS gets its own little backend (no NuGet packages).</summary>
public interface IAudioPlayer
{
	/// <summary>"ffplay", "afplay", "winmm (MCI)"…</summary>
	string Name { get; }
	/// <param name="volume">0..1</param>
	/// <param name="finished">Called (from any thread) when a non-looping sound ends by itself; not when it is stopped.</param>
	IAudioHandle Play(string file, bool loop, double volume, Action? finished);
	void StopAll();
}

/// <summary>Linux / macOS: runs a command-line player per sound and kills it on stop. Never leaves a child behind.</summary>
sealed class ProcessAudioPlayer : IAudioPlayer
{
	sealed record Backend(string Exe, Func<string, bool, double, string[]> Args, bool NativeLoop);

	readonly Backend _b;
	readonly ConcurrentDictionary<Handle, byte> _live = new();
	public string Name { get; }

	ProcessAudioPlayer(string exe, Backend b)
	{
		Name = Path.GetFileNameWithoutExtension(exe);
		_b = b with { Exe = exe };
	}

	public static ProcessAudioPlayer? Detect()
	{
		var backends = new Dictionary<string, Backend>
		{
			["ffplay"] = new("ffplay", (f, loop, v) => new[] { "-nodisp", "-autoexit", "-loglevel", "quiet" }
				.Concat(loop ? new[] { "-loop", "0" } : Array.Empty<string>())
				.Concat(new[] { "-volume", ((int)Math.Round(v * 100)).ToString(), f }).ToArray(), true),
			["mpv"] = new("mpv", (f, loop, v) => new[] { "--no-video", "--really-quiet", "--no-terminal" }
				.Concat(loop ? new[] { "--loop=inf" } : Array.Empty<string>())
				.Concat(new[] { $"--volume={(int)Math.Round(v * 100)}", f }).ToArray(), true),
			["paplay"] = new("paplay", (f, _, v) => new[] { $"--volume={(int)Math.Round(v * 65536)}", f }, false),
			["aplay"] = new("aplay", (f, _, _) => new[] { "-q", f }, false),
			["afplay"] = new("afplay", (f, _, v) => new[] { "-v", v.ToString("0.##", System.Globalization.CultureInfo.InvariantCulture), f }, false),
		};
		var order = OperatingSystem.IsMacOS() ? new[] { "afplay", "ffplay", "mpv" } : new[] { "ffplay", "mpv", "paplay", "aplay" };
		foreach (var name in order)
			if (Which(name) is { } exe) return new ProcessAudioPlayer(exe, backends[name]);
		return null;
	}

	static string? Which(string exe)
	{
		var path = Environment.GetEnvironmentVariable("PATH") ?? "";
		var dirs = path.Split(Path.PathSeparator, StringSplitOptions.RemoveEmptyEntries).Concat(new[] { "/usr/bin", "/usr/local/bin", "/opt/homebrew/bin" });
		foreach (var d in dirs)
		{
			var p = Path.Combine(d, exe);
			if (File.Exists(p)) return p;
		}
		return null;
	}

	public IAudioHandle Play(string file, bool loop, double volume, Action? finished)
	{
		var h = new Handle(this, file, loop, volume, finished);
		_live[h] = 0;
		h.Spawn();
		return h;
	}

	public void StopAll()
	{
		foreach (var h in _live.Keys) h.Stop();
	}

	sealed class Handle : IAudioHandle
	{
		readonly ProcessAudioPlayer _owner;
		readonly string _file;
		readonly bool _loop;
		readonly double _volume;
		readonly Action? _finished;
		readonly object _lock = new();
		Process? _proc;
		bool _stopped;

		public Handle(ProcessAudioPlayer owner, string file, bool loop, double volume, Action? finished)
		{
			_owner = owner;
			_file = file;
			_loop = loop;
			_volume = volume;
			_finished = finished;
		}

		public void Spawn()
		{
			lock (_lock)
			{
				if (_stopped) return;
				var psi = new ProcessStartInfo(_owner._b.Exe)
				{
					UseShellExecute = false,
					CreateNoWindow = true,
					RedirectStandardInput = true,
				};
				foreach (var a in _owner._b.Args(_file, _loop && _owner._b.NativeLoop, _volume)) psi.ArgumentList.Add(a);
				var started = DateTime.UtcNow;
				try
				{
					var p = new Process { StartInfo = psi, EnableRaisingEvents = true };
					p.Exited += (_, _) => OnExited(p, started);
					p.Start();
					_proc = p;
				}
				catch (Exception ex) when (ex is System.ComponentModel.Win32Exception or InvalidOperationException)
				{
					_stopped = true;
					_owner._live.TryRemove(this, out _);
					_finished?.Invoke();
				}
			}
		}

		void OnExited(Process p, DateTime started)
		{
			bool again;
			lock (_lock)
			{
				if (_stopped || p != _proc) return;
				// A loop on a player without native looping restarts itself, unless it died at once (broken file or device).
				again = _loop && !_owner._b.NativeLoop && DateTime.UtcNow - started > TimeSpan.FromMilliseconds(400);
				if (!again) _stopped = true;
			}
			p.Dispose();
			if (again) Spawn();
			else
			{
				_owner._live.TryRemove(this, out _);
				_finished?.Invoke();
			}
		}

		public void Stop()
		{
			Process? p;
			lock (_lock)
			{
				if (_stopped && _proc == null) return;
				_stopped = true;
				p = _proc;
				_proc = null;
			}
			_owner._live.TryRemove(this, out _);
			if (p == null) return;
			try
			{
				if (!p.HasExited) p.Kill(entireProcessTree: true);
			}
			catch (Exception ex) when (ex is InvalidOperationException or System.ComponentModel.Win32Exception)
			{
				// Already gone.
			}
			p.Dispose();
		}
	}
}

/// <summary>Windows: winmm MCI, which (unlike System.Media.SoundPlayer) can play music and a voice clip at the same time.</summary>
sealed class MciAudioPlayer : IAudioPlayer
{
	[DllImport("winmm.dll", CharSet = CharSet.Unicode)]
	static extern int mciSendString(string command, StringBuilder? result, int resultLength, IntPtr callback);

	readonly ConcurrentDictionary<Handle, byte> _live = new();
	int _next;
	public string Name => "winmm (MCI)";

	public IAudioHandle Play(string file, bool loop, double volume, Action? finished)
	{
		var h = new Handle(this, "sw" + Interlocked.Increment(ref _next));
		_live[h] = 0;
		if (!h.Open(file, loop, volume))
		{
			_live.TryRemove(h, out _);
			finished?.Invoke();
		}
		else if (!loop) new Thread(() => h.Wait(finished)) { IsBackground = true }.Start();
		return h;
	}

	public void StopAll()
	{
		foreach (var h in _live.Keys) h.Stop();
	}

	sealed class Handle : IAudioHandle
	{
		readonly MciAudioPlayer _owner;
		readonly string _alias;
		readonly object _lock = new();
		bool _open;

		public Handle(MciAudioPlayer owner, string alias)
		{
			_owner = owner;
			_alias = alias;
		}

		public bool Open(string file, bool loop, double volume)
		{
			lock (_lock)
			{
				if (mciSendString($"open \"{file}\" type waveaudio alias {_alias}", null, 0, IntPtr.Zero) != 0) return false;
				_open = true;
				mciSendString($"setaudio {_alias} volume to {(int)Math.Round(volume * 1000)}", null, 0, IntPtr.Zero);
				if (mciSendString($"play {_alias}{(loop ? " repeat" : "")}", null, 0, IntPtr.Zero) != 0)
				{
					Close();
					return false;
				}
				return true;
			}
		}

		public void Wait(Action? finished)
		{
			var sb = new StringBuilder(32);
			while (true)
			{
				Thread.Sleep(120);
				lock (_lock)
				{
					if (!_open) return;
					sb.Clear();
					if (mciSendString($"status {_alias} mode", sb, sb.Capacity, IntPtr.Zero) != 0 || sb.ToString() != "playing")
					{
						Close();
						_owner._live.TryRemove(this, out _);
						break;
					}
				}
			}
			finished?.Invoke();
		}

		void Close()
		{
			if (!_open) return;
			_open = false;
			mciSendString($"stop {_alias}", null, 0, IntPtr.Zero);
			mciSendString($"close {_alias}", null, 0, IntPtr.Zero);
		}

		public void Stop()
		{
			lock (_lock) Close();
			_owner._live.TryRemove(this, out _);
		}
	}
}

/// <summary>
/// The app-wide audio: one voice channel and one music channel on top of the OS backend, plus the on/off toggles
/// the preview panels share. Does nothing (and says why) if no player exists.
/// </summary>
public static class AudioService
{
	public const double MusicVolume = 0.5, VoiceVolume = 1.0;

	static readonly object Lock = new();
	static readonly List<IDisposable> Signals = new();
	static IAudioPlayer? _player;
	static bool _detected;
	static IAudioHandle? _voice, _music;
	static string? _voicePath, _musicPath;
	static object? _musicOwner;
	static long _voiceGen;
	static bool _voiceEnabled = true, _musicEnabled = true;

	public static IAudioPlayer? Player
	{
		get
		{
			lock (Lock)
			{
				if (!_detected)
				{
					_detected = true;
					try
					{
						_player = OperatingSystem.IsWindows() ? new MciAudioPlayer() : OperatingSystem.IsLinux() || OperatingSystem.IsMacOS() ? ProcessAudioPlayer.Detect() : null;
					}
					catch (Exception ex) when (ex is DllNotFoundException or EntryPointNotFoundException)
					{
						_player = null;
					}
					AppDomain.CurrentDomain.ProcessExit += (_, _) => Shutdown();
					if (!OperatingSystem.IsWindows())
					{
						// Don't orphan a looping player when the app is closed from a terminal or killed politely.
						foreach (var sig in new[] { System.Runtime.InteropServices.PosixSignal.SIGTERM, System.Runtime.InteropServices.PosixSignal.SIGHUP, System.Runtime.InteropServices.PosixSignal.SIGINT })
							Signals.Add(System.Runtime.InteropServices.PosixSignalRegistration.Create(sig, _ => Shutdown()));
					}
				}
				return _player;
			}
		}
	}

	public static bool Available => Player != null;

	public static string UnavailableReason => OperatingSystem.IsLinux()
		? "No audio player found. Install ffmpeg (ffplay), mpv or pulseaudio-utils (paplay)."
		: OperatingSystem.IsMacOS() ? "afplay was not found." : "Audio playback is not supported on this system.";

	public static string BackendName => Player?.Name ?? "none";

	public static bool VoiceEnabled
	{
		get => _voiceEnabled;
		set
		{
			if (_voiceEnabled == value) return;
			_voiceEnabled = value;
			if (!value) StopVoice();
			Changed?.Invoke();
		}
	}

	public static bool MusicEnabled
	{
		get => _musicEnabled;
		set
		{
			if (_musicEnabled == value) return;
			_musicEnabled = value;
			if (!value) StopMusic();
			Changed?.Invoke();
		}
	}

	/// <summary>A toggle changed (raised on the caller's thread).</summary>
	public static event Action? Changed;
	/// <summary>The voice clip that is playing changed or ended (raised on the UI thread).</summary>
	public static event Action? VoiceChanged;
	/// <summary>The music track that is playing changed (raised on the caller's thread).</summary>
	public static event Action? MusicChanged;

	public static string? CurrentVoice { get { lock (Lock) return _voicePath; } }
	public static string? CurrentMusic { get { lock (Lock) return _musicPath; } }

	/// <summary>Plays a clip, replacing any clip already playing. Silently does nothing without a player.</summary>
	public static void PlayVoice(string path)
	{
		var player = Player;
		if (player == null) return;
		long gen;
		lock (Lock)
		{
			StopVoiceCore();
			gen = ++_voiceGen;
			_voicePath = path;
			_voice = player.Play(path, false, VoiceVolume, () => OnVoiceFinished(gen));
		}
		VoiceChanged?.Invoke();
	}

	static void OnVoiceFinished(long gen)
	{
		lock (Lock)
		{
			if (_voiceGen != gen) return;
			_voice = null;
			_voicePath = null;
		}
		Dispatcher.UIThread.Post(() => VoiceChanged?.Invoke());
	}

	public static void StopVoice()
	{
		bool had;
		lock (Lock)
		{
			had = _voicePath != null;
			StopVoiceCore();
		}
		if (had) VoiceChanged?.Invoke();
	}

	static void StopVoiceCore()
	{
		_voiceGen++;
		_voice?.Stop();
		_voice = null;
		_voicePath = null;
	}

	/// <summary>Loops a track for <paramref name="owner"/>. Asking for the track already playing keeps it going.</summary>
	public static void PlayMusic(object owner, string path)
	{
		var player = Player;
		if (player == null || !_musicEnabled) return;
		lock (Lock)
		{
			if (_musicPath == path && _music != null)
			{
				_musicOwner = owner;
				return;
			}
			_music?.Stop();
			_musicOwner = owner;
			_musicPath = path;
			_music = player.Play(path, true, MusicVolume, null);
		}
		MusicChanged?.Invoke();
	}

	/// <summary>Stops the music if <paramref name="owner"/> started it (null stops it whoever did).</summary>
	public static void StopMusic(object? owner = null)
	{
		lock (Lock)
		{
			if (_music == null || (owner != null && !ReferenceEquals(owner, _musicOwner))) return;
			_music.Stop();
			_music = null;
			_musicPath = null;
			_musicOwner = null;
		}
		MusicChanged?.Invoke();
	}

	/// <summary>Kills every sound; called when the app exits.</summary>
	public static void Shutdown()
	{
		lock (Lock)
		{
			_voiceGen++;
			_voice?.Stop();
			_music?.Stop();
			_voice = _music = null;
			_voicePath = _musicPath = null;
			_player?.StopAll();
		}
	}
}
