// I Can Fix Him - AI Game Jam 2026

#include "World/FixHimHunk.h"
#include "Core/FixHimAssets.h"
#include "Core/FixHimSettings.h"
#include "Dialogue/DialogueTypes.h"
#include "Components/CapsuleComponent.h"
#include "Components/SkeletalMeshComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Components/SceneCaptureComponent2D.h"
#include "Engine/SkeletalMesh.h"
#include "Engine/TextureRenderTarget2D.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "Materials/MaterialInstanceDynamic.h"
#include "Animation/AnimInstance.h"

AFixHimHunk::AFixHimHunk()
{
	PrimaryActorTick.bCanEverTick = true;
	AutoPossessAI = EAutoPossessAI::Disabled;
	AIControllerClass = nullptr;

	GetCapsuleComponent()->InitCapsuleSize(38.f, 92.f);
	GetCharacterMovement()->GravityScale = 0.f;
	GetCharacterMovement()->SetMovementMode(MOVE_None);

	GetMesh()->SetRelativeLocation(FVector(0.f, 0.f, -92.f));
	GetMesh()->SetRelativeRotation(FRotator(0.f, -90.f, 0.f));
	GetMesh()->SetCollisionEnabled(ECollisionEnabled::NoCollision);

	PortraitCapture = CreateDefaultSubobject<USceneCaptureComponent2D>(TEXT("PortraitCapture"));
	PortraitCapture->SetupAttachment(GetCapsuleComponent());
	// In front of the face, looking back at it. Mannequin head sits ~70cm above capsule centre.
	PortraitCapture->SetRelativeLocation(FVector(118.f, 10.f, 74.f));
	PortraitCapture->SetRelativeRotation(FRotator(-4.f, 185.f, 0.f));
	PortraitCapture->FOVAngle = 30.f;
	PortraitCapture->bCaptureEveryFrame = false;
	PortraitCapture->bCaptureOnMovement = false;
	PortraitCapture->PrimitiveRenderMode = ESceneCapturePrimitiveRenderMode::PRM_UseShowOnlyList;
	PortraitCapture->CaptureSource = ESceneCaptureSource::SCS_SceneColorHDR;
}

void AFixHimHunk::BeginPlay()
{
	Super::BeginPlay();

	const UFixHimSettings* S = UFixHimSettings::Get();
	if (USkeletalMesh* Mesh = S->HunkMesh.LoadSynchronous())
	{
		GetMesh()->SetSkeletalMesh(Mesh);
	}
	if (UClass* Anim = S->LocomotionAnimClass.LoadSynchronous())
	{
		GetMesh()->SetAnimInstanceClass(Anim);
	}

	PortraitTarget = NewObject<UTextureRenderTarget2D>(this);
	PortraitTarget->RenderTargetFormat = RTF_RGBA16f;
	PortraitTarget->ClearColor = FLinearColor(0.f, 0.f, 0.f, 1.f);
	PortraitTarget->InitAutoFormat(512, 512);
	PortraitTarget->UpdateResourceImmediate(true);
	PortraitCapture->TextureTarget = PortraitTarget;
	PortraitCapture->ShowOnlyActors.Add(this);

	SetPresentImmediate(false);
}

void AFixHimHunk::ApplyDefinition(const FHunkDefinition& Def)
{
	HunkId = Def.Id;
	BaseScale = Def.Scale;

	FixHim::Assets::FOutfit Outfit;
	Outfit.Skin = Def.Skin;
	Outfit.Shirt = Def.Shirt;
	Outfit.Pants = Def.Pants;
	Outfit.Shoes = Def.Shoes;
	Outfit.Pattern = Def.Pattern;
	FixHim::Assets::ApplyOutfit(GetMesh(), Outfit);

	// Props are placed against the reference pose, then glued to their bone so they follow the idle animation.
	SetActorScale3D(FVector(BaseScale));
	FixHim::Assets::AddEyes(this);
	for (const FHunkProp& Prop : Def.Props)
	{
		FixHim::Assets::AddBodyProp(this, Prop.Shape, Prop.Location, Prop.Scale, Prop.Color, Prop.Socket, Prop.Rotation, Prop.Emissive);
	}

	SetActorScale3D(FVector(BaseScale * (bPresent ? 1.f : 0.01f)));
}

void AFixHimHunk::SetPresentImmediate(bool bVisible)
{
	bPresent = bVisible;
	PopAlpha = PopTarget = bVisible ? 1.f : 0.f;
	SetActorHiddenInGame(!bVisible);
	SetActorEnableCollision(bVisible);
	SetActorScale3D(FVector(BaseScale * (bVisible ? 1.f : 0.01f)));
}

void AFixHimHunk::Appear()
{
	if (bPresent)
	{
		return;
	}
	bPresent = true;
	PopTarget = 1.f;
	SetActorHiddenInGame(false);
	SetActorEnableCollision(true);
}

void AFixHimHunk::Disappear()
{
	if (!bPresent)
	{
		return;
	}
	bPresent = false;
	PopTarget = 0.f;
	SetActorEnableCollision(false);
	SetPortraitLive(false);
}

void AFixHimHunk::SetPortraitLive(bool bLive)
{
	bPortraitLive = bLive;
	PortraitCapture->bCaptureEveryFrame = bLive;
	if (bLive)
	{
		CapturePortraitNow();
	}
}

void AFixHimHunk::CapturePortraitNow()
{
	if (PortraitCapture && PortraitTarget)
	{
		// Capture at full size even mid-pop so silhouettes are never tiny.
		const FVector Saved = GetActorScale3D();
		SetActorScale3D(FVector(BaseScale));
		const bool bWasHidden = IsHidden();
		SetActorHiddenInGame(false);
		PortraitCapture->CaptureScene();
		SetActorHiddenInGame(bWasHidden);
		SetActorScale3D(Saved);
	}
}

void AFixHimHunk::Tick(float DeltaSeconds)
{
	Super::Tick(DeltaSeconds);
	Age += DeltaSeconds;

	if (!FMath::IsNearlyEqual(PopAlpha, PopTarget))
	{
		PopAlpha = FMath::FInterpConstantTo(PopAlpha, PopTarget, DeltaSeconds, 3.f);
		// Ease-out-back for a springy "poof" entrance.
		const float T = PopAlpha;
		const float C1 = 1.70158f;
		const float C3 = C1 + 1.f;
		const float Eased = PopTarget > 0.5f ? 1.f + C3 * FMath::Pow(T - 1.f, 3.f) + C1 * FMath::Pow(T - 1.f, 2.f) : T * T;
		SetActorScale3D(FVector(BaseScale * FMath::Max(0.01f, Eased)));
		if (PopAlpha <= 0.f && PopTarget <= 0.f)
		{
			SetActorHiddenInGame(true);
		}
	}
}
