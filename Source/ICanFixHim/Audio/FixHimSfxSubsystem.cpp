// I Can Fix Him - AI Game Jam 2026

#include "Audio/FixHimSfxSubsystem.h"
#include "ICanFixHim.h"
#include "AssetRegistry/AssetRegistryModule.h"
#include "Engine/GameInstance.h"
#include "Engine/World.h"
#include "HAL/IConsoleManager.h"
#include "HAL/PlatformTime.h"
#include "Kismet/GameplayStatics.h"
#include "Sound/SoundWave.h"

namespace
{
	const TCHAR* SfxRoot = TEXT("/Game/ICanFixHim/Audio/SFX");

	/** Same sound can't retrigger faster than this (real time, so it also works while paused). */
	constexpr double MinRepeatSeconds = 0.04;

	/** "SFX_Footstep_3" -> "Footstep"; "SFX_ButtonClick" -> "ButtonClick". */
	FName BaseName(FString AssetName)
	{
		AssetName.RemoveFromStart(TEXT("SFX_"));
		int32 Underscore;
		if (AssetName.FindLastChar(TEXT('_'), Underscore) && AssetName.Mid(Underscore + 1).IsNumeric())
		{
			AssetName.LeftInline(Underscore);
		}
		return FName(*AssetName);
	}

	FAutoConsoleCommandWithWorldAndArgs GSfxTest(
		TEXT("Sfx.Test"),
		TEXT("Sfx.Test <Name> plays a sound effect (e.g. Sfx.Test FixComplete); with no name, lists them."),
		FConsoleCommandWithWorldAndArgsDelegate::CreateLambda([](const TArray<FString>& Args, UWorld* World)
		{
			UFixHimSfxSubsystem* Sfx = UFixHimSfxSubsystem::Get(World);
			if (!Sfx || Args.IsEmpty())
			{
				UE_LOG(LogFixHim, Display, TEXT("Sfx.Test <Name>; sounds are SFX_<Name>[_n] under %s"), SfxRoot);
				return;
			}
			if (!Sfx->Play2D(FName(*Args[0]), 1.f, 0.f))
			{
				UE_LOG(LogFixHim, Display, TEXT("Sfx.Test: '%s' missing"), *Args[0]);
			}
		}));

	FAutoConsoleCommandWithWorld GSfxReload(
		TEXT("Sfx.Reload"),
		TEXT("Rescan the SFX folder."),
		FConsoleCommandWithWorldDelegate::CreateLambda([](UWorld* World)
		{
			if (UFixHimSfxSubsystem* Sfx = UFixHimSfxSubsystem::Get(World))
			{
				Sfx->RebuildIndex();
			}
		}));
}

UFixHimSfxSubsystem* UFixHimSfxSubsystem::Get(const UObject* WorldContext)
{
	const UWorld* World = WorldContext ? WorldContext->GetWorld() : nullptr;
	const UGameInstance* GI = World ? World->GetGameInstance() : nullptr;
	return GI ? GI->GetSubsystem<UFixHimSfxSubsystem>() : nullptr;
}

void UFixHimSfxSubsystem::Initialize(FSubsystemCollectionBase& Collection)
{
	Super::Initialize(Collection);
	RebuildIndex();
}

void UFixHimSfxSubsystem::RebuildIndex()
{
	Index.Reset();
	Warned.Reset();
	IAssetRegistry& Registry = FModuleManager::LoadModuleChecked<FAssetRegistryModule>(TEXT("AssetRegistry")).Get();
#if WITH_EDITOR
	// In the editor the background scan may not have reached the folder yet.
	Registry.ScanPathsSynchronous({ SfxRoot }, /*bForceRescan*/ false);
#endif
	FARFilter Filter;
	Filter.PackagePaths.Add(SfxRoot);
	Filter.bRecursivePaths = true;
	Filter.ClassPaths.Add(USoundWave::StaticClass()->GetClassPathName());
	TArray<FAssetData> Assets;
	Registry.GetAssets(Filter, Assets);
	for (const FAssetData& Asset : Assets)
	{
		Index.FindOrAdd(BaseName(Asset.AssetName.ToString())).Variants.Add(Asset.GetSoftObjectPath());
	}
	UE_LOG(LogFixHim, Log, TEXT("Sfx: %d sounds (%d files) indexed under %s"), Index.Num(), Assets.Num(), SfxRoot);
}

USoundBase* UFixHimSfxSubsystem::Pick(FName Name)
{
	FEntry* Entry = Index.Find(Name);
	if (Name.IsNone())
	{
		return nullptr;
	}
	if (!Entry)
	{
		if (!Warned.Contains(Name))
		{
			Warned.Add(Name);
			UE_LOG(LogFixHim, Warning, TEXT("Sfx: no sound named '%s' (expected SFX_%s under %s)"), *Name.ToString(), *Name.ToString(), SfxRoot);
		}
		return nullptr;
	}
	const double Now = FPlatformTime::Seconds();
	if (Now - Entry->LastPlayTime < MinRepeatSeconds)
	{
		return nullptr;
	}

	int32 Choice = FMath::RandHelper(Entry->Variants.Num());
	if (Entry->Variants.Num() > 1 && Choice == Entry->LastVariant)
	{
		Choice = (Choice + 1 + FMath::RandHelper(Entry->Variants.Num() - 1)) % Entry->Variants.Num();
	}
	USoundBase* Sound = Cast<USoundBase>(Entry->Variants[Choice].TryLoad());
	if (!Sound)
	{
		return nullptr;
	}
	Loaded.AddUnique(Sound);
	Entry->LastVariant = Choice;
	Entry->LastPlayTime = Now;
	return Sound;
}

bool UFixHimSfxSubsystem::Play2D(FName Name, float Volume, float PitchJitter)
{
	UWorld* World = GetGameInstance() ? GetGameInstance()->GetWorld() : nullptr;
	USoundBase* Sound = World ? Pick(Name) : nullptr;
	if (!Sound)
	{
		return false;
	}
	const float Pitch = 1.f + FMath::FRandRange(-PitchJitter, PitchJitter);
	// bIsUISound keeps it audible while the game is paused.
	UGameplayStatics::PlaySound2D(World, Sound, Volume, Pitch, 0.f, nullptr, nullptr, /*bIsUISound*/ true);
	return true;
}

bool UFixHimSfxSubsystem::PlayAt(FName Name, const FVector& Location, float Volume, float PitchJitter)
{
	UWorld* World = GetGameInstance() ? GetGameInstance()->GetWorld() : nullptr;
	USoundBase* Sound = World ? Pick(Name) : nullptr;
	if (!Sound)
	{
		return false;
	}
	const float Pitch = 1.f + FMath::FRandRange(-PitchJitter, PitchJitter);
	UGameplayStatics::PlaySoundAtLocation(World, Sound, Location, Volume, Pitch);
	return true;
}

void FixHim::Sfx(const UObject* WorldContext, FName Name, float Volume, float PitchJitter)
{
	if (UFixHimSfxSubsystem* S = UFixHimSfxSubsystem::Get(WorldContext))
	{
		S->Play2D(Name, Volume, PitchJitter);
	}
}

void FixHim::SfxAt(const UObject* WorldContext, FName Name, const FVector& Location, float Volume, float PitchJitter)
{
	if (UFixHimSfxSubsystem* S = UFixHimSfxSubsystem::Get(WorldContext))
	{
		S->PlayAt(Name, Location, Volume, PitchJitter);
	}
}
