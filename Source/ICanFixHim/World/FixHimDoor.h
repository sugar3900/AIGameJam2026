// I Can Fix Him - AI Game Jam 2026

#pragma once

#include "CoreMinimal.h"
#include "World/FixHimInteractable.h"
#include "FixHimDoor.generated.h"

/** The front door. Click it to be asked whether to leave and end the day. */
UCLASS()
class ICANFIXHIM_API AFixHimDoor : public AFixHimInteractable
{
	GENERATED_BODY()

public:
	AFixHimDoor();

	/** Spawns the front door at the apartment's entrance if the level doesn't already contain one. */
	static AFixHimDoor* EnsureInWorld(UWorld* World);

	virtual void Interact(AFixHimPlayerController* Player) override;
	virtual FText GetPrompt() const override;
	virtual FName DefaultInteractSfx(bool bNowOn) const override { return TEXT("DoorKnock"); }
};
