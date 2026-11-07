// I Can Fix Him - AI Game Jam 2026

#pragma once

#include "CoreMinimal.h"

class UMaterialInstanceDynamic;
class UMaterialInterface;
class UStaticMesh;
class UStaticMeshComponent;
class UObject;

/** Small helpers for building stylized primitive visuals at runtime from the assets in UFixHimSettings. */
namespace FixHim::Assets
{
	ICANFIXHIM_API UStaticMesh* ShapeMesh(const FString& Shape);

	/** Dynamic instance of the flat lit material. */
	ICANFIXHIM_API UMaterialInstanceDynamic* MakeFlat(UObject* Outer, const FLinearColor& Color, const FLinearColor& Emissive = FLinearColor::Black, float Roughness = 0.6f);

	/** Dynamic instance of the unlit translucent material. */
	ICANFIXHIM_API UMaterialInstanceDynamic* MakeTranslucent(UObject* Outer, const FLinearColor& Color, float Opacity);

	/** Applies one flat colour to every material slot of a mesh component. */
	ICANFIXHIM_API void PaintComponent(UStaticMeshComponent* Comp, const FLinearColor& Color, const FLinearColor& Emissive = FLinearColor::Black);

	/**
	 * Creates a cosmetic static mesh component (no collision, no navigation impact) and attaches it.
	 * Location is in the parent's space, Size is in centimetres (meshes are assumed 100cm primitives).
	 */
	struct FOutfit
	{
		FLinearColor Skin, Shirt, Pants, Shoes;
		float Pattern = 0.f;
	};

	/** Applies M_Character to every slot of a mannequin with the given outfit colours. */
	ICANFIXHIM_API void ApplyOutfit(class USkeletalMeshComponent* Mesh, const FOutfit& Outfit);

	/**
	 * Glues a cosmetic primitive to a mannequin. Location is in "character space"
	 * (X forward, Y right, Z up from the feet, cm, unscaled) and the shape follows Bone.
	 */
	ICANFIXHIM_API UStaticMeshComponent* AddBodyProp(class ACharacter* Character, const FString& Shape, const FVector& Location, const FVector& SizeCm, const FLinearColor& Color, FName Bone, const FRotator& Rotation = FRotator::ZeroRotator, float Emissive = 0.f);

	/** Two little glossy eyes, because faceless mannequins are hard to flirt with. */
	ICANFIXHIM_API void AddEyes(class ACharacter* Character, const FLinearColor& Color = FLinearColor(0.02f, 0.02f, 0.03f));

	ICANFIXHIM_API UStaticMeshComponent* AddShape(AActor* Owner, USceneComponent* Parent, const FString& Shape, const FVector& Location, const FVector& SizeCm, const FLinearColor& Color, FName Socket = NAME_None, const FRotator& Rotation = FRotator::ZeroRotator);
}
