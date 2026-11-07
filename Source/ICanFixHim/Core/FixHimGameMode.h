// I Can Fix Him - AI Game Jam 2026

#pragma once

#include "CoreMinimal.h"
#include "GameFramework/GameModeBase.h"
#include "FixHimGameMode.generated.h"

/** Single-map game: the apartment doubles as the animated title-screen backdrop. */
UCLASS()
class ICANFIXHIM_API AFixHimGameMode : public AGameModeBase
{
	GENERATED_BODY()

public:
	AFixHimGameMode();
};
