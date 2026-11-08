// I Can Fix Him - AI Game Jam 2026

#pragma once

#include "CoreMinimal.h"
#include "World/FixHimInteractable.h"
#include "FixHimBed.generated.h"

/** Rosie's bed. Click it to end the day (one week passes). */
UCLASS()
class ICANFIXHIM_API AFixHimBed : public AFixHimInteractable
{
	GENERATED_BODY()

public:
	AFixHimBed();

	virtual void Interact(AFixHimPlayerController* Player) override;
	virtual FText GetPrompt() const override;
};
