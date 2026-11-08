// I Can Fix Him - AI Game Jam 2026
//
// Debug entry points on the player controller (see FixHimDebug.h). These live here so the
// controller itself only carries their declarations.

#include "ICanFixHim.h"
#include "Player/FixHimPlayerController.h"

#if FIXHIM_DEBUG

#include "World/FixHimMalady.h"
#include "World/FixHimHunk.h"
#include "Core/FixHimSaveSubsystem.h"
#include "Core/FixHimSettings.h"
#include "Dialogue/FixHimDialogueSubsystem.h"
#include "UI/FixHimHUDWidget.h"
#include "UI/FixHimDialogueWidget.h"
#include "UI/FixHimDayWidgets.h"
#include "UI/FixHimMenus.h"
#include "UI/FixHimCards.h"
#include "UI/FixHimFloorPlanWidget.h"
#include "Camera/PlayerCameraManager.h"
#include "EngineUtils.h"
#include "TimerManager.h"

void AFixHimPlayerController::DebugSetPanelOpen(bool bOpen)
{
	bDebugPanelOpen = bOpen;
	// Playing: cursor + game-and-UI while open, back to hidden cursor + game-only on close.
	ApplyInputModeForState();
}

void AFixHimPlayerController::DebugRefreshWorld()
{
	for (TActorIterator<AFixHimMalady> It(GetWorld()); It; ++It)
	{
		It->RefreshRepairState();
	}
	RefreshRepairs();
}

void AFixHimPlayerController::DebugTeleportToDoor()
{
	if (State == EFixHimState::Playing)
	{
		PlacePlayerAtDoor();
	}
}

void AFixHimPlayerController::DebugSetWeek(int32 NewWeek)
{
	switch (State)
	{
	case EFixHimState::Title:
	case EFixHimState::Sleeping:
	case EFixHimState::Traveling:
	case EFixHimState::Finale:
		if (HUDWidget)
		{
			HUDWidget->ShowToast(TEXT("Debug: can't skip days from here."), 2.f);
		}
		return;
	default:
		break;
	}
	UFixHimSaveSubsystem* Save = UFixHimSaveSubsystem::Get(this);
	if (!Save)
	{
		return;
	}
	const int32 NumWeeks = UFixHimSettings::Get()->NumWeeks;
	NewWeek = FMath::Clamp(NewWeek, 1, NumWeeks + 1);

	// Tear down whatever is in progress: podcast, encounter, conversation / cutscene chain, popups, pause.
	if (RadioWidget)
	{
		RadioWidget->Stop();
	}
	bPodcastPlaying = false;
	GetWorldTimerManager().ClearTimer(EncounterTimer);
	GetWorldTimerManager().ClearTimer(TravelTimer);
	if (UFixHimDialogueSubsystem* D = UFixHimDialogueSubsystem::Get(this))
	{
		D->AbortConversation();
	}
	SceneQueue.Reset();
	SceneChainDone = nullptr;
	ActiveSceneId.Reset();
	if (DialogueWidget)
	{
		DialogueWidget->ClearFx();
	}
	HideWidget(DialogueWidget);
	HideWidget(IntroWidget);
	IntroWidget = nullptr;
	HideWidget(EndingWidget);
	EndingWidget = nullptr;
	HideWidget(DoorWidget);
	HideWidget(FloorPlanWidget);
	CloseSubMenu();
	HideWidget(PauseWidget);
	SetPause(false);
	if (ActiveMalady)
	{
		if (AFixHimHunk* Hunk = ActiveMalady->GetHunk())
		{
			Hunk->SetPortraitLive(false);
		}
		ActiveMalady = nullptr;
	}
	for (TActorIterator<AFixHimMalady> It(GetWorld()); It; ++It)
	{
		It->DismissHunk();
	}
	SetViewTargetWithBlend(GetPawn(), 0.f);

	Save->Data().Week = NewWeek;
	if (NewWeek > NumWeeks)
	{
		// Inspection day: straight into the finale (the "Inspection Day" card is skipped).
		DayElapsed = 0.f;
		UpdateDaylight(0.f);
		RefreshRepairs();
		Save->SaveGame();
		EnterState(EFixHimState::Playing);
		RunFinale();
		return;
	}

	// Same morning setup as RequestEndDay's midpoint: hunks home, player at the door, fresh daylight.
	for (TActorIterator<AFixHimMalady> It(GetWorld()); It; ++It)
	{
		It->RefreshRepairState();
	}
	PlacePlayerAtDoor();
	DayElapsed = 0.f;
	bLateToastShown = false;
	UpdateDaylight(0.f);
	RefreshRepairs();
	Save->SaveGame();
	EnterState(EFixHimState::Playing);
	if (PlayerCameraManager)
	{
		PlayerCameraManager->StartCameraFade(1.f, 0.f, 0.4f, FLinearColor(0.12f, 0.f, 0.08f), false, false);
	}
	if (HUDWidget)
	{
		HUDWidget->ShowToast(FString::Printf(TEXT("Debug: week %d"), NewWeek), 2.f);
	}
	StartPodcast();
}

#endif // FIXHIM_DEBUG
