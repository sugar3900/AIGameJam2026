// I Can Fix Him - AI Game Jam 2026

#include "World/FixHimInteractable.h"
#include "Core/FixHimAssets.h"
#include "Core/FixHimSettings.h"
#include "Audio/FixHimSfxSubsystem.h"
#include "Components/StaticMeshComponent.h"
#include "Components/PointLightComponent.h"
#include "Components/MaterialBillboardComponent.h"
#include "Engine/StaticMesh.h"
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

	Sparkles = CreateDefaultSubobject<USceneComponent>(TEXT("Sparkles"));
	Sparkles->SetupAttachment(Root);
}

void AFixHimInteractable::OnConstruction(const FTransform& Transform)
{
	Super::OnConstruction(Transform);
	ApplyLook();
}

void AFixHimInteractable::BeginPlay()
{
	Super::BeginPlay();
	ApplyLook();
	BuildOutline();
	BuildSparkles();
	ToggleAlpha = bIsOn ? 1.f : 0.f;
	ApplyToggleAlpha(ToggleAlpha);
	Age = FMath::FRand() * 10.f;
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
	if (RevealPart && RevealPart->GetStaticMesh())
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
	// Inverted-hull outline: a slightly larger copy of each body mesh rendered with reverse culling
	// in an unlit colour. Works well for the convex primitives the apartment is built from.
	TArray<UStaticMeshComponent*> Sources;
	GetComponents<UStaticMeshComponent>(Sources);
	for (UStaticMeshComponent* Src : Sources)
	{
		if (!Src || !Src->GetStaticMesh() || Src == RevealPart || OutlineShells.Contains(Src) || !Src->IsVisible())
		{
			continue;
		}
		if (Src != Body && !Src->IsAttachedTo(Pivot))
		{
			continue;
		}

		const FBox LocalBox = Src->GetStaticMesh()->GetBoundingBox();
		const FVector Size = LocalBox.GetSize() * Src->GetRelativeScale3D().GetAbs();
		const FVector Center = LocalBox.GetCenter();
		const FVector ScaleMul(
			Size.X > KINDA_SMALL_NUMBER ? 1.f + 2.f * OutlineThickness / Size.X : 1.f,
			Size.Y > KINDA_SMALL_NUMBER ? 1.f + 2.f * OutlineThickness / Size.Y : 1.f,
			Size.Z > KINDA_SMALL_NUMBER ? 1.f + 2.f * OutlineThickness / Size.Z : 1.f);

		UStaticMeshComponent* Shell = NewObject<UStaticMeshComponent>(this);
		Shell->SetStaticMesh(Src->GetStaticMesh());
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

void AFixHimInteractable::BuildSparkles()
{
	UMaterialInterface* SparkleMat = UFixHimSettings::Get()->SparkleMaterial.LoadSynchronous();
	if (!bSparkle || !SparkleMat || !Body || !Body->GetStaticMesh())
	{
		return;
	}
	SparkleMID = UMaterialInstanceDynamic::Create(SparkleMat, this);
	SparkleMID->SetVectorParameterValue(TEXT("Color"), SparkleColor);

	const FBoxSphereBounds B = Body->CalcBounds(Body->GetComponentTransform());
	Sparkles->SetWorldLocation(B.Origin);
	const float Radius = FMath::Clamp(FMath::Max(B.BoxExtent.X, B.BoxExtent.Y) * 0.9f, 15.f, 70.f);
	const float Size = FMath::Clamp(B.SphereRadius * 0.35f, 14.f, 26.f);

	// Three twinkling sprites at different heights around the object.
	for (int32 i = 0; i < 3; ++i)
	{
		UMaterialBillboardComponent* Sprite = NewObject<UMaterialBillboardComponent>(this);
		Sprite->SetupAttachment(Sparkles);
		const float Angle = (i / 3.f) * 2.f * PI;
		Sprite->SetRelativeLocation(FVector(FMath::Cos(Angle) * Radius, FMath::Sin(Angle) * Radius, (i - 1) * B.BoxExtent.Z * 0.6f));
		Sprite->SetCollisionEnabled(ECollisionEnabled::NoCollision);
		Sprite->SetCastShadow(false);
		Sprite->AddElement(SparkleMID, nullptr, false, Size * (1.f - 0.15f * i), Size * (1.f - 0.15f * i), nullptr);
		Sprite->RegisterComponent();
	}
}

void AFixHimInteractable::Tick(float DeltaSeconds)
{
	Super::Tick(DeltaSeconds);
	Age += DeltaSeconds;

	const float Target = bIsOn ? 1.f : 0.f;
	if (!FMath::IsNearlyEqual(ToggleAlpha, Target))
	{
		ToggleAlpha = FMath::FInterpConstantTo(ToggleAlpha, Target, DeltaSeconds, 3.5f);
		ApplyToggleAlpha(ToggleAlpha);
	}

	if (Sparkles)
	{
		// Slow orbit; the material twinkles each sprite on its own phase.
		Sparkles->SetRelativeRotation(FRotator(0.f, Age * 40.f, 0.f));
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
		break;
	case EInteractToggle::Slide:
		Pivot->SetRelativeLocation(ToggleOffset * Smooth);
		break;
	case EInteractToggle::Rotate:
		Pivot->SetRelativeRotation(ToggleRotation * Smooth);
		break;
	case EInteractToggle::Reveal:
		RevealPart->SetVisibility(Alpha > 0.05f);
		break;
	default:
		break;
	}
}

void AFixHimInteractable::Interact(AFixHimPlayerController* Player)
{
	if (Toggle != EInteractToggle::None)
	{
		SetOn(!bIsOn);
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
	// The prompts are authored per object in Tools/Editor/build_apartment.py ("Turn on stove", "Lift the lid", ...).
	const FString Label = (GetActorNameOrLabel() + PromptOff.ToString()).ToLower();
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
	bIsOn = bInOn;
	if (bInstant)
	{
		ToggleAlpha = bIsOn ? 1.f : 0.f;
		ApplyToggleAlpha(ToggleAlpha);
	}
}

FText AFixHimInteractable::GetPrompt() const
{
	return bIsOn ? PromptOn : PromptOff;
}

void AFixHimInteractable::SetHovered(bool bInHovered)
{
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
