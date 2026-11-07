// I Can Fix Him - AI Game Jam 2026

#include "Core/FixHimGameMode.h"
#include "Player/FixHimCharacter.h"
#include "Player/FixHimPlayerController.h"

AFixHimGameMode::AFixHimGameMode()
{
	DefaultPawnClass = AFixHimCharacter::StaticClass();
	PlayerControllerClass = AFixHimPlayerController::StaticClass();
}
