// I Can Fix Him - AI Game Jam 2026

#include "World/FixHimBed.h"
#include "Player/FixHimPlayerController.h"

AFixHimBed::AFixHimBed()
{
	Toggle = EInteractToggle::None;
	ShineColor = FLinearColor(0.75f, 0.7f, 1.f);
	OutlineColor = FLinearColor(0.7f, 0.55f, 1.f);
}

void AFixHimBed::Interact(AFixHimPlayerController* Player)
{
	PlayInteractSfx();
	if (Player)
	{
		Player->OpenDoorPrompt();
	}
}

FText AFixHimBed::GetPrompt() const
{
	return NSLOCTEXT("FixHim", "BedPrompt", "Go to bed (end the day)");
}
