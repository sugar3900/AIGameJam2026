// I Can Fix Him - AI Game Jam 2026

#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Character.h"
#include "FixHimCharacter.generated.h"

class UCameraComponent;

/** Rosie: the new homeowner. First person, so she has no visible body. Input is routed in by AFixHimPlayerController. */
UCLASS()
class ICANFIXHIM_API AFixHimCharacter : public ACharacter
{
	GENERATED_BODY()

public:
	AFixHimCharacter();

	virtual void Tick(float DeltaSeconds) override;

	void DoMove(float Right, float Forward);
	void DoLook(float Yaw, float Pitch);

	UCameraComponent* GetFirstPersonCamera() const { return FirstPersonCamera; }

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Components")
	TObjectPtr<UCameraComponent> FirstPersonCamera;

private:
	/** Distance walked since the last footstep sound, and how far the next one is (varies a little). */
	float StepDistance = 0.f;
	float NextStepDistance = 140.f;
};
