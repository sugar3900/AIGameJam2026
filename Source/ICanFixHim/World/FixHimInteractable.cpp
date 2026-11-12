// I Can Fix Him - AI Game Jam 2026

#include "World/FixHimInteractable.h"
#include "Core/FixHimAssets.h"
#include "Core/FixHimSettings.h"
#include "Audio/FixHimSfxSubsystem.h"
#include "Components/StaticMeshComponent.h"
#include "Components/PointLightComponent.h"
#include "Engine/StaticMesh.h"
#include "Engine/Light.h"
#include "Components/LightComponent.h"
#include "EngineUtils.h"
#include "Kismet/GameplayStatics.h"
#include "Player/FixHimPlayerController.h"
#include "Materials/MaterialInstanceDynamic.h"

AFixHimInteractable::AFixHimInteractable()
{
	PrimaryActorTick.bCanEverTick = true;

	Root = CreateDefaultSubobject<USceneComponent>(TEXT("Root"));
	SetRootComponent(Root);

	Pivot = CreateDefaultSubobject<USceneComponent>(TEXT("Pivot"));
	Pivot->SetupAttachment(Root);

	Body = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("Body"));
	Body->SetupAttachment(Pivot);
	Body->SetCollisionProfileName(TEXT("BlockAll"));

	RevealPart = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("RevealPart"));
	RevealPart->SetupAttachment(Root);
	RevealPart->SetCollisionEnabled(ECollisionEnabled::NoCollision);
	RevealPart->SetCastShadow(false);
	RevealPart->SetVisibility(false);

	Light = CreateDefaultSubobject<UPointLightComponent>(TEXT("Light"));
	Light->SetupAttachment(Root);
	Light->SetIntensity(0.f);
	Light->SetAttenuationRadius(600.f);
	Light->SetLightColor(FLinearColor(1.f, 0.82f, 0.62f));
	Light->SetCastShadows(false);
	Light->SetVisibility(false);
}

void AFixHimInteractable::OnConstruction(const FTransform& Transform)
{
	Super::OnConstruction(Transform);
	ApplyLook();
}

void AFixHimInteractable::BeginPlay()
{
	Super::BeginPlay();
	Age = FMath::FRand() * 10.f;
	ApplyLook();
	BuildOutline();
	BuildShine();
	BuildGlow();
	SetOnLocal(bIsOn, true);
	InitFill();
}

void AFixHimInteractable::InitFill()
{
	bFillReady = false;
	if (!IsValid(FillSurface) || FillSurface == this)
	{
		return;
	}
	if (USceneComponent* SurfaceRoot = FillSurface->GetRootComponent())
	{
		SurfaceRoot->SetMobility(EComponentMobility::Movable);
	}
	FillFullLocation = FillSurface->GetActorLocation();
	{
		// the surface itself (top of the authored water mesh), not the actor origin, is where the stream ends
		FVector Origin, Extent;
		FillSurface->GetActorBounds(false, Origin, Extent, true);
		FillFullSurfaceZ = Origin.Z + Extent.Z;
	}
	FillFullScale = FillSurface->GetActorScale3D();
	FillFollowerFull.Reset();
	for (AActor* Actor : FillFollowers)
	{
		if (IsValid(Actor) && Actor->GetRootComponent()) Actor->GetRootComponent()->SetMobility(EComponentMobility::Movable);
		FillFollowerFull.Add(IsValid(Actor) ? Actor->GetActorLocation() : FVector::ZeroVector);
	}
	RevealTopZ = RevealBottomZ = 0.f;
	if (bFillTrimsReveal && RevealPart && RevealPart->GetStaticMesh())
	{
		RevealRelLocation = RevealPart->GetRelativeLocation();
		RevealRelScale = RevealPart->GetRelativeScale3D();
		// The stream runs along its mesh's local Z (it may lean a little, like a spout's arc): its top and bottom are
		// the mesh bounds' end-cap centres.
		const FBox Local = RevealPart->GetStaticMesh()->GetBoundingBox();
		const FTransform& Xf = RevealPart->GetComponentTransform();
		RevealTopToPivot = Xf.TransformPosition(FVector(Local.GetCenter().X, Local.GetCenter().Y, Local.Max.Z)) - Xf.GetLocation();
		RevealTopZ = Xf.GetLocation().Z + RevealTopToPivot.Z;
		RevealBottomZ = Xf.TransformPosition(FVector(Local.GetCenter().X, Local.GetCenter().Y, Local.Min.Z)).Z;
	}
	FillLevel = bIsOn ? 1.f : 0.f;
	bFillReady = true;
	ApplyFill();
}

void AFixHimInteractable::ApplyFill()
{
	if (!bFillReady || !IsValid(FillSurface))
	{
		return;
	}
	const FVector Down(0.f, 0.f, (1.f - FillLevel) * FillDepth);
	const FVector2D S = FMath::Lerp(FillEmptyScale, FVector2D(1.f, 1.f), FillLevel);
	FillSurface->SetActorLocation(FillFullLocation - Down);
	FillSurface->SetActorScale3D(FVector(FillFullScale.X * S.X, FillFullScale.Y * S.Y, FillFullScale.Z));
	FillSurface->SetActorHiddenInGame(FillLevel < 0.01f);
	for (int32 Index = 0; Index < FillFollowers.Num(); ++Index)
	{
		if (IsValid(FillFollowers[Index]) && FillFollowerFull.IsValidIndex(Index))
		{
			FillFollowers[Index]->SetActorLocation(FillFollowerFull[Index] - Down);
		}
	}
	if (RevealTopZ > RevealBottomZ + 1.f)
	{
		// The stream keeps its top at the spout and ends on the surface: shorten it along its axis about its pivot,
		// then move it back so the top stays put.
		const float Bottom = FMath::Clamp(FillFullSurfaceZ - Down.Z, RevealBottomZ, RevealTopZ - 1.f);
		const float F = (RevealTopZ - Bottom) / (RevealTopZ - RevealBottomZ);
		RevealPart->SetRelativeScale3D(FVector(RevealRelScale.X, RevealRelScale.Y, RevealRelScale.Z * F));
		const FVector Shift = GetActorTransform().InverseTransformVectorNoScale(RevealTopToPivot * (1.f - F));
		RevealPart->SetRelativeLocation(RevealRelLocation + Shift);
	}
}

void AFixHimInteractable::BuildGlow()
{
	ExtraLights.Reset();
	ExtraLightOnValues.Reset();
	for (const TSoftObjectPtr<AActor>& Soft : ToggleLightActors)
	{
		if (AActor* Actor = Soft.Get())
		{
			TArray<ULightComponent*> Lights;
			Actor->GetComponents(Lights);
			for (ULightComponent* L : Lights)
			{
				ExtraLights.Add(L);
				ExtraLightOnValues.Add(L->Intensity);
			}
		}
	}
	GlowMIDs.Reset();
	GlowOnValues.Reset();
	for (const TSoftObjectPtr<AActor>& Soft : GlowActors)
	{
		AActor* Actor = Soft.Get();
		if (!Actor)
		{
			continue;
		}
		TArray<UStaticMeshComponent*> Meshes;
		Actor->GetComponents(Meshes);
		for (UStaticMeshComponent* Mesh : Meshes)
		{
			for (int32 Index = 0; Index < Mesh->GetNumMaterials(); ++Index)
			{
				UMaterialInterface* Material = Mesh->GetMaterial(Index);
				float OnValue = 0.f;
				if (Material && Material->GetScalarParameterValue(FHashedMaterialParameterInfo(GlowParam), OnValue))
				{
					GlowMIDs.Add(Mesh->CreateAndSetMaterialInstanceDynamic(Index));
					GlowOnValues.Add(OnValue);
				}
			}
		}
	}
}

void AFixHimInteractable::ApplyLook()
{
	if (Body && Body->GetStaticMesh() && !bUseAuthoredBodyMaterials)
	{
		BodyMID = FixHim::Assets::MakeFlat(this, BodyColor);
		if (BodyMID)
		{
			for (int32 i = 0; i < FMath::Max(1, Body->GetNumMaterials()); ++i)
			{
				Body->SetMaterial(i, BodyMID);
			}
		}
	}
	RevealMIDs.Reset();
	if (bUseAuthoredRevealMaterial)
	{
		auto CacheMaterials = [this](UStaticMeshComponent* Mesh)
		{
			if (!Mesh || !Mesh->GetStaticMesh()) return;
			for (int32 Slot = 0; Slot < Mesh->GetNumMaterials(); ++Slot)
			{
				// Reuse an existing MID when construction runs again; avoid nested instances.
				UMaterialInstanceDynamic* MID = Cast<UMaterialInstanceDynamic>(Mesh->GetMaterial(Slot));
				if (!MID) MID = Mesh->CreateDynamicMaterialInstance(Slot);
				if (MID) RevealMIDs.AddUnique(MID);
			}
		};
		CacheMaterials(RevealPart);
		for (AActor* Actor : RevealActors)
		{
			if (!IsValid(Actor) || Actor == this) continue;
			TArray<UStaticMeshComponent*> Meshes;
			Actor->GetComponents(Meshes);
			for (UStaticMeshComponent* Mesh : Meshes) CacheMaterials(Mesh);
		}
	}
	else if (RevealPart && RevealPart->GetStaticMesh())
	{
		if (UMaterialInstanceDynamic* MID = FixHim::Assets::MakeTranslucent(this, RevealColor, RevealOpacity))
		{
			RevealPart->SetMaterial(0, MID);
		}
	}
	if (Light)
	{
		Light->SetVisibility(Toggle == EInteractToggle::Light);
	}
}

void AFixHimInteractable::BuildOutline()
{
	if (!bEnabled || !bHoverOutline)
	{
		return;
	}
	// Inverted-hull outline: a slightly larger copy of each body mesh rendered with reverse culling
	// in an unlit colour. Works well for the convex primitives the apartment is built from.
	TArray<UStaticMeshComponent*> Sources;
	GetComponents<UStaticMeshComponent>(Sources);
	for (UStaticMeshComponent* Src : Sources)
	{
		if (!Src || !Src->GetStaticMesh() || IsRevealMesh(Src) || OutlineShells.Contains(Src) || !Src->IsVisible())
		{
			continue;
		}
		if (Src != Body && !Src->IsAttachedTo(Pivot))
		{
			continue;
		}

		UStaticMesh* ShellMesh = Src->GetStaticMesh();
		if (Src == Body && OutlineMeshOverride) ShellMesh = OutlineMeshOverride.Get();
		const FBox LocalBox = ShellMesh->GetBoundingBox();
		const FVector Size = LocalBox.GetSize() * Src->GetRelativeScale3D().GetAbs();
		const FVector Center = LocalBox.GetCenter();
		const FVector ScaleMul(
			Size.X > KINDA_SMALL_NUMBER ? 1.f + 2.f * OutlineThickness / Size.X : 1.f,
			Size.Y > KINDA_SMALL_NUMBER ? 1.f + 2.f * OutlineThickness / Size.Y : 1.f,
			Size.Z > KINDA_SMALL_NUMBER ? 1.f + 2.f * OutlineThickness / Size.Z : 1.f);

		UStaticMeshComponent* Shell = NewObject<UStaticMeshComponent>(this);
		Shell->SetStaticMesh(ShellMesh);
		Shell->SetupAttachment(Src);
		// Scale about the mesh bounds centre rather than its pivot.
		Shell->SetRelativeScale3D(ScaleMul);
		Shell->SetRelativeLocation(Center * (FVector::OneVector - ScaleMul));
		Shell->SetCollisionEnabled(ECollisionEnabled::NoCollision);
		Shell->SetCastShadow(false);
		Shell->SetReverseCulling(true);
		Shell->SetVisibility(false);
		Shell->RegisterComponent();
		FixHim::Assets::PaintComponent(Shell, FLinearColor::Black, OutlineColor * 14.f);
		OutlineShells.Add(Shell);
	}
}

void AFixHimInteractable::BuildShine()
{
	if (!bEnabled)
	{
		return;
	}
	UMaterialInterface* ShineMat = UFixHimSettings::Get()->ShineMaterial.LoadSynchronous();
	if (!ShineMat)
	{
		return;
	}
	ShineMID = UMaterialInstanceDynamic::Create(ShineMat, this);
	ShineMID->SetVectorParameterValue(TEXT("Color"), ShineColor);
	ShineMID->SetScalarParameterValue(TEXT("Sweep"), -1.f);
	ShineMID->SetScalarParameterValue(TEXT("ShineStrength"), ShineStrength);
	ShineMID->SetScalarParameterValue(TEXT("Glow"), 0.f);

	// One overlay for every visible mesh that moves with the body, with bounds covering all of them so a single
	// shine band crosses the whole object (a cabinet and its door, a lamp and its shade) in one sweep.
	TArray<UStaticMeshComponent*> Meshes;
	GetComponents<UStaticMeshComponent>(Meshes);
	FBox Box(ForceInit);
	TArray<UStaticMeshComponent*> Targets;
	for (UStaticMeshComponent* Mesh : Meshes)
	{
		if (!Mesh || !Mesh->GetStaticMesh() || IsRevealMesh(Mesh) || OutlineShells.Contains(Mesh) || !Mesh->IsVisible())
		{
			continue;
		}
		if (Mesh != Body && !Mesh->IsAttachedTo(Pivot))
		{
			continue;
		}
		Box += Mesh->Bounds.GetBox();
		Targets.Add(Mesh);
	}
	if (Targets.IsEmpty())
	{
		return;
	}
	const FBoxSphereBounds Bounds(Box);
	ShineMID->SetVectorParameterValue(TEXT("Bounds"), FLinearColor(Bounds.Origin.X, Bounds.Origin.Y, Bounds.Origin.Z, Bounds.SphereRadius));
	for (UStaticMeshComponent* Mesh : Targets)
	{
		Mesh->SetOverlayMaterial(ShineMID);
	}
	NextShineAt = Age + FMath::FRandRange(0.3f, ShineInterval.Y);
}

void AFixHimInteractable::Tick(float DeltaSeconds)
{
	Super::Tick(DeltaSeconds);
	Age += DeltaSeconds;

	if (bAutoCloseOnWalkAway && bIsOn && (Toggle == EInteractToggle::Slide || Toggle == EInteractToggle::Rotate))
	{
		const AFixHimPlayerController* PC = Cast<AFixHimPlayerController>(UGameplayStatics::GetPlayerController(this, 0));
		if (PC && PC->GetState() == EFixHimState::Playing && PC->GetPawn())
		{
			// Measure from the closed body's center, so the moving door cannot change the threshold.
			const FVector Center = Body->GetStaticMesh()
				? Body->GetRelativeTransform().TransformPosition(Body->GetStaticMesh()->GetBounds().Origin)
				: FVector::ZeroVector;
			const FVector ClosedCenter = GetActorTransform().TransformPosition(Center);
			const float Distance = FVector::Dist2D(PC->GetPawn()->GetActorLocation(), ClosedCenter);
			ClosestOpenDistance = FMath::Min(ClosestOpenDistance, Distance);
			// Allow normal movement nearby, then close after a 60 cm retreat. Opening at long
			// interaction range must still work without immediately snapping the door shut.
			const float Range = FMath::Max(180.f, ClosestOpenDistance + 60.f);
			if (Distance > Range)
			{
				SetOn(false);
				PlayInteractSfx();
			}
		}
	}

	if (bFillReady)
	{
		// Fill while the water runs; drain slowly once it is off (DrainSeconds 0 keeps the water).
		const float Before = FillLevel;
		if (bIsOn)
		{
			FillLevel = FMath::Min(1.f, FillLevel + DeltaSeconds / FMath::Max(FillSeconds, 0.1f));
		}
		else if (DrainSeconds > 0.f)
		{
			FillLevel = FMath::Max(0.f, FillLevel - DeltaSeconds / DrainSeconds);
		}
		if (FillLevel != Before)
		{
			ApplyFill();
		}
	}

	const float Target = bIsOn ? 1.f : 0.f;
	if (!FMath::IsNearlyEqual(ToggleAlpha, Target))
	{
		ToggleAlpha = FMath::FInterpConstantTo(ToggleAlpha, Target, DeltaSeconds, FMath::Max(ToggleSpeed, 0.001f));
		ApplyToggleAlpha(ToggleAlpha);
	}

	if (PullAge >= 0.f)
	{
		PullAge += DeltaSeconds;
		const float Phase = PullAge / FMath::Max(PullSeconds, 0.01f);
		if (Phase >= 1.f)
		{
			PullAge = -1.f;
			Pivot->SetRelativeLocation(FVector::ZeroVector);
		}
		else
		{
			Pivot->SetRelativeLocation(PullOffset * FMath::Sin(PI * Phase));
		}
	}

	if (ShineMID && bShine && bEnabled && bInteractionShineEnabled)
	{
		// A shine takes ShineDuration to cross the object, then the next one is a few seconds away.
		constexpr float ShineDuration = 1.4f;
		const float Progress = (Age - NextShineAt) / ShineDuration;
		if (Progress >= 0.f && Progress <= 1.f)
		{
			ShineMID->SetScalarParameterValue(TEXT("Sweep"), Progress);
		}
		else if (Progress > 1.f)
		{
			ShineMID->SetScalarParameterValue(TEXT("Sweep"), -1.f);
			NextShineAt = Age + FMath::FRandRange(ShineInterval.X, ShineInterval.Y);
		}
	}
}

void AFixHimInteractable::SetInteractionShineEnabled(bool bAllow)
{
	if (bInteractionShineEnabled == bAllow)
	{
		return;
	}
	bInteractionShineEnabled = bAllow;
	if (ShineMID)
	{
		ShineMID->SetScalarParameterValue(TEXT("Sweep"), -1.f);
	}
	// Resume with a fresh delay, rather than continuing a sweep left over from before the conversation.
	NextShineAt = Age + FMath::FRandRange(ShineInterval.X, ShineInterval.Y);
}

bool AFixHimInteractable::IsRevealMesh(const UStaticMeshComponent* Mesh) const
{
	if (Mesh == RevealPart) return true;
	return Mesh && RevealActors.ContainsByPredicate([Mesh](const TObjectPtr<AActor>& Actor)
	{
		return Actor.Get() == Mesh->GetOwner();
	});
}

void AFixHimInteractable::ApplyRevealAlpha(float Alpha)
{
	const bool bVisible = Alpha > 0.05f;
	RevealPart->SetVisibility(bVisible);
	for (AActor* Actor : RevealActors)
	{
		if (!IsValid(Actor) || Actor == this) continue;
		Actor->SetActorHiddenInGame(!bVisible);
		TArray<UStaticMeshComponent*> Meshes;
		Actor->GetComponents(Meshes);
		for (UStaticMeshComponent* Mesh : Meshes) Mesh->SetVisibility(bVisible);
	}
	if (bUseAuthoredRevealMaterial)
	{
		for (UMaterialInstanceDynamic* MID : RevealMIDs)
		{
			if (IsValid(MID)) MID->SetScalarParameterValue(TEXT("RevealAlpha"), Alpha);
		}
	}
}

void AFixHimInteractable::ApplyToggleAlpha(float Alpha)
{
	const float Smooth = FMath::SmoothStep(0.f, 1.f, Alpha);
	switch (Toggle)
	{
	case EInteractToggle::Light:
		if (Light)
		{
			Light->SetIntensity(LightIntensityOn * Smooth);
		}
		if (BodyMID)
		{
			BodyMID->SetVectorParameterValue(TEXT("Emissive"), OnEmissive * Smooth);
		}
		for (int32 Index = 0; Index < ExtraLights.Num(); ++Index)
		{
			if (ExtraLights[Index])
			{
				ExtraLights[Index]->SetIntensity(ExtraLightOnValues[Index] * Smooth);
			}
		}
		for (int32 Index = 0; Index < GlowMIDs.Num(); ++Index)
		{
			if (GlowMIDs[Index])
			{
				GlowMIDs[Index]->SetScalarParameterValue(GlowParam, GlowOnValues[Index] * Smooth);
			}
		}
		// Optional lit art (e.g. a gas flame) follows the toggle, including external reveal art.
		if ((RevealPart && RevealPart->GetStaticMesh()) || !RevealActors.IsEmpty())
		{
			ApplyRevealAlpha(Alpha);
		}
		break;
	case EInteractToggle::Slide:
		Pivot->SetRelativeLocation(ToggleOffset * Smooth);
		break;
	case EInteractToggle::Rotate:
		Pivot->SetRelativeRotation(ToggleRotation * Smooth);
		break;
	case EInteractToggle::Reveal:
		ApplyRevealAlpha(Alpha);
		break;
	default:
		break;
	}
}

void AFixHimInteractable::Interact(AFixHimPlayerController* Player)
{
	if (!CanInteract())
	{
		return;
	}
	if (Toggle != EInteractToggle::None)
	{
		SetOn(!bIsOn);
	}
	if (bPullOnClick && (Toggle == EInteractToggle::Light || Toggle == EInteractToggle::None))
	{
		PullAge = 0.f;
	}
	PlayInteractSfx();
}

FName AFixHimInteractable::GetInteractSfx(bool bNowOn) const
{
	const FName Explicit = bNowOn || InteractSfxOff.IsNone() ? InteractSfx : InteractSfxOff;
	if (!Explicit.IsNone())
	{
		return Explicit;
	}
	return DefaultInteractSfx(bNowOn);
}

FName AFixHimInteractable::DefaultInteractSfx(bool bNowOn) const
{
	// Recorded household cues picked from the actor label and its prompts (authored per object in
	// Tools/Editor/build_apartment.py: "Turn on lamp", "Open fridge", "Lift the lid"...). Prompts are matched too because
	// actor labels don't exist in cooked builds. A cue that isn't imported falls back to the generic sound below.
	const FString Label = (GetActorNameOrLabel() + TEXT(" | ") + PromptOff.ToString() + TEXT(" | ") + PromptOn.ToString()).ToLower();
	struct FCue { const TCHAR* Keys[3]; const TCHAR* On; const TCHAR* Off; };
	static const FCue Cues[] =
	{
		{ { TEXT("lamp"), nullptr, nullptr }, TEXT("LampOn"), TEXT("LampOff") },
		{ { TEXT("turn on tv"), TEXT("tv |"), nullptr }, TEXT("TvOn"), TEXT("TvOff") },
		{ { TEXT("stove"), nullptr, nullptr }, TEXT("StoveIgnite"), TEXT("StoveOff") },
		{ { TEXT("fridge"), nullptr, nullptr }, TEXT("FridgeOpen"), TEXT("FridgeClose") },
		{ { TEXT("drawer"), nullptr, nullptr }, TEXT("DrawerOpen"), TEXT("DrawerClose") },
		{ { TEXT("wardrobe"), nullptr, nullptr }, TEXT("WardrobeOpen"), TEXT("WardrobeClose") },
		{ { TEXT("faucet"), TEXT("bath"), TEXT("water") }, TEXT("FaucetOn"), TEXT("FaucetOff") },
		{ { TEXT("toilet"), TEXT("lid"), nullptr }, TEXT("ToiletLidUp"), TEXT("ToiletLidDown") },
		{ { TEXT("go to bed"), nullptr, nullptr }, TEXT("BedRustle"), TEXT("BedRustle") },
	};
	const UFixHimSfxSubsystem* Sfx = UFixHimSfxSubsystem::Get(this);
	for (const FCue& Cue : Cues)
	{
		bool bMatch = false;
		for (const TCHAR* Key : Cue.Keys)
		{
			bMatch |= Key && Label.Contains(Key);
		}
		const FName Name(bNowOn ? Cue.On : Cue.Off);
		if (bMatch && (!Sfx || Sfx->Has(Name)))
		{
			return Name;
		}
	}

	switch (Toggle)
	{
	case EInteractToggle::Light:
		return bNowOn && Label.Contains(TEXT("stove")) ? FName("Sizzle") : FName(bNowOn ? "SwitchOn" : "SwitchOff");
	case EInteractToggle::Reveal:
		return bNowOn ? FName("WaterSplash") : FName("TapDrip");
	case EInteractToggle::Slide:
	case EInteractToggle::Rotate:
		if (Label.Contains(TEXT("lid")))
		{
			return bNowOn ? FName("Interact") : FName("CabinetClose");
		}
		return bNowOn ? FName("CabinetOpen") : FName("CabinetClose");
	default:
		return TEXT("Interact");
	}
}

void AFixHimInteractable::PlayInteractSfx()
{
	FixHim::SfxAt(this, GetInteractSfx(bIsOn), GetActorLocation());
}

void AFixHimInteractable::SetOn(bool bInOn, bool bInstant)
{
	SetOnLocal(bInOn, bInstant);
	if (!ToggleGroup.IsNone() && GetWorld())
	{
		for (TActorIterator<AFixHimInteractable> It(GetWorld()); It; ++It)
		{
			if (*It != this && It->ToggleGroup == ToggleGroup)
			{
				// Assign the requested state, never toggle recursively. Disabled light fixtures still receive it.
				It->SetOnLocal(bInOn, bInstant);
			}
		}
	}
}

void AFixHimInteractable::SetOnLocal(bool bInOn, bool bInstant)
{
	if (bInOn != bIsOn)
	{
		ClosestOpenDistance = TNumericLimits<float>::Max();
	}
	bIsOn = bInOn;
	if (bInstant)
	{
		ToggleAlpha = bIsOn ? 1.f : 0.f;
		ApplyToggleAlpha(ToggleAlpha);
	}
	for (const TSoftObjectPtr<ALight>& Target : ControlledLights)
	{
		if (ALight* TargetLight = Target.Get())
		{
			TargetLight->GetLightComponent()->SetVisibility(bIsOn);
		}
	}
}

FText AFixHimInteractable::GetPrompt() const
{
	return bIsOn ? PromptOn : PromptOff;
}

void AFixHimInteractable::SetHovered(bool bInHovered)
{
	bInHovered &= CanInteract();
	if (bHovered == bInHovered)
	{
		return;
	}
	bHovered = bInHovered;
	if (bHovered)
	{
		FixHim::Sfx(this, "Hover", 0.7f, 0.04f);
	}
	for (UStaticMeshComponent* Shell : OutlineShells)
	{
		if (Shell)
		{
			Shell->SetVisibility(bHovered);
		}
	}
}
