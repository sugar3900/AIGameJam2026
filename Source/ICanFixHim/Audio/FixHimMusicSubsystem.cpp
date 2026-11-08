// I Can Fix Him - AI Game Jam 2026

#include "Audio/FixHimMusicSubsystem.h"
#include "Kismet/GameplayStatics.h"
#include "ICanFixHim.h"
#include "AssetRegistry/AssetRegistryModule.h"
#include "Components/AudioComponent.h"
#include "Dialogue/FixHimVoiceSubsystem.h"
#include "Engine/GameInstance.h"
#include "Engine/World.h"
#include "HAL/IConsoleManager.h"
#include "HAL/PlatformTime.h"
#include "Sound/SoundBase.h"
#include "Sound/SoundWave.h"

namespace
{
	const TCHAR* MusicRoot = TEXT("/Game/ICanFixHim/Audio/BGM");

	/** Tracks are peak-normalised at -3 dBFS and the option defaults to 0.5; this keeps them under the SFX. */
	constexpr float TrackTrim = 0.8f;
	/** Music dips about 6 dB while a voice line is playing. */
	constexpr float VoiceDuckGain = 0.5f;

	/** "BGM_Explore" -> "Explore". */
	FName TrackName(FString AssetName)
	{
		AssetName.RemoveFromStart(TEXT("BGM_"));
		return FName(*AssetName);
	}

	FAutoConsoleCommandWithWorldAndArgs GMusicPlay(
		TEXT("Music.Play"),
		TEXT("Music.Play <Name> crossfades to a music track (e.g. Music.Play Tyler); with no name, lists them."),
		FConsoleCommandWithWorldAndArgsDelegate::CreateLambda([](const TArray<FString>& Args, UWorld* World)
		{
			UFixHimMusicSubsystem* Music = UFixHimMusicSubsystem::Get(World);
			if (!Music || Args.IsEmpty())
			{
				UE_LOG(LogFixHim, Display, TEXT("Music.Play <Name>; tracks are BGM_<Name> under %s (now: %s)"), MusicRoot,
					Music ? *Music->GetCurrentTrack().ToString() : TEXT("-"));
				return;
			}
			if (!Music->PlayTrack(FName(*Args[0]), 1.f))
			{
				UE_LOG(LogFixHim, Display, TEXT("Music.Play: '%s' missing"), *Args[0]);
			}
		}));

	FAutoConsoleCommandWithWorld GMusicStop(
		TEXT("Music.Stop"),
		TEXT("Fade the music out."),
		FConsoleCommandWithWorldDelegate::CreateLambda([](UWorld* World)
		{
			if (UFixHimMusicSubsystem* Music = UFixHimMusicSubsystem::Get(World))
			{
				Music->StopMusic(1.f);
			}
		}));

	FAutoConsoleCommandWithWorld GMusicStatus(
		TEXT("Music.Status"),
		TEXT("Log the music voices (track, playing, crossfade level, volume)."),
		FConsoleCommandWithWorldDelegate::CreateLambda([](UWorld* World)
		{
			if (UFixHimMusicSubsystem* Music = UFixHimMusicSubsystem::Get(World))
			{
				UE_LOG(LogFixHim, Display, TEXT("Music.Status %s"), *Music->DescribeState());
			}
		}));

	FAutoConsoleCommandWithWorld GMusicReload(
		TEXT("Music.Reload"),
		TEXT("Rescan the music folder."),
		FConsoleCommandWithWorldDelegate::CreateLambda([](UWorld* World)
		{
			if (UFixHimMusicSubsystem* Music = UFixHimMusicSubsystem::Get(World))
			{
				Music->RebuildIndex();
			}
		}));
}

UFixHimMusicSubsystem* UFixHimMusicSubsystem::Get(const UObject* WorldContext)
{
	const UWorld* World = WorldContext ? WorldContext->GetWorld() : nullptr;
	const UGameInstance* GI = World ? World->GetGameInstance() : nullptr;
	return GI ? GI->GetSubsystem<UFixHimMusicSubsystem>() : nullptr;
}

void UFixHimMusicSubsystem::Initialize(FSubsystemCollectionBase& Collection)
{
	Super::Initialize(Collection);
	RebuildIndex();
	LastTickTime = FPlatformTime::Seconds();
	TickHandle = FTSTicker::GetCoreTicker().AddTicker(FTickerDelegate::CreateUObject(this, &UFixHimMusicSubsystem::Tick), 0.f);
}

void UFixHimMusicSubsystem::Deinitialize()
{
	FTSTicker::GetCoreTicker().RemoveTicker(TickHandle);
	for (TObjectPtr<UAudioComponent>& Voice : Voices)
	{
		if (Voice)
		{
			Voice->Stop();
			Voice->DestroyComponent();
		}
		Voice = nullptr;
	}
	Current = NAME_None;
	Super::Deinitialize();
}

void UFixHimMusicSubsystem::RebuildIndex()
{
	Index.Reset();
	Warned.Reset();
	IAssetRegistry& Registry = FModuleManager::LoadModuleChecked<FAssetRegistryModule>(TEXT("AssetRegistry")).Get();
#if WITH_EDITOR
	// In the editor the background scan may not have reached the folder yet.
	Registry.ScanPathsSynchronous({ MusicRoot }, /*bForceRescan*/ false);
#endif
	FARFilter Filter;
	Filter.PackagePaths.Add(MusicRoot);
	Filter.bRecursivePaths = true;
	Filter.ClassPaths.Add(USoundWave::StaticClass()->GetClassPathName());
	TArray<FAssetData> Assets;
	Registry.GetAssets(Filter, Assets);
	for (const FAssetData& Asset : Assets)
	{
		Index.Add(TrackName(Asset.AssetName.ToString()), Asset.GetSoftObjectPath());
	}
	UE_LOG(LogFixHim, Log, TEXT("Music: %d tracks indexed under %s"), Index.Num(), MusicRoot);
}

bool UFixHimMusicSubsystem::PlayTrack(FName Name, float FadeSeconds)
{
	if (Name.IsNone())
	{
		return false;
	}
	const FSoftObjectPath* Path = Index.Find(Name);
	if (!Path)
	{
		if (!Warned.Contains(Name))
		{
			Warned.Add(Name);
			UE_LOG(LogFixHim, Warning, TEXT("Music: no track named '%s' (expected BGM_%s under %s)"), *Name.ToString(), *Name.ToString(), MusicRoot);
		}
		return false;
	}

	UAudioComponent* Playing = Voices[Active];
	if (Name == Current && Playing && Playing->IsPlaying() && State[Active].Target > 0.f)
	{
		return true; // already playing: never restart
	}

	USoundBase* Sound = Cast<USoundBase>(Path->TryLoad());
	UWorld* World = GetGameInstance() ? GetGameInstance()->GetWorld() : nullptr;
	if (!Sound || !World)
	{
		return false;
	}
	const int32 Next = 1 - Active;
	if (UAudioComponent* Old = Voices[Next])
	{
		Old->Stop();
		Old->DestroyComponent();
	}
	// Persists across level transitions; not auto-destroyed so it can be faded out and replaced by us.
	UAudioComponent* Voice = UGameplayStatics::CreateSound2D(World, Sound, 0.f, 1.f, 0.f, nullptr, /*bPersistAcrossLevelTransition*/ true, /*bAutoDestroy*/ false);
	if (!Voice)
	{
		return false;
	}
	Voice->bIsUISound = true; // keeps playing while the game is paused
	Voice->bIsMusic = true;
	// Never lose the music to voice stealing when lots of SFX play at once.
	Voice->bOverridePriority = true;
	Voice->Priority = 100.f;
	Voices[Next] = Voice;

	const float Rate = 1.f / FMath::Max(FadeSeconds, 0.02f);
	// The outgoing track keeps its current level and fades out; the new one starts from silence.
	State[Active].Target = 0.f;
	State[Active].Rate = Rate;
	State[Next] = { 0.f, 1.f, Rate };
	Voice->SetVolumeMultiplier(0.f);
	Voice->Play(0.f);
	Active = Next;
	Current = Name;
	if (FadeSeconds <= 0.f)
	{
		State[Next].Level = 1.f;
		State[1 - Next].Level = 0.f;
	}
	ApplyVolumes();
	return true;
}

void UFixHimMusicSubsystem::StopMusic(float FadeSeconds)
{
	for (FVoiceState& S : State)
	{
		S.Target = 0.f;
		S.Rate = 1.f / FMath::Max(FadeSeconds, 0.02f);
	}
	Current = NAME_None;
}

void UFixHimMusicSubsystem::SetMusicVolume(float Volume)
{
	UserVolume = FMath::Clamp(Volume, 0.f, 1.f);
	ApplyVolumes();
}

void UFixHimMusicSubsystem::SetDuck(float Multiplier, float FadeSeconds)
{
	DuckTarget = FMath::Clamp(Multiplier, 0.f, 1.f);
	DuckSeconds = FMath::Max(FadeSeconds, 0.02f);
}

void UFixHimMusicSubsystem::ApplyVolumes()
{
	const float Base = UserVolume * TrackTrim * DuckCurrent * VoiceDuck;
	for (int32 i = 0; i < 2; ++i)
	{
		if (UAudioComponent* Voice = Voices[i])
		{
			Voice->SetVolumeMultiplier(Base * FMath::Sin(State[i].Level * HALF_PI));
		}
	}
}

bool UFixHimMusicSubsystem::Tick(float /*DeltaTime*/)
{
	// Real time on purpose: this must keep fading while the game is paused or a level is loading.
	const double Now = FPlatformTime::Seconds();
	const float Dt = static_cast<float>(FMath::Clamp(Now - LastTickTime, 0.0, 0.1));
	LastTickTime = Now;

	// Voice-over ducking (about -6 dB, fast attack, slower release).
	const UFixHimVoiceSubsystem* Voice = GetGameInstance() ? GetGameInstance()->GetSubsystem<UFixHimVoiceSubsystem>() : nullptr;
	const float VoiceTarget = (Voice && Voice->IsPlaying()) ? VoiceDuckGain : 1.f;
	VoiceDuck = FMath::FInterpTo(VoiceDuck, VoiceTarget, Dt, VoiceTarget < VoiceDuck ? 10.f : 3.f);
	DuckCurrent = FMath::FInterpConstantTo(DuckCurrent, DuckTarget, Dt, 0.6f / DuckSeconds);

	for (int32 i = 0; i < 2; ++i)
	{
		FVoiceState& S = State[i];
		S.Level = FMath::FInterpConstantTo(S.Level, S.Target, Dt, S.Rate);
		if (S.Target <= 0.f && S.Level <= 0.f && Voices[i] && Voices[i]->IsPlaying())
		{
			Voices[i]->Stop();
		}
	}
	ApplyVolumes();
	return true;
}

FString UFixHimMusicSubsystem::DescribeState() const
{
	FString Out = FString::Printf(TEXT("current=%s active=%d user=%.2f duck=%.2f voiceDuck=%.2f"), *Current.ToString(), Active, UserVolume, DuckCurrent, VoiceDuck);
	for (int32 i = 0; i < 2; ++i)
	{
		const UAudioComponent* V = Voices[i];
		Out += FString::Printf(TEXT(" | voice%d sound=%s playing=%d level=%.2f target=%.2f"), i,
			V && V->Sound ? *V->Sound->GetName() : TEXT("-"), V && V->IsPlaying() ? 1 : 0, State[i].Level, State[i].Target);
	}
	return Out;
}

void FixHim::Music(const UObject* WorldContext, FName Track, float FadeSeconds)
{
	if (UFixHimMusicSubsystem* M = UFixHimMusicSubsystem::Get(WorldContext))
	{
		M->PlayTrack(Track, FadeSeconds);
	}
}
