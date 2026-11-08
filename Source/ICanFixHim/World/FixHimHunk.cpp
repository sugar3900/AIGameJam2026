// I Can Fix Him - AI Game Jam 2026

#include "World/FixHimHunk.h"
#include "ICanFixHim.h"
#include "Audio/FixHimSfxSubsystem.h"
#include "World/FixHimPuffFx.h"
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
#include "Animation/AnimSequenceBase.h"
#include "Misc/PackageName.h"
#include "TimerManager.h"

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
	// Close on the face, slightly below eye level and tilted up at it. Mannequin head sits ~70cm above capsule centre.
	PortraitCapture->SetRelativeLocation(FVector(86.f, 6.f, 64.f));
	PortraitCapture->SetRelativeRotation(FRotator(5.f, 184.f, 0.f));
	PortraitCapture->FOVAngle = 26.f;
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

namespace
{
	/** Loads "/Game/Dir/Asset" or "/Game/Dir/Asset.Asset" (JSON paths may omit the object name). */
	template <typename T>
	T* LoadAssetPath(const FString& Path)
	{
		if (Path.IsEmpty())
		{
			return nullptr;
		}
		FString ObjectPath = Path;
		if (!FPackageName::GetShortName(ObjectPath).Contains(TEXT(".")))
		{
			ObjectPath += TEXT(".") + FPackageName::GetShortName(ObjectPath);
		}
		return TSoftObjectPtr<T>(FSoftObjectPath(ObjectPath)).LoadSynchronous();
	}
}

void AFixHimHunk::ApplyDefinition(const FHunkDefinition& Def)
{
	HunkId = Def.Id;
	BaseScale = Def.Scale;
	GlowColor = Def.GlowColor;

	if (!Def.Mesh.IsEmpty())
	{
		USkeletalMesh* Model = LoadAssetPath<USkeletalMesh>(Def.Mesh);
		if (Model)
		{
			// A real character model: textured, has a face, no primitive dress-up needed.
			// It has its own skeleton, so the mannequin AnimBP can't drive it; loop its retargeted idle instead.
			GetMesh()->SetSkeletalMesh(Model);
			UAnimSequenceBase* Idle = LoadAssetPath<UAnimSequenceBase>(Def.Idle);
			if (Idle)
			{
				GetMesh()->PlayAnimation(Idle, true);
				// Desync hunks so they don't breathe in unison.
				GetMesh()->SetPosition(FMath::FRandRange(0.f, Idle->GetPlayLength()), false);
			}
			else
			{
				GetMesh()->SetAnimInstanceClass(nullptr);
				UE_LOG(LogFixHim, Warning, TEXT("Hunk '%s': no idle animation ('%s'); he'll hold his rest pose."), *Def.Id, *Def.Idle);
			}
			SetActorScale3D(FVector(BaseScale * (bPresent ? 1.f : 0.01f)));
			return;
		}
		UE_LOG(LogFixHim, Warning, TEXT("Hunk '%s': mesh '%s' not found, falling back to the mannequin."), *Def.Id, *Def.Mesh);
	}

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
	PopAnim = EPopAnim::None;
	SetActorHiddenInGame(!bVisible);
	SetActorEnableCollision(bVisible);
	SetActorScale3D(FVector(BaseScale * (bVisible ? 1.f : 0.01f)));
}

void AFixHimHunk::Appear(const FVector& From)
{
	if (bPresent && PopAnim != EPopAnim::Pop)
	{
		return;
	}
	bPresent = true;
	PopAnim = EPopAnim::Appear;
	PopTime = 0.f;
	AppearTo = GetActorLocation();
	AppearFrom = From;
	// Hidden for the first short beat (the fixture sparkles first), then he grows out of it.
	SetActorHiddenInGame(true);
	SetActorScale3D(FVector(BaseScale * 0.01f));
	SetActorLocation(AppearFrom);
	SetActorEnableCollision(true);
	const FLinearColor Glow = GlowColor;
	AFixHimPuffFx::Spawn(GetWorld(), From, Glow, EFixHimPuffStyle::Appear, 1.f);
	FixHim::SfxAt(this, UFixHimSfxSubsystem::Get(this) && UFixHimSfxSubsystem::Get(this)->Has("HunkAppear") ? FName("HunkAppear") : FName("HunkPop"), From, 0.9f, 0.02f);

	if (!bHasStill)
	{
		// The dialogue avatar is a still of this first appearance: once he has grown in and settled, capture it once.
		GetWorldTimerManager().SetTimer(StillTimer, FTimerDelegate::CreateWeakLambda(this, [this]()
			{
				if (!bHasStill)
				{
					CapturePortraitNow(true);
				}
			}), AppearDelay + AppearGrowSeconds + 0.1f, false);
	}
}

void AFixHimHunk::Disappear(bool bBubblePop)
{
	if (!bPresent)
	{
		return;
	}
	bPresent = false;
	SetActorEnableCollision(false);
	SetPortraitLive(false);
	if (!bBubblePop || IsHidden())
	{
		SetPresentImmediate(false);
		return;
	}
	if (PopAnim == EPopAnim::Appear)
	{
		// Still growing in: finish at his spot so the pop happens where he stands.
		SetActorLocation(AppearTo);
	}
	PopAnim = EPopAnim::Pop;
	PopTime = 0.f;
}

void AFixHimHunk::SetPortraitLive(bool bLive)
{
	// Not live any more: the avatar is a single still. Only capture here if he never got his first-appearance shot.
	if (bLive && !bHasStill)
	{
		CapturePortraitNow(true);
	}
}

void AFixHimHunk::CapturePortraitNow(bool bAsStill)
{
	if (PortraitCapture && PortraitTarget)
	{
		bHasStill |= bAsStill;
		// Capture at full size even mid-pop so silhouettes are never tiny.
		const FVector Saved = GetActorScale3D();
		SetActorScale3D(FVector(BaseScale));
		const bool bWasHidden = IsHidden();
		SetActorHiddenInGame(false);
		GetMesh()->RefreshBoneTransforms();
		PortraitCapture->CaptureScene();
		SetActorHiddenInGame(bWasHidden);
		SetActorScale3D(Saved);
	}
}

void AFixHimHunk::CaptureKeepsake(UTextureRenderTarget2D* Target)
{
	if (!PortraitCapture || !Target)
	{
		return;
	}
	UTextureRenderTarget2D* SavedTarget = PortraitCapture->TextureTarget;
	const FVector SavedLoc = PortraitCapture->GetRelativeLocation();
	const FRotator SavedRot = PortraitCapture->GetRelativeRotation();
	const float SavedFov = PortraitCapture->FOVAngle;

	PortraitCapture->TextureTarget = Target;
	PortraitCapture->SetRelativeLocation(FVector(230.f, 28.f, 52.f));
	PortraitCapture->SetRelativeRotation(FRotator(-6.f, 187.f, 0.f));
	PortraitCapture->FOVAngle = 44.f;
	CapturePortraitNow();

	PortraitCapture->TextureTarget = SavedTarget;
	PortraitCapture->SetRelativeLocation(SavedLoc);
	PortraitCapture->SetRelativeRotation(SavedRot);
	PortraitCapture->FOVAngle = SavedFov;
}

void AFixHimHunk::Tick(float DeltaSeconds)
{
	Super::Tick(DeltaSeconds);
	Age += DeltaSeconds;

	if (PopAnim == EPopAnim::Appear)
	{
		PopTime += DeltaSeconds;
		const float T = (PopTime - AppearDelay) / AppearGrowSeconds;
		if (T > 0.f && IsHidden())
		{
			SetActorHiddenInGame(false);
		}
		const float U = FMath::Clamp(T, 0.f, 1.f);
		// Soft ease-out with a barely-there overshoot (much gentler than ease-out-back's 10%).
		const float Ease = 1.f - FMath::Pow(1.f - U, 3.f);
		const float Settle = 1.f + 0.035f * FMath::Sin(U * PI) * U;
		SetActorScale3D(FVector(BaseScale * FMath::Max(0.01f, Ease * Settle)));
		// Drift from the fixture to his spot, slightly ahead of the growth so he never clips through it.
		const float Move = 1.f - FMath::Pow(1.f - FMath::Clamp(T * 1.25f, 0.f, 1.f), 2.f);
		SetActorLocation(FMath::Lerp(AppearFrom, AppearTo, Move));
		if (T >= 1.f)
		{
			PopAnim = EPopAnim::None;
			SetActorScale3D(FVector(BaseScale));
			SetActorLocation(AppearTo);
		}
	}
	else if (PopAnim == EPopAnim::Pop)
	{
		// A quick swell (like a bubble stretching), then gone with a burst.
		constexpr float Swell = 0.16f;
		PopTime += DeltaSeconds;
		if (PopTime < Swell)
		{
			const float U = PopTime / Swell;
			SetActorScale3D(FVector(BaseScale * (1.f + 0.14f * FMath::Sin(U * HALF_PI))));
		}
		else
		{
			const FVector Center = GetActorLocation() + FVector(0.f, 0.f, 40.f * BaseScale);
			AFixHimPuffFx::Spawn(GetWorld(), Center, GlowColor, EFixHimPuffStyle::BubblePop, BaseScale);
			FixHim::SfxAt(this, UFixHimSfxSubsystem::Get(this) && UFixHimSfxSubsystem::Get(this)->Has("BubblePop") ? FName("BubblePop") : FName("HunkLeave"), Center, 1.f, 0.04f);
			SetPresentImmediate(false);
		}
	}

}
