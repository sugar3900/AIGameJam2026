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
#include "Engine/Texture.h"
#include "Engine/TextureRenderTarget2D.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "Materials/MaterialInstanceDynamic.h"
#include "Animation/AnimInstance.h"
#include "Animation/AnimSequenceBase.h"
#include "Misc/PackageName.h"
#include "TimerManager.h"
#if WITH_EDITOR
#include "TextureCompiler.h"
#endif

AFixHimHunk::AFixHimHunk()
{
	PrimaryActorTick.bCanEverTick = true;
	AutoPossessAI = EAutoPossessAI::Disabled;
	AIControllerClass = nullptr;
	// Stay invisible from component registration onward, before BeginPlay loads any assets.
	SetActorHiddenInGame(true);
	SetActorEnableCollision(false);

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
	SetActorHiddenInGame(true);
	SetActorEnableCollision(false);

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

	// ApplyDefinition installs the final mesh and its fully dissolved materials while still hidden.
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
	SetActorHiddenInGame(true);
	SetActorEnableCollision(false);
	bPresent = false;
	PopAnim = EPopAnim::None;
	GetWorldTimerManager().ClearTimer(StillTimer);
	bHasStill = false;
	// A new definition must not inherit dynamic materials from the previous mesh.
	GetMesh()->EmptyOverrideMaterials();
	FormMIDs.Reset();
	HunkId = Def.Id;
	BaseScale = Def.Scale;
	GlowColor = Def.GlowColor;
	Enter = ParseEntrance(Def.Entrance);
	Leave = Def.Exit.IsEmpty() ? Enter : ParseEntrance(Def.Exit);

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
			SetActorScale3D(FVector(BaseScale));
			SetForm(0.f, Enter);
			PreloadTextures();
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

	SetActorScale3D(FVector(BaseScale));
	SetForm(0.f, Enter);
	PreloadTextures();
}

void AFixHimHunk::PreloadTextures()
{
	// Warm up while the character is still hidden, including materials on fallback outfit props.
	TArray<UTexture*> Textures;
	TInlineComponentArray<UMeshComponent*> Meshes(this);
	for (UMeshComponent* Mesh : Meshes)
	{
		for (UMaterialInterface* Material : Mesh->GetMaterials())
		{
			if (!Material)
			{
				continue;
			}
			TArray<UTexture*> UsedTextures;
			Material->GetUsedTextures(UsedTextures);
			for (UTexture* Texture : UsedTextures)
			{
				if (Texture)
				{
					Textures.AddUnique(Texture);
				}
			}
		}
	}
	// Loaded objects may still have asynchronous texture builds pending in the editor.
#if WITH_EDITOR
	FTextureCompilingManager::Get().FinishCompilation(Textures);
#endif
	for (UTexture* Texture : Textures)
	{
		Texture->SetForceMipLevelsToBeResident(30.f);
	}
	for (UTexture* Texture : Textures)
	{
		Texture->WaitForStreaming();
	}
}

void AFixHimHunk::SetPresentImmediate(bool bVisible)
{
	bPresent = bVisible;
	PopAnim = EPopAnim::None;
	if (!bVisible)
	{
		SetActorHiddenInGame(true);
		GetWorldTimerManager().ClearTimer(StillTimer);
	}
	SetActorEnableCollision(bVisible);
	SetActorScale3D(FVector(BaseScale));
	SetForm(bVisible ? 1.f : 0.f, Enter);
	SetActorHiddenInGame(!bVisible);
}

void AFixHimHunk::Appear(const FVector& From)
{
	if (bPresent && PopAnim != EPopAnim::Pop)
	{
		return;
	}
	// Hidden characters can have their mips evicted between visits. Finish reloading before
	// starting the dissolve, sound, portrait timer, or the caller's encounter timer.
	PreloadTextures();
	bPresent = true;
	PopAnim = EPopAnim::Appear;
	PopTime = 0.f;
	AppearTo = GetActorLocation();
	// Hidden for the first short beat (the fixture sparkles first), then he grows out of it.
	// No scaling and no travel for any style: he stands where he will be, and the transition effect builds him there.
	SetActorHiddenInGame(true);
	SetActorEnableCollision(true);
	SetActorScale3D(FVector(BaseScale));
	SetActorLocation(AppearTo);
	SetForm(0.f, Enter);
	PlayEntranceFx(AppearTo, true);

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
	PopAnim = EPopAnim::Pop;
	PopTime = 0.f;
	bLeaveFxPlayed = false;
	LeaveStartForm = FormAlpha;
}

AFixHimHunk::EEntrance AFixHimHunk::ParseEntrance(const FString& Name)
{
	if (Name.Equals(TEXT("sparkle"), ESearchCase::IgnoreCase))
	{
		return EEntrance::Sparkle;
	}
	if (Name.Equals(TEXT("spores"), ESearchCase::IgnoreCase))
	{
		return EEntrance::Spores;
	}
	if (Name.Equals(TEXT("surge"), ESearchCase::IgnoreCase))
	{
		return EEntrance::Surge;
	}
	return EEntrance::Bubble;
}

void AFixHimHunk::SetForm(float Alpha, EEntrance Style)
{
	FormAlpha = Alpha;
	if (FormMIDs.IsEmpty())
	{
		if (!GetMesh())
		{
			return;
		}
		for (int32 i = 0; i < GetMesh()->GetNumMaterials(); ++i)
		{
			if (UMaterialInterface* M = GetMesh()->GetMaterial(i))
			{
				UMaterialInstanceDynamic* MID = UMaterialInstanceDynamic::Create(M, this);
				// Set the mask before attaching: the master material defaults to fully visible.
				MID->SetScalarParameterValue(TEXT("Dissolve"), Alpha);
				GetMesh()->SetMaterial(i, MID);
				FormMIDs.Add(MID);
			}
		}
	}
	// The front of the sweep, per style:
	//   Spores  smoky black that darkens him as he forms
	//   Surge   hot electric blue-white with crackling arcs
	//   Sparkle a warm glittering white
	//   Bubble  a soft, glassy bubble-pink shimmer
	FLinearColor Edge;
	float Glow = 0.f, Arcs = 0.f, Dark = 0.f;
	switch (Style)
	{
	case EEntrance::Spores:
		Edge = FLinearColor(0.01f, 0.014f, 0.01f);
		Dark = 1.f;
		break;
	case EEntrance::Surge:
		Edge = FMath::Lerp(GlowColor, FLinearColor(0.45f, 0.8f, 1.f), 0.6f);
		Glow = 14.f;
		Arcs = 6.f;
		break;
	case EEntrance::Sparkle:
		Edge = FMath::Lerp(GlowColor, FLinearColor(1.f, 0.95f, 0.8f), 0.55f);
		Glow = 9.f;
		break;
	default:
		Edge = FMath::Lerp(FMath::Lerp(GlowColor, FLinearColor::White, 0.45f), FLinearColor(1.f, 0.62f, 0.82f), 0.5f);
		Glow = 5.f;
		break;
	}
	for (UMaterialInstanceDynamic* MID : FormMIDs)
	{
		if (!MID)
		{
			continue;
		}
		MID->SetScalarParameterValue(TEXT("Dissolve"), Alpha);
		MID->SetScalarParameterValue(TEXT("FormHeight"), 190.f * BaseScale);
		MID->SetVectorParameterValue(TEXT("EdgeColor"), Edge);
		MID->SetScalarParameterValue(TEXT("EdgeGlow"), Glow);
		MID->SetScalarParameterValue(TEXT("ArcAmount"), Arcs);
		MID->SetScalarParameterValue(TEXT("EdgeDark"), Dark);
	}
}

void AFixHimHunk::PlayEntranceFx(const FVector& At, bool bIn)
{
	const UFixHimSfxSubsystem* Sfx = UFixHimSfxSubsystem::Get(this);
	// The cue, falling back to a generic hunk sound if the new one has not been imported.
	const auto Play = [&](const char* Cue, const char* Fallback, float Volume)
	{
		FixHim::SfxAt(this, Sfx && Sfx->Has(Cue) ? FName(Cue) : FName(Fallback), At, Volume, 0.03f);
	};
	switch (bIn ? Enter : Leave)
	{
	case EEntrance::Surge:
		AFixHimPuffFx::Spawn(GetWorld(), At, GlowColor, bIn ? EFixHimPuffStyle::SurgeIn : EFixHimPuffStyle::SurgeOut, BaseScale);
		Play(bIn ? "SurgeIn" : "SurgeOut", bIn ? "Zap" : "HunkLeave", 1.f);
		break;
	case EEntrance::Sparkle:
		AFixHimPuffFx::Spawn(GetWorld(), At, GlowColor, bIn ? EFixHimPuffStyle::SparkleIn : EFixHimPuffStyle::SparkleOut, BaseScale);
		if (bIn)
		{
			Play("HunkAppear", "HunkPop", 0.9f);
		}
		else
		{
			Play("SparkleOut", "HunkLeave", 0.9f);
		}
		break;
	case EEntrance::Spores:
		AFixHimPuffFx::Spawn(GetWorld(), At, GlowColor, bIn ? EFixHimPuffStyle::SporesIn : EFixHimPuffStyle::SporesOut, BaseScale);
		Play(bIn ? "SporesIn" : "SporesOut", bIn ? "HunkPop" : "HunkLeave", 1.f);
		break;
	default:
		AFixHimPuffFx::Spawn(GetWorld(), At, GlowColor, bIn ? EFixHimPuffStyle::Appear : EFixHimPuffStyle::BubblePop, bIn ? 1.f : BaseScale);
		Play(bIn ? "HunkAppear" : "BubblePop", bIn ? "HunkPop" : "HunkLeave", bIn ? 0.9f : 1.f);
		break;
	}
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
		const float SavedForm = FormAlpha;
		SetForm(1.f, Enter);
		SetActorHiddenInGame(false);
		GetMesh()->RefreshBoneTransforms();
		PortraitCapture->CaptureScene();
		SetActorHiddenInGame(bWasHidden);
		SetForm(SavedForm, Enter);
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
		// Built in place by the transition shader (no scaling): the front sweeps from his feet to his head.
		PopTime += DeltaSeconds;
		const float T = (PopTime - AppearDelay) / InSeconds(static_cast<int32>(Enter));
		// Update the mask before exposing the mesh to the main view.
		SetForm(FMath::Clamp(T, 0.f, 1.f), Enter);
		if (T > 0.f && IsHidden())
		{
			SetActorHiddenInGame(false);
		}
		if (T >= 1.f)
		{
			PopAnim = EPopAnim::None;
			SetForm(1.f, Enter);
		}
	}
	else if (PopAnim == EPopAnim::Pop)
	{
		// Taken apart in place: the effect starts at once and the shader removes him from the head down.
		PopTime += DeltaSeconds;
		if (!bLeaveFxPlayed)
		{
			bLeaveFxPlayed = true;
			PlayEntranceFx(GetActorLocation(), false);
		}
		const float U = FMath::Clamp(PopTime / OutSeconds(static_cast<int32>(Leave)), 0.f, 1.f);
		SetForm(LeaveStartForm * (1.f - U), Leave);
		if (U >= 1.f)
		{
			SetPresentImmediate(false);
		}
	}
}
