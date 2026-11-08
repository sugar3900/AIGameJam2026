// I Can Fix Him - AI Game Jam 2026

#include "World/FixHimDoor.h"
#include "Player/FixHimPlayerController.h"
#include "Core/FixHimSettings.h"
#include "Audio/FixHimSfxSubsystem.h"
#include "Components/StaticMeshComponent.h"
#include "Engine/StaticMesh.h"
#include "Engine/World.h"
#include "EngineUtils.h"

AFixHimDoor::AFixHimDoor()
{
	Toggle = EInteractToggle::None;
	InteractRangeOverride = 220.f;
	ShineColor = FLinearColor(1.f, 0.85f, 0.6f);
	OutlineColor = FLinearColor(1.f, 0.75f, 0.4f);
}

FName AFixHimDoor::DefaultInteractSfx(bool bNowOn) const
{
	const UFixHimSfxSubsystem* Sfx = UFixHimSfxSubsystem::Get(this);
	return !Sfx || Sfx->Has(TEXT("DoorHandle")) ? FName(TEXT("DoorHandle")) : FName(TEXT("DoorKnock"));
}

AFixHimDoor* AFixHimDoor::EnsureInWorld(UWorld* World)
{
	if (!World)
	{
		return nullptr;
	}
	TActorIterator<AFixHimDoor> Existing(World);
	if (Existing)
	{
		return *Existing;
	}

	// Same placement as Tools/Editor/build_apartment.py: the doorway in the living room's south wall
	// (x 132-248, y 0-14). The slab is invisible, slightly thicker than the authored door's blocking proxy so the
	// hover trace hits it first; the authored door mesh stays the visible one.
	const FTransform T(FRotator::ZeroRotator, FVector(190.f, 0.f, 0.f));
	AFixHimDoor* Door = World->SpawnActorDeferred<AFixHimDoor>(AFixHimDoor::StaticClass(), T);
	if (!Door)
	{
		return nullptr;
	}
	Door->RoomId = TEXT("living");
	Door->BodyColor = FLinearColor(0.8f, 0.2f, 0.38f);
	Door->Body->SetStaticMesh(UFixHimSettings::Get()->CubeMesh.LoadSynchronous());
	Door->Body->SetRelativeLocation(FVector(0.f, 8.f, 109.f));
	Door->Body->SetRelativeScale3D(FVector(1.16f, 0.16f, 2.18f));
	Door->Body->SetHiddenInGame(true);
	Door->FinishSpawning(T);
	return Door;
}

void AFixHimDoor::Interact(AFixHimPlayerController* Player)
{
	PlayInteractSfx();
	if (Player)
	{
		Player->OpenDoorPrompt();
	}
}

FText AFixHimDoor::GetPrompt() const
{
	return NSLOCTEXT("FixHim", "DoorPrompt", "Leave the apartment");
}
