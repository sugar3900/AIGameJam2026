// I Can Fix Him - AI Game Jam 2026

#include "World/FixHimMorphInteractable.h"

#include "Components/SkeletalMeshComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Core/FixHimAssets.h"
#include "Engine/SkeletalMesh.h"
#include "Engine/StaticMesh.h"
#include "Materials/MaterialInstanceDynamic.h"
#include "UObject/ConstructorHelpers.h"

AFixHimMorphInteractable::AFixHimMorphInteractable()
{
	MorphMesh = CreateDefaultSubobject<USkeletalMeshComponent>(TEXT("MorphMesh"));
	// Under Pivot like any moving body part (Pivot never moves here), so outline code that walks the body's parts
	// picks it up.
	MorphMesh->SetupAttachment(Pivot);
	MorphMesh->SetCollisionEnabled(ECollisionEnabled::NoCollision);
	// No animation blueprint drives this mesh; keep the pose (and so the morph) refreshing while it is on screen.
	MorphMesh->VisibilityBasedAnimTickOption = EVisibilityBasedAnimTickOption::OnlyTickPoseWhenRendered;

	// Body is a hidden box sized each frame from ProxyOff/ProxyOn: it only catches the player's aim (and blocks
	// aiming through the shape, e.g. at the taps behind a drawn curtain). It never blocks movement.
	static ConstructorHelpers::FObjectFinder<UStaticMesh> Cube(TEXT("/Engine/BasicShapes/Cube.Cube"));
	if (Cube.Succeeded())
	{
		Body->SetStaticMesh(Cube.Object);
	}
	Body->SetVisibility(false);
	Body->SetCastShadow(false);
	Body->SetCollisionEnabled(ECollisionEnabled::QueryOnly);
	Body->SetCollisionResponseToAllChannels(ECR_Ignore);
	Body->SetCollisionResponseToChannel(ECC_Visibility, ECR_Block);
	bUseAuthoredBodyMaterials = true;

	// A slide with no offset: the base class toggles state and plays sounds; nothing moves rigidly.
	Toggle = EInteractToggle::Slide;
	ToggleOffset = FVector::ZeroVector;
	ToggleSpeed = 1.1f;
}

void AFixHimMorphInteractable::OnConstruction(const FTransform& Transform)
{
	Super::OnConstruction(Transform);
	// Show the authored state (and its proxy) in the editor too.
	ApplyToggleAlpha(bIsOn ? 1.f : 0.f);
}

void AFixHimMorphInteractable::BeginPlay()
{
	Super::BeginPlay();
	BuildMorphShine();
	ApplyToggleAlpha(ToggleAlpha);
}

void AFixHimMorphInteractable::BuildMorphShine()
{
	// The base shine only covers visible static meshes (none here: Body is the hidden proxy).
	if (!ShineMID || !MorphMesh || !MorphMesh->GetSkeletalMeshAsset())
	{
		return;
	}
	const FBoxSphereBounds Bounds((ProxyOn + ProxyOff).TransformBy(GetActorTransform()));
	ShineMID->SetVectorParameterValue(TEXT("Bounds"), FLinearColor(Bounds.Origin.X, Bounds.Origin.Y, Bounds.Origin.Z, Bounds.SphereRadius));
	MorphMesh->SetOverlayMaterial(ShineMID);
}

void AFixHimMorphInteractable::ApplyToggleAlpha(float Alpha)
{
	Super::ApplyToggleAlpha(Alpha);
	const float Smooth = FMath::SmoothStep(0.f, 1.f, Alpha);
	if (MorphMesh)
	{
		MorphMesh->SetMorphTarget(MorphTarget, Smooth, false);
	}
	if (Body)
	{
		const FVector Min = FMath::Lerp(ProxyOff.Min, ProxyOn.Min, Smooth);
		const FVector Max = FMath::Lerp(ProxyOff.Max, ProxyOn.Max, Smooth);
		Body->SetRelativeLocation((Min + Max) * 0.5f);
		Body->SetRelativeScale3D(((Max - Min) / 100.f).ComponentMax(FVector(0.01f)));
	}
}
