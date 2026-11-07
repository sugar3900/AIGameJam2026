// I Can Fix Him - AI Game Jam 2026

#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Character.h"
#include "FixHimCharacter.generated.h"

class USpringArmComponent;
class UCameraComponent;

/** Rosie: the new homeowner. Third-person, over-the-shoulder. Input is routed in by AFixHimPlayerController. */
UCLASS()
class ICANFIXHIM_API AFixHimCharacter : public ACharacter
{
	GENERATED_BODY()

public:
	AFixHimCharacter();

	virtual void BeginPlay() override;

	void DoMove(float Right, float Forward);
	void DoLook(float Yaw, float Pitch);

	UCameraComponent* GetFollowCamera() const { return FollowCamera; }
	USpringArmComponent* GetCameraBoom() const { return CameraBoom; }

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Components")
	TObjectPtr<USpringArmComponent> CameraBoom;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Components")
	TObjectPtr<UCameraComponent> FollowCamera;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Look")
	FLinearColor SkinColor = FLinearColor(0.86f, 0.6f, 0.47f);

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Look")
	FLinearColor ShirtColor = FLinearColor(0.18f, 0.36f, 0.66f);

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Look")
	FLinearColor PantsColor = FLinearColor(0.1f, 0.15f, 0.3f);

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Look")
	FLinearColor HairColor = FLinearColor(0.12f, 0.05f, 0.03f);

private:
	void DressUp();
};
