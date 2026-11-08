// I Can Fix Him - AI Game Jam 2026

#pragma once

#include "CoreMinimal.h"
#include "Containers/Ticker.h"
#include "Subsystems/GameInstanceSubsystem.h"
#include "FixHimMusicSubsystem.generated.h"

class UAudioComponent;

/**
 * Looping background music. A track "Foo" is the sound wave BGM_Foo under /Game/ICanFixHim/Audio/BGM (made by
 * Tools/Audio/generate_bgm.py + Tools/Editor/import_bgm.py).
 *
 * Two audio components (owned by the game instance, so they survive level reloads such as returning to the title)
 * are equal-power crossfaded by PlayTrack. They're 2D UI sounds, so music keeps playing while the game is paused.
 * The fade is driven by a core ticker, not world time, for the same reason. A missing track is logged once and
 * ignored. Music volume is the player's option (FFixHimOptions::MusicVolume) times a fixed per-track trim, and is
 * ducked while a dialogue voice line plays and while a caller asks for it (the podcast).
 *
 * Who decides what plays lives in AFixHimPlayerController::UpdateMusic.
 */
UCLASS()
class ICANFIXHIM_API UFixHimMusicSubsystem : public UGameInstanceSubsystem
{
	GENERATED_BODY()

public:
	static UFixHimMusicSubsystem* Get(const UObject* WorldContext);

	virtual void Initialize(FSubsystemCollectionBase& Collection) override;
	virtual void Deinitialize() override;

	/** Rescan the BGM folder (after importing new tracks while the game is running). */
	void RebuildIndex();
	bool Has(FName Name) const { return Index.Contains(Name); }

	/** Crossfade to a track. Already playing it: nothing happens (it never restarts). False if the track is missing. */
	bool PlayTrack(FName Name, float FadeSeconds = 1.5f);
	void StopMusic(float FadeSeconds = 1.f);
	FName GetCurrentTrack() const { return Current; }

	/** 0..1 player option. Applied live. */
	void SetMusicVolume(float Volume);
	float GetMusicVolume() const { return UserVolume; }

	/** Extra gain (1 = none) that eases in/out, e.g. 0.4 while the opening podcast plays. Cheap to call every frame. */
	void SetDuck(float Multiplier, float FadeSeconds = 0.8f);

private:
	bool Tick(float DeltaTime);
	void ApplyVolumes();

	struct FVoiceState
	{
		/** 0..1 crossfade position; the audible gain is sin(Level * pi/2), which gives an equal-power crossfade. */
		float Level = 0.f;
		float Target = 0.f;
		float Rate = 1.f;
	};

	TMap<FName, FSoftObjectPath> Index;
	TSet<FName> Warned;

	/**
	 * The two crossfading voices. A component with no world can't resolve the right audio device (in the editor the
	 * play session has its own), so they are normal world-registered 2D sounds that persist across level
	 * transitions. Weak on purpose: the world owns them, and a strong reference from here would keep a finished
	 * play-in-editor world alive. They are recreated when a new world needs music.
	 */
	TWeakObjectPtr<UAudioComponent> Voices[2];
	FVoiceState State[2];
	int32 Active = 0;
	FName Current;

	float UserVolume = 0.5f;
	float DuckTarget = 1.f, DuckCurrent = 1.f, DuckSeconds = 0.8f;
	float VoiceDuck = 1.f;
	double LastTickTime = 0.0;
	FTSTicker::FDelegateHandle TickHandle;
};

namespace FixHim
{
	/** Fire-and-forget: FixHim::Music(this, "Explore"). Safe with a null context. */
	ICANFIXHIM_API void Music(const UObject* WorldContext, FName Track, float FadeSeconds = 1.5f);
}
