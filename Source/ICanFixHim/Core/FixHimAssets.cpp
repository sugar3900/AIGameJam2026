// I Can Fix Him - AI Game Jam 2026

#include "Core/FixHimAssets.h"
#include "Core/FixHimSettings.h"
#include "Components/StaticMeshComponent.h"
#include "Engine/StaticMesh.h"
#include "GameFramework/Actor.h"
#include "Materials/MaterialInstanceDynamic.h"
#include "Components/CapsuleComponent.h"
#include "Components/SkeletalMeshComponent.h"
#include "GameFramework/Character.h"
#include "AnimationRuntime.h"
#include "Engine/SkeletalMesh.h"

namespace FixHim::Assets
{
	UStaticMesh* ShapeMesh(const FString& Shape)
	{
		const UFixHimSettings* S = UFixHimSettings::Get();
		if (Shape.Equals(TEXT("sphere"), ESearchCase::IgnoreCase)) { return S->SphereMesh.LoadSynchronous(); }
		if (Shape.Equals(TEXT("cylinder"), ESearchCase::IgnoreCase)) { return S->CylinderMesh.LoadSynchronous(); }
		if (Shape.Equals(TEXT("plane"), ESearchCase::IgnoreCase)) { return S->PlaneMesh.LoadSynchronous(); }
		return S->CubeMesh.LoadSynchronous();
	}

	UMaterialInstanceDynamic* MakeFlat(UObject* Outer, const FLinearColor& Color, const FLinearColor& Emissive, float Roughness)
	{
		UMaterialInterface* Base = UFixHimSettings::Get()->FlatMaterial.LoadSynchronous();
		if (!Base)
		{
			return nullptr;
		}
		UMaterialInstanceDynamic* MID = UMaterialInstanceDynamic::Create(Base, Outer);
		MID->SetVectorParameterValue(TEXT("BaseColor"), Color);
		MID->SetVectorParameterValue(TEXT("Emissive"), Emissive);
		MID->SetScalarParameterValue(TEXT("Roughness"), Roughness);
		return MID;
	}

	UMaterialInstanceDynamic* MakeTranslucent(UObject* Outer, const FLinearColor& Color, float Opacity)
	{
		UMaterialInterface* Base = UFixHimSettings::Get()->TranslucentMaterial.LoadSynchronous();
		if (!Base)
		{
			return nullptr;
		}
		UMaterialInstanceDynamic* MID = UMaterialInstanceDynamic::Create(Base, Outer);
		MID->SetVectorParameterValue(TEXT("BaseColor"), Color);
		MID->SetScalarParameterValue(TEXT("Opacity"), Opacity);
		return MID;
	}

	void PaintComponent(UStaticMeshComponent* Comp, const FLinearColor& Color, const FLinearColor& Emissive)
	{
		if (!Comp)
		{
			return;
		}
		UMaterialInstanceDynamic* MID = MakeFlat(Comp, Color, Emissive);
		if (!MID)
		{
			return;
		}
		const int32 Num = FMath::Max(1, Comp->GetNumMaterials());
		for (int32 i = 0; i < Num; ++i)
		{
			Comp->SetMaterial(i, MID);
		}
	}

	UStaticMeshComponent* AddShape(AActor* Owner, USceneComponent* Parent, const FString& Shape, const FVector& Location, const FVector& SizeCm, const FLinearColor& Color, FName Socket, const FRotator& Rotation)
	{
		UStaticMeshComponent* Comp = NewObject<UStaticMeshComponent>(Owner);
		Comp->SetStaticMesh(ShapeMesh(Shape));
		Comp->SetCollisionEnabled(ECollisionEnabled::NoCollision);
		Comp->SetCanEverAffectNavigation(false);
		Comp->SetGenerateOverlapEvents(false);
		Comp->SetupAttachment(Parent, Socket);
		Comp->SetRelativeLocation(Location);
		Comp->SetRelativeRotation(Rotation);
		Comp->SetRelativeScale3D(SizeCm / 100.f);
		Comp->RegisterComponent();
		Owner->AddInstanceComponent(Comp);
		PaintComponent(Comp, Color);
		return Comp;
	}

	void ApplyOutfit(USkeletalMeshComponent* Mesh, const FOutfit& Outfit)
	{
		UMaterialInterface* Base = UFixHimSettings::Get()->CharacterMaterial.LoadSynchronous();
		if (!Mesh || !Base)
		{
			return;
		}
		UMaterialInstanceDynamic* MID = UMaterialInstanceDynamic::Create(Base, Mesh);
		MID->SetVectorParameterValue(TEXT("Skin"), Outfit.Skin);
		MID->SetVectorParameterValue(TEXT("Shirt"), Outfit.Shirt);
		MID->SetVectorParameterValue(TEXT("Pants"), Outfit.Pants);
		MID->SetVectorParameterValue(TEXT("Shoes"), Outfit.Shoes);
		MID->SetScalarParameterValue(TEXT("Pattern"), Outfit.Pattern);
		MID->SetScalarParameterValue(TEXT("Roughness"), 0.55f);
		for (int32 i = 0; i < Mesh->GetNumMaterials(); ++i)
		{
			Mesh->SetMaterial(i, MID);
		}
	}

	UStaticMeshComponent* AddBodyProp(ACharacter* Character, const FString& Shape, const FVector& Location, const FVector& SizeCm, const FLinearColor& Color, FName Bone, const FRotator& Rotation, float Emissive)
	{
		USkeletalMeshComponent* Mesh = Character->GetMesh();
		// Character space -> mesh space (the mannequin faces +Y, its mesh is rotated -90 yaw on the capsule).
		const FVector MeshLoc(-Location.Y, Location.X, Location.Z);
		const FRotator MeshRot = (FRotator(0.f, 90.f, 0.f).Quaternion() * Rotation.Quaternion()).Rotator();
		UStaticMeshComponent* Comp = AddShape(Character, Mesh, Shape, MeshLoc, SizeCm, Color, NAME_None, MeshRot);
		if (Emissive > 0.f)
		{
			PaintComponent(Comp, Color, Color * Emissive);
		}
		Comp->SetCastShadow(false);
		const USkeletalMesh* Asset = Mesh->GetSkeletalMeshAsset();
		const int32 BoneIndex = Asset && !Bone.IsNone() ? Asset->GetRefSkeleton().FindBoneIndex(Bone) : INDEX_NONE;
		if (BoneIndex != INDEX_NONE)
		{
			// Express the prop relative to the bone's *reference pose* so it rides along with the animation.
			const FTransform BoneCS = FAnimationRuntime::GetComponentSpaceTransformRefPose(Asset->GetRefSkeleton(), BoneIndex);
			const FTransform PropCS(MeshRot, MeshLoc, SizeCm / 100.f);
			Comp->AttachToComponent(Mesh, FAttachmentTransformRules::KeepRelativeTransform, Bone);
			Comp->SetRelativeTransform(PropCS.GetRelativeTransform(BoneCS));
		}
		return Comp;
	}

	void AddEyes(ACharacter* Character, const FLinearColor& Color)
	{
		for (const float Side : { -1.f, 1.f })
		{
			UStaticMeshComponent* Eye = AddBodyProp(Character, TEXT("sphere"), FVector(10.2f, 3.3f * Side, 170.5f), FVector(1.6f, 2.3f, 3.0f), Color, TEXT("head"));
			if (UMaterialInstanceDynamic* MID = MakeFlat(Eye, Color, FLinearColor::Black, 0.15f))
			{
				Eye->SetMaterial(0, MID);
			}
		}
	}
}
