// I Can Fix Him - AI Game Jam 2026

#include "Core/FixHimWarmupSubsystem.h"
#include "ICanFixHim.h"
#include "Core/FixHimSettings.h"
#include "Dialogue/DialogueTypes.h"
#include "Dialogue/FixHimDialogueSubsystem.h"
#include "World/FixHimPuffFx.h"
#include "Engine/GameInstance.h"
#include "Engine/World.h"
#include "Misc/PackageName.h"
#include "PipelineStateCache.h"
#if WITH_EDITOR
#include "AssetCompilingManager.h"
#endif

namespace
{
	/** Frames to keep rendering before trusting "nothing left": the first frames create render proxies and issue PSO requests. */
	constexpr int32 MinFrames = 5;
	/** Consecutive frames with no outstanding work before declaring ready. */
	constexpr int32 SettleFrames = 3;
	/** How often to log progress while still waiting. There is no timeout: the game never starts with work outstanding. */
	constexpr double ReportIntervalSeconds = 15.0;

	/** "/Game/Dir/Asset" or "/Game/Dir/Asset.Asset" (hunk JSON paths may omit the object name). */
	FSoftObjectPath HunkAssetPath(const FString& Path)
	{
		FString ObjectPath = Path;
		if (!FPackageName::GetShortName(ObjectPath).Contains(TEXT(".")))
		{
			ObjectPath += TEXT(".") + FPackageName::GetShortName(ObjectPath);
		}
		return FSoftObjectPath(ObjectPath);
	}
}

UFixHimWarmupSubsystem* UFixHimWarmupSubsystem::Get(const UObject* WorldContext)
{
	const UWorld* World = WorldContext ? WorldContext->GetWorld() : nullptr;
	const UGameInstance* GI = World ? World->GetGameInstance() : nullptr;
	return GI ? GI->GetSubsystem<UFixHimWarmupSubsystem>() : nullptr;
}

void UFixHimWarmupSubsystem::Begin(UWorld& World)
{
	if (bWarmed)
	{
		return;
	}
	StartTime = FPlatformTime::Seconds();
	NextReportTime = StartTime + ReportIntervalSeconds;
	FramesTicked = 0;
	IdleFrames = 0;
	PeakRemaining = 0;
	Progress = 0.f;
	// Loading starts each material's shader compilation (or DDC fetch) in the editor; Update waits for it to finish
	// while the loading screen draws.
	if (Retained.IsEmpty())
	{
		LoadGameplayAssets();
	}
	WarmEffects(World);
	bStarted = true;
}

bool UFixHimWarmupSubsystem::Update()
{
	if (bWarmed)
	{
		return true;
	}
	if (!bStarted)
	{
		return false;
	}

	++FramesTicked;
	const int32 Remaining = CountRemainingWork();
	PeakRemaining = FMath::Max(PeakRemaining, Remaining);
	IdleFrames = Remaining == 0 ? IdleFrames + 1 : 0;

	const float Done = PeakRemaining > 0 ? 1.f - float(Remaining) / float(PeakRemaining) : 1.f;
	// Hold back the last sliver until really finished, so the bar never sits at 100% while still waiting.
	Progress = FMath::Max(Progress, FMath::Min(Done, 0.97f));

	const double Now = FPlatformTime::Seconds();
	if (FramesTicked < MinFrames || IdleFrames < SettleFrames)
	{
		if (Now >= NextReportTime)
		{
			NextReportTime = Now + ReportIntervalSeconds;
			UE_LOG(LogFixHim, Log, TEXT("Warmup: still preparing after %.0fs, %d items left (peak %d)."), Now - StartTime, Remaining, PeakRemaining);
		}
		return false;
	}
	UE_LOG(LogFixHim, Log, TEXT("Warmup: %d assets ready in %.2fs (peak %d items compiling)."), Retained.Num(), Now - StartTime, PeakRemaining);
	bWarmed = true;
	Progress = 1.f;
	return true;
}

int32 UFixHimWarmupSubsystem::CountRemainingWork() const
{
	int32 Remaining = 0;
#if WITH_EDITOR
	// Includes shader maps: this is the "Preparing Shaders (N)" count the editor shows.
	Remaining += FAssetCompilingManager::Get().GetNumRemainingAssets();
#endif
	Remaining += static_cast<int32>(PipelineStateCache::NumActivePrecacheRequests());
	return Remaining;
}

void UFixHimWarmupSubsystem::LoadGameplayAssets()
{
	const UFixHimSettings* S = UFixHimSettings::Get();
	TArray<FSoftObjectPath> Paths = {
		S->CharacterMaterial.ToSoftObjectPath(),
		S->FlatMaterial.ToSoftObjectPath(),
		S->TranslucentMaterial.ToSoftObjectPath(),
		S->SparkleMaterial.ToSoftObjectPath(),
		S->ShineMaterial.ToSoftObjectPath(),
		S->HoverOutlineMaterial.ToSoftObjectPath(),   // else the first hover shows no rim while its shader compiles
		S->PortraitMaterial.ToSoftObjectPath(),
		S->HunkMesh.ToSoftObjectPath(),
		S->CubeMesh.ToSoftObjectPath(),
		S->SphereMesh.ToSoftObjectPath(),
		S->CylinderMesh.ToSoftObjectPath(),
		S->PlaneMesh.ToSoftObjectPath(),
		S->HeartTexture.ToSoftObjectPath(),
		S->PlayerPortraitTexture.ToSoftObjectPath(),
	};

	// Each character's model (and with it his materials and textures), idle and painted portrait.
	if (const UFixHimDialogueSubsystem* Dialogue = UFixHimDialogueSubsystem::Get(GetWorld()))
	{
		for (const TPair<FString, FHunkDefinition>& Pair : Dialogue->GetAllHunks())
		{
			for (const FString* Path : { &Pair.Value.Mesh, &Pair.Value.Idle, &Pair.Value.Portrait })
			{
				if (!Path->IsEmpty())
				{
					Paths.Add(HunkAssetPath(*Path));
				}
			}
		}
	}

	for (const FSoftObjectPath& Path : Paths)
	{
		if (Path.IsNull())
		{
			continue;
		}
		if (UObject* Asset = Path.TryLoad())
		{
			Retained.AddUnique(Asset);
		}
		else
		{
			UE_LOG(LogFixHim, Warning, TEXT("Warmup: '%s' not found."), *Path.ToString());
		}
	}
}

void UFixHimWarmupSubsystem::WarmEffects(UWorld& World)
{
	// The bursts are built from components created on spawn. Building each style once, hidden, registers those
	// components with their materials so pipeline states are requested now. They destroy themselves as usual.
	static constexpr EFixHimPuffStyle Styles[] = {
		EFixHimPuffStyle::BubblePop, EFixHimPuffStyle::Appear,
		EFixHimPuffStyle::SparkleIn, EFixHimPuffStyle::SparkleOut,
		EFixHimPuffStyle::SporesIn, EFixHimPuffStyle::SporesOut,
		EFixHimPuffStyle::SurgeIn, EFixHimPuffStyle::SurgeOut,
	};
	for (const EFixHimPuffStyle Style : Styles)
	{
		if (AFixHimPuffFx* Fx = AFixHimPuffFx::Spawn(&World, FVector::ZeroVector, FLinearColor::White, Style))
		{
			Fx->SetActorHiddenInGame(true);
		}
	}
}
