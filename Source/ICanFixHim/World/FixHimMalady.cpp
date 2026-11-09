// I Can Fix Him - AI Game Jam 2026

#include "World/FixHimMalady.h"
#include "World/FixHimHunk.h"
#include "Player/FixHimPlayerController.h"
#include "Audio/FixHimSfxSubsystem.h"
#include "Core/FixHimAssets.h"
#include "Core/FixHimSaveSubsystem.h"
#include "Dialogue/FixHimDialogueSubsystem.h"
#include "Components/ArrowComponent.h"
#include "Components/PointLightComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Camera/CameraComponent.h"
#include "Materials/MaterialInstanceDynamic.h"
#include "Engine/World.h"

AFixHimMalady::AFixHimMalady()
{
	Toggle = EInteractToggle::None;
	// The host breathes a soft glow (Tick) instead of the occasional shine wipe.
	bShine = false;

	HunkSpawn = CreateDefaultSubobject<UArrowComponent>(TEXT("HunkSpawn"));
	HunkSpawn->SetupAttachment(Root);
	HunkSpawn->SetRelativeLocation(FVector(140.f, 0.f, 0.f));
	HunkSpawn->ArrowColor = FColor(80, 160, 255);

	TalkSpot = CreateDefaultSubobject<UArrowComponent>(TEXT("TalkSpot"));
	TalkSpot->SetupAttachment(Root);
	TalkSpot->SetRelativeLocation(FVector(300.f, 0.f, 0.f));
	TalkSpot->SetRelativeRotation(FRotator(0.f, 180.f, 0.f));
	TalkSpot->ArrowColor = FColor(255, 80, 160);

	DialogueCamera = CreateDefaultSubobject<UCameraComponent>(TEXT("DialogueCamera"));
	DialogueCamera->SetupAttachment(Root);
	DialogueCamera->SetRelativeLocation(FVector(450.f, -60.f, 80.f));
	DialogueCamera->SetRelativeRotation(FRotator(-5.f, 180.f, 0.f));
	DialogueCamera->SetFieldOfView(55.f);
	DialogueCamera->SetAutoActivate(true);

	GlowLight = CreateDefaultSubobject<UPointLightComponent>(TEXT("GlowLight"));
	GlowLight->SetupAttachment(Root);
	GlowLight->SetIntensity(600.f);
	GlowLight->SetAttenuationRadius(260.f);
	GlowLight->SetCastShadows(false);
}

void AFixHimMalady::BeginPlay()
{
	Super::BeginPlay();

	if (const UFixHimDialogueSubsystem* Dialogue = UFixHimDialogueSubsystem::Get(this))
	{
		if (const FHunkDefinition* Def = Dialogue->FindHunk(HunkId))
		{
			GlowColor = Def->GlowColor;
			HunkName = FText::FromString(Def->Name);

			FActorSpawnParameters Params;
			Params.SpawnCollisionHandlingOverride = ESpawnActorCollisionHandlingMethod::AlwaysSpawn;
			Params.Owner = this;
			HunkStandLocation = FindStandLocation(HunkSpawn->GetComponentLocation(), Def->Scale);
			Hunk = GetWorld()->SpawnActor<AFixHimHunk>(AFixHimHunk::StaticClass(), HunkStandLocation, HunkSpawn->GetComponentRotation(), Params);
			if (Hunk)
			{
				Hunk->ApplyDefinition(*Def);
			}
		}
	}

	GlowLight->SetLightColor(GlowColor);
	OutlineColor = GlowColor;
	if (ShineMID)
	{
		ShineMID->SetVectorParameterValue(TEXT("Color"), FMath::Lerp(GlowColor, FLinearColor::White, 0.25f));
	}

	BuildBrokenFx();
	if (bAutoFrameCamera)
	{
		FrameCamera();
	}
	RefreshRepairState();
}

FVector AFixHimMalady::FindStandLocation(const FVector& Around, float Scale) const
{
	// Drop onto whatever floor is below so level designers only need to get X/Y right.
	FHitResult Hit;
	FCollisionQueryParams Q(SCENE_QUERY_STAT(FixHimStand), false, this);
	const FVector Start(Around.X, Around.Y, GetActorLocation().Z + 50.f);
	const FVector End(Around.X, Around.Y, Start.Z - 2000.f);
	const float FloorZ = GetWorld()->LineTraceSingleByChannel(Hit, Start, End, ECC_Visibility, Q) ? Hit.ImpactPoint.Z : 0.f;
	return FVector(Around.X, Around.Y, FloorZ + 92.f * Scale + 1.f);
}

FVector AFixHimMalady::GetTalkLocation(float CapsuleHalfHeight) const
{
	const FVector T = TalkSpot->GetComponentLocation();
	return FVector(T.X, T.Y, HunkStandLocation.Z - 92.f + CapsuleHalfHeight);
}

void AFixHimMalady::FrameCamera()
{
	// First-person framing: Rosie's eye height at the talk spot (a touch back so he fits), looking at his face.
	const FVector Head = HunkStandLocation + FVector(0.f, 0.f, 62.f);
	const bool bMalcolm = HunkId.Equals(TEXT("malcolm"), ESearchCase::IgnoreCase);
	const FVector Talk = TalkSpot->GetComponentLocation();
	FVector Dir = Head - Talk;
	Dir.Z = 0.f;
	Dir = Dir.GetSafeNormal();
	FVector CamLoc = FVector(Talk.X, Talk.Y, HunkStandLocation.Z - 92.f + 160.f) - Dir * (bMalcolm ? 80.f : 40.f);

	// Small rooms: if a wall is between his face and the ideal spot, slide the camera in front of the wall.
	FHitResult Hit;
	FCollisionQueryParams Q(SCENE_QUERY_STAT(FixHimDialogueCam), false, this);
	if (Hunk)
	{
		Q.AddIgnoredActor(Hunk);
	}
	// Rosie stands between the face and the camera; her capsule must not push the camera toward him.
	if (APlayerController* Player = GetWorld()->GetFirstPlayerController())
	{
		Q.AddIgnoredActor(Player->GetPawn());
	}
	if (GetWorld()->SweepSingleByChannel(Hit, Head, CamLoc, FQuat::Identity, ECC_Visibility, FCollisionShape::MakeSphere(18.f), Q))
	{
		CamLoc = Hit.Location + (Head - CamLoc).GetSafeNormal() * 10.f;
	}
	// Aim a little below the face so he sits in the top 3/4 of the frame, above the dialogue box.
	// Aim at Malcolm's upper torso: his face belongs in the upper third, clear of the dialogue panel.
	const FVector Aim = Head + FVector(0.f, 0.f, bMalcolm ? -30.f : -38.f);
	DialogueCamera->SetWorldLocationAndRotation(CamLoc, (Aim - CamLoc).Rotation());
}

void AFixHimMalady::BuildBrokenFx()
{
	const FVector O = FxOffset;
	switch (Style)
	{
	case EMaladyStyle::Leak:
	{
		Drop = FixHim::Assets::AddShape(this, Root, TEXT("sphere"), O, FVector(3.5f, 3.5f, 5.f), FLinearColor(0.5f, 0.8f, 1.f));
		FixHim::Assets::PaintComponent(Drop, FLinearColor(0.5f, 0.8f, 1.f), FLinearColor(0.1f, 0.25f, 0.4f));
		BrokenFx.Add(Drop);
		const float FloorZ = -GetActorLocation().Z + 0.6f;
		UStaticMeshComponent* Puddle = FixHim::Assets::AddShape(this, Root, TEXT("cylinder"), FVector(O.X + 25.f, O.Y, FloorZ), FVector(120.f, 90.f, 0.6f), FLinearColor(0.4f, 0.65f, 0.9f));
		if (UMaterialInstanceDynamic* MID = FixHim::Assets::MakeTranslucent(Puddle, FLinearColor(1.6f, 2.8f, 4.0f), 0.28f))
		{
			Puddle->SetMaterial(0, MID);
		}
		BrokenFx.Add(Puddle);
		break;
	}
	case EMaladyStyle::Mold:
	{
		TArray<AActor*> AttachedActors;
		GetAttachedActors(AttachedActors);
		if (AttachedActors.ContainsByPredicate([](const AActor* Actor)
			{ return Actor && Actor->ActorHasTag(TEXT("AuthoredMoldDamage")); }))
		{
			break;
		}
		FRandomStream Rng(GetTypeHash(HunkId) + 7);
		for (int32 i = 0; i < 14; ++i)
		{
			const FVector P = O + FVector(1.f, Rng.FRandRange(-85.f, 85.f), Rng.FRandRange(-70.f, 80.f));
			const float S = Rng.FRandRange(14.f, 48.f);
			const FLinearColor C = FMath::Lerp(FLinearColor(0.02f, 0.03f, 0.02f), FLinearColor(0.08f, 0.14f, 0.06f), Rng.FRand());
			BrokenFx.Add(FixHim::Assets::AddShape(this, Root, TEXT("sphere"), P, FVector(2.f, S, S * Rng.FRandRange(0.6f, 1.1f)), C));
		}
		break;
	}
	case EMaladyStyle::Wiring:
	{
		FxLight = NewObject<UPointLightComponent>(this);
		FxLight->SetupAttachment(Root);
		FxLight->SetRelativeLocation(O + FVector(15.f, 0.f, 0.f));
		FxLight->SetLightColor(FLinearColor(0.6f, 0.8f, 1.f));
		FxLight->SetAttenuationRadius(300.f);
		FxLight->SetCastShadows(false);
		FxLight->RegisterComponent();
		for (int32 i = 0; i < 6; ++i)
		{
			UStaticMeshComponent* Spark = FixHim::Assets::AddShape(this, Root, TEXT("cube"), O, FVector(1.2f, 1.2f, 4.f), FLinearColor(1.f, 0.9f, 0.4f));
			FixHim::Assets::PaintComponent(Spark, FLinearColor(1.f, 0.9f, 0.4f), FLinearColor(30.f, 22.f, 6.f));
			BrokenFx.Add(Spark);
		}
		break;
	}
	case EMaladyStyle::Tile:
	case EMaladyStyle::Glow:
	default:
		break;
	}
}

void AFixHimMalady::RefreshRepairState()
{
	const UFixHimSaveSubsystem* Save = UFixHimSaveSubsystem::Get(this);
	const FHunkProgress* P = Save ? Save->FindHunk(HunkId) : nullptr;
	const bool bWasRepaired = bRepaired;
	bRepaired = P && P->bFixed;
	// A repair that happens while playing (not just loaded from the save): celebrate a good ending, sigh at a bad one.
	if (bRepairKnown && bRepaired && !bWasRepaired)
	{
		FixHim::SfxAt(this, P->Ending.EndsWith(TEXT("_success")) ? "FixComplete" : "RepairFail", GetActorLocation());
	}
	bRepairKnown = true;

	for (UStaticMeshComponent* Fx : BrokenFx)
	{
		if (Fx)
		{
			Fx->SetVisibility(!bRepaired);
		}
	}
	if (FxLight)
	{
		FxLight->SetVisibility(!bRepaired);
	}
	// Level-authored nonblocking damage follows the same repair state as FX.
	TArray<AActor*> AttachedActors;
	GetAttachedActors(AttachedActors);
	for (AActor* Attached : AttachedActors)
	{
		if (Attached && Attached->ActorHasTag(TEXT("RepairDamage")))
		{
			Attached->SetActorHiddenInGame(bRepaired);
		}
	}
}

void AFixHimMalady::Tick(float DeltaSeconds)
{
	Super::Tick(DeltaSeconds);
	FxTime += DeltaSeconds;

	// Subtle breathing glow: a little stronger while broken, slower and softer once repaired.
	const float Pulse = 0.5f + 0.5f * FMath::Sin(FxTime * (bRepaired ? 1.2f : 1.8f));
	const float Strength = bRepaired ? 0.15f + 0.2f * Pulse : 0.4f + 0.7f * Pulse;
	if (BodyMID)
	{
		BodyMID->SetVectorParameterValue(TEXT("Emissive"), GlowColor * Strength);
	}
	if (ShineMID)
	{
		ShineMID->SetScalarParameterValue(TEXT("Glow"), bRepaired ? 0.12f + 0.12f * Pulse : 0.25f + 0.3f * Pulse);
	}
	GlowLight->SetIntensity((bRepaired ? 150.f : 450.f) * (0.6f + 0.8f * Pulse));

	if (!bRepaired)
	{
		TickBrokenFx(DeltaSeconds);
	}
}

void AFixHimMalady::TickBrokenFx(float DeltaSeconds)
{
	switch (Style)
	{
	case EMaladyStyle::Leak:
		if (Drop)
		{
			const float Period = 1.1f;
			const float T = FMath::Fmod(FxTime, Period) / Period;
			const float FallDist = FMath::Max(10.f, GetActorLocation().Z - 2.f + FxOffset.Z);
			const float Fall = T < 0.35f ? 0.f : FMath::Square((T - 0.35f) / 0.65f) * FallDist;
			Drop->SetRelativeLocation(FxOffset - FVector(0.f, 0.f, Fall));
			Drop->SetRelativeScale3D(FVector(0.035f, 0.035f, 0.05f) * (T < 0.35f ? FMath::Lerp(0.3f, 1.f, T / 0.35f) : 1.f));
		}
		break;
	case EMaladyStyle::Wiring:
	{
		const bool bBurst = FMath::Fmod(FxTime, 1.7f) < 0.35f;
		for (UStaticMeshComponent* Spark : BrokenFx)
		{
			if (!Spark)
			{
				continue;
			}
			Spark->SetVisibility(bBurst && FMath::FRand() > 0.3f);
			if (bBurst)
			{
				Spark->SetRelativeLocation(FxOffset + FVector(FMath::FRandRange(4.f, 30.f), FMath::FRandRange(-18.f, 18.f), FMath::FRandRange(-12.f, 18.f)));
				Spark->SetRelativeRotation(FRotator(FMath::FRandRange(0.f, 360.f), FMath::FRandRange(0.f, 360.f), 0.f));
			}
		}
		if (FxLight)
		{
			FxLight->SetIntensity(bBurst ? FMath::FRandRange(800.f, 3000.f) : 0.f);
		}
		break;
	}
	default:
		break;
	}
}

void AFixHimMalady::Interact(AFixHimPlayerController* Player)
{
	if (Player && Hunk)
	{
		PlayInteractSfx();
		Player->BeginEncounter(this);
	}
}

FName AFixHimMalady::DefaultInteractSfx(bool bNowOn) const
{
	FName Cue = TEXT("Interact");
	switch (Style)
	{
	case EMaladyStyle::Leak: Cue = TEXT("PipeClank"); break;
	case EMaladyStyle::Wiring: Cue = TEXT("Zap"); break;
	case EMaladyStyle::Mold: Cue = TEXT("Squelch"); break;
	case EMaladyStyle::Tile: Cue = TEXT("TileTap"); break;
	default: break;
	}
	const UFixHimSfxSubsystem* Sfx = UFixHimSfxSubsystem::Get(this);
	return !Sfx || Sfx->Has(Cue) ? Cue : FName(TEXT("Interact"));
}

bool AFixHimMalady::CanInteract() const
{
	if (!Super::CanInteract())
	{
		return false;
	}
	const UWorld* World = GetWorld();
	if (World && World->GetTimeSeconds() < InteractLockedUntil)
	{
		return false;
	}
	return !(Hunk && Hunk->IsTransitioning());
}

void AFixHimMalady::LockInteraction(float Seconds)
{
	if (const UWorld* World = GetWorld())
	{
		InteractLockedUntil = FMath::Max(InteractLockedUntil, World->GetTimeSeconds() + Seconds);
	}
}

FText AFixHimMalady::GetPrompt() const
{
	const UFixHimSaveSubsystem* Save = UFixHimSaveSubsystem::Get(this);
	const FHunkProgress* P = Save ? Save->FindHunk(HunkId) : nullptr;
	if (!P || !P->bMet)
	{
		return NSLOCTEXT("FixHim", "InspectPrompt", "Inspect");
	}
	return FText::Format(NSLOCTEXT("FixHim", "TalkPrompt", "Talk to {0}"), HunkName);
}

void AFixHimMalady::SummonHunk()
{
	// Re-frame now rather than only at BeginPlay: doors (e.g. a closet hiding the fixture) may have been
	// opened since, and the wall-avoidance sweep should see the room as it is for this encounter.
	if (bAutoFrameCamera)
	{
		FrameCamera();
	}
	if (Hunk)
	{
		Hunk->SetActorLocationAndRotation(HunkStandLocation, HunkSpawn->GetComponentRotation());
		// Grow out of the glowing fixture itself.
		const FVector From = Body && Body->GetStaticMesh() ? Body->Bounds.Origin : GetActorLocation();
		Hunk->Appear(From);
	}
}

void AFixHimMalady::DismissHunk(bool bBubblePop)
{
	if (Hunk)
	{
		Hunk->Disappear(bBubblePop);
	}
}

bool AFixHimMalady::IsHunkPresent() const
{
	return Hunk && Hunk->IsPresent();
}
