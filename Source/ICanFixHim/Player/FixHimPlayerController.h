// I Can Fix Him - AI Game Jam 2026

#pragma once

#include "CoreMinimal.h"
#include "GameFramework/PlayerController.h"
#include "Core/FixHimSaveTypes.h"
#include "Dialogue/DialogueTypes.h"
#include "FixHimPlayerController.generated.h"

class UInputAction;
class UInputMappingContext;
struct FInputActionValue;
class AFixHimInteractable;
class AFixHimMalady;
class AFixHimRoom;
class UFixHimTitleWidget;
class UFixHimHUDWidget;
class UFixHimDialogueWidget;
class UFixHimPauseWidget;
class UFixHimDoorPromptWidget;
class UFixHimOptionsWidget;
class UFixHimCreditsWidget;
class UFixHimFloorPlanWidget;
class UFixHimIntroCardWidget;
class UFixHimEndingCardWidget;
class UFixHimRadioWidget;
class UFixHimNameEntryWidget;
class UFixHimTransitionWidget;
class UFixHimKeepsakeWidget;
class ADirectionalLight;
class ULightComponent;
class UMaterialInstanceDynamic;
class UUserWidget;

UENUM(BlueprintType)
enum class EFixHimState : uint8
{
	Title,
	Playing,
	/** Camera swinging to the hunk / intro card playing. */
	Encounter,
	Dialogue,
	FloorPlan,
	Paused,
	/** "End the day?" popup from the front door; gameplay is paused underneath. */
	DoorPrompt,
	Ending,
	Traveling,
	/** Week transition / sleeping. */
	Sleeping,
	/** A scripted scene in the dialogue box with no hunk (inspection, epilogue). */
	Cutscene,
	/** End-of-game keepsake screen. */
	Finale
};

/**
 * The game's hub: game state machine, input, interaction tracing, encounters,
 * menus and room tracking. Widgets call back into the public API here.
 */
UCLASS()
class ICANFIXHIM_API AFixHimPlayerController : public APlayerController
{
	GENERATED_BODY()

public:
	AFixHimPlayerController();

	virtual void BeginPlay() override;
	virtual void EndPlay(const EEndPlayReason::Type Reason) override;
	virtual void SetupInputComponent() override;
	virtual void PlayerTick(float DeltaTime) override;

	UFUNCTION(BlueprintPure, Category = "Game State")
	EFixHimState GetState() const { return State; }

	// ---- Menu API (called by widgets) -------------------------------------
	/** Title "New Game": asks for the heroine's name first. */
	void StartNewGame();
	/** Name chosen: wipe progress and start week 1. */
	void BeginNewGame(const FString& PlayerName);
	void CancelNameEntry();
	void ContinueGame();
	void OpenOptions();
	void OpenCredits();
	void CloseSubMenu();
	void SetPaused(bool bPause);
	void ReturnToMainMenu();
	void QuitToDesktop();
	void CloseEndingCard();
	/** Called by the keepsake screen: wipe the finished save and go back to the title. */
	void FinishGame();

	// ---- Days ----------------------------------------------------------------
	/** Bed or door popup confirmed. On week 1 you must meet everyone first. On the last week this triggers the finale. */
	void RequestEndDay();
	/** False on week 1 until everyone has been met. */
	bool CanEndDay() const;
	/** Door or bed was clicked: pops up End Day / Cancel. */
	void OpenDoorPrompt();
	/** Cancel (or Escape): closes the popup and gives control back. Nothing is consumed. */
	void CloseDoorPrompt();
	/** "End Day" pressed in the popup. */
	void ConfirmEndDay();
	UFUNCTION(BlueprintPure, Category = "Game State")
	bool IsPodcastPlaying() const { return bPodcastPlaying; }

	// ---- World API ---------------------------------------------------------
	void BeginEncounter(AFixHimMalady* Malady);
	void AdvanceDialogue();
	void ToggleFloorPlan();
	void TravelToRoom(AFixHimRoom* Room);
	void NotifyEnteredRoom(AFixHimRoom* Room);
	void NotifyLeftRoom(AFixHimRoom* Room);
	const FString& GetCurrentRoomId() const { return CurrentRoomId; }

	// ---- Debug / automation (console) -------------------------------------
	/** Skips the name prompt (automation). */
	UFUNCTION(Exec) void FixHimNewGame(const FString& PlayerName);
	/** Same as the title menu's Continue button (loads the save for this map). */
	UFUNCTION(Exec) void FixHimContinue();
	UFUNCTION(Exec) void FixHimTalk(const FString& HunkId);
	UFUNCTION(Exec) void FixHimAdvance(int32 Times = 1);
	UFUNCTION(Exec) void FixHimChoose(int32 OneBasedIndex);
	UFUNCTION(Exec) void FixHimTopic(const FString& Topic);
	UFUNCTION(Exec) void FixHimMap();
	/** Simulates a click: interacts with whatever is under the reticle, or dismisses the ending card. */
	UFUNCTION(Exec) void FixHimClick();
	/** Clicks the topmost screen at a viewport position (0..1 fractions) via UFixHimWidget::SimulateClickAt: tests UI hit areas. */
	UFUNCTION(Exec) void FixHimClickAt(float X, float Y);
	UFUNCTION(Exec) void FixHimPause(bool bPause);
	/** Same as Pause > Save & Exit: saves and reloads the map to the title screen. */
	UFUNCTION(Exec) void FixHimReturnToTitle();
	UFUNCTION(Exec) void FixHimOptions();
	UFUNCTION(Exec) void FixHimSleep();
	UFUNCTION(Exec) void FixHimSkipTime(float Seconds);
	UFUNCTION(Exec) void FixHimSkipPodcast();
	UFUNCTION(Exec) void FixHimKeepsake(int32 Index);
	UFUNCTION(Exec) void FixHimNamePrompt();
	/** Plays the active conversation to the end, picking choices from a comma list of 1-based indices (default 1). */
	UFUNCTION(Exec) void FixHimAuto(const FString& Choices);
	UFUNCTION(Exec) void FixHimGoto(const FString& RoomId);
	UFUNCTION(Exec) void FixHimLook(float Yaw, float Pitch);
	/** Places the pawn Distance cm from an interactable (name or editor-label substring), on the side facing its room's
	 *  entry, and aims at its bounds centre so the normal hover trace targets it. For scripted screenshots. */
	UFUNCTION(Exec) void FixHimAimAt(const FString& Name, float Distance = 160.f);
	UFUNCTION(Exec) void FixHimShot(const FString& Name);
	UFUNCTION(Exec) void FixHimDump();
	/** Plays dialogue scripts (comma-separated ids, e.g. "inspection,epilogue") in the dialogue box, then back to playing. */
	UFUNCTION(Exec) void FixHimScene(const FString& SceneIds);
	/** Marks a story hunk (or "all") fixed (1) or not (0) and logs whether the house would pass inspection. */
	UFUNCTION(Exec) void FixHimSetFixed(const FString& HunkId, int32 Fixed = 1);
	/** Runs a ';'-separated list of console commands. "wait <seconds>" pauses the script. */
	UFUNCTION(Exec) void FixHimScript(const FString& Script);

#if WITH_EDITOR || !UE_BUILD_SHIPPING
	/** Debug panel open/closed: keeps the cursor visible with game input still running, and restores the state's own mode on close. */
	void DebugSetPanelOpen(bool bOpen);
	/** Jumps to a week (1..NumWeeks+1 = finale) as a clean day rollover, ignoring the week-1 "meet everyone" rule. */
	void DebugSetWeek(int32 NewWeek);
	/** Re-applies the save data to the world (repair state of maladies, HUD counters). */
	void DebugRefreshWorld();
	void DebugTeleportToDoor();
#endif

private:
	void BuildInput();
	void EnterState(EFixHimState NewState);
	void ApplyInputModeForState();
	void RefreshInteractionShine();
	/** Music director: picks the track for the current state (see FixHimMusicSubsystem). Called from EnterState. */
	void UpdateMusic();
	void UpdateHover();
	void SetHovered(AFixHimInteractable* NewHovered);

	void StartDialogue();
	void HandleDialogueView(const FDialogueView& View);
	void HandleConversationStarted(const FString& HunkId);
	void HandleConversationEnded(const FString& HunkId, const FString& EndingId);
	void HandleStatChanged(const FString& HunkId, ERelationshipAxis Axis, int32 Delta);
	void HandleSaved();
	void HandlePreSave();
	void BeginPlaying(bool bFromSave);
	/** Puts the player just inside the front door facing the apartment (start of every day). */
	void PlacePlayerAtDoor();
	void RefreshRepairs();
	void ShowWidget(UUserWidget* Widget, int32 ZOrder);
	void HideWidget(UUserWidget* Widget);
	void RunNextScriptStep();

#if WITH_EDITOR || !UE_BUILD_SHIPPING
	// In-game debug panel (Debug/FixHimDebug*.cpp); not compiled into shipping builds.
	friend class UFixHimDebugComponent;
	bool bDebugPanelOpen = false;
#endif

	// Days, podcast, scripted scenes, finale
	void StartDay(bool bFromSave);
	void StartPodcast();
	void UpdateDaylight(float DeltaTime);
	bool HaveMetEveryone() const;
	void PlaySceneChain(TArray<FString> SceneIds, TFunction<void()> OnDone);
	void PlayNextScene();
	void RunFinale();
	void ShowKeepsake();
	int32 CurrentWeek() const;

	// Input handlers
	void OnMove(const FInputActionValue& Value);
	void OnMouseLook(const FInputActionValue& Value);
	void OnStickLook(const FInputActionValue& Value);
	void OnInteract();
	void OnAdvance();
	void OnPausePressed();
	void OnMapPressed();
	void OnChoice(int32 Index);

	UPROPERTY(Transient) TObjectPtr<UInputMappingContext> Mapping;
	UPROPERTY(Transient) TObjectPtr<UInputAction> MoveAction;
	UPROPERTY(Transient) TObjectPtr<UInputAction> MouseLookAction;
	UPROPERTY(Transient) TObjectPtr<UInputAction> StickLookAction;
	UPROPERTY(Transient) TObjectPtr<UInputAction> InteractAction;
	UPROPERTY(Transient) TObjectPtr<UInputAction> AdvanceAction;
	UPROPERTY(Transient) TObjectPtr<UInputAction> PauseAction;
	UPROPERTY(Transient) TObjectPtr<UInputAction> MapAction;
	UPROPERTY(Transient) TArray<TObjectPtr<UInputAction>> ChoiceActions;

	UPROPERTY(Transient) TObjectPtr<UFixHimTitleWidget> TitleWidget;
	UPROPERTY(Transient) TObjectPtr<UFixHimHUDWidget> HUDWidget;
	UPROPERTY(Transient) TObjectPtr<UFixHimDialogueWidget> DialogueWidget;
	UPROPERTY(Transient) TObjectPtr<UFixHimPauseWidget> PauseWidget;
	UPROPERTY(Transient) TObjectPtr<UFixHimDoorPromptWidget> DoorWidget;
	UPROPERTY(Transient) TObjectPtr<UFixHimOptionsWidget> OptionsWidget;
	UPROPERTY(Transient) TObjectPtr<UFixHimCreditsWidget> CreditsWidget;
	UPROPERTY(Transient) TObjectPtr<UFixHimFloorPlanWidget> FloorPlanWidget;
	UPROPERTY(Transient) TObjectPtr<UFixHimIntroCardWidget> IntroWidget;
	UPROPERTY(Transient) TObjectPtr<UFixHimEndingCardWidget> EndingWidget;
	UPROPERTY(Transient) TObjectPtr<UUserWidget> SubMenu;
	UPROPERTY(Transient) TObjectPtr<UFixHimRadioWidget> RadioWidget;
	UPROPERTY(Transient) TObjectPtr<UFixHimNameEntryWidget> NameWidget;
	UPROPERTY(Transient) TObjectPtr<UFixHimTransitionWidget> TransitionWidget;
	UPROPERTY(Transient) TObjectPtr<UFixHimKeepsakeWidget> KeepsakeWidget;
	UPROPERTY(Transient) TObjectPtr<ADirectionalLight> Sun;
	UPROPERTY(Transient) TArray<TObjectPtr<UMaterialInstanceDynamic>> WindowViews;
	UPROPERTY(Transient) TArray<TObjectPtr<ULightComponent>> WindowSunLights;
	TArray<float> WindowSunBaseIntensities;

	UPROPERTY(Transient) TObjectPtr<AFixHimInteractable> Hovered;
	UPROPERTY(Transient) TObjectPtr<AFixHimMalady> ActiveMalady;
	UPROPERTY(Transient) TObjectPtr<AActor> TitleCamera;

	EFixHimState State = EFixHimState::Title;
	EFixHimState StateBeforePause = EFixHimState::Playing;
	FString CurrentRoomId;
	FString PendingEndingHunk;
	FString PendingEnding;

	TArray<FString> ScriptSteps;
	FTimerHandle ScriptTimer;
	FTimerHandle EncounterTimer;
	FTimerHandle TravelTimer;
	FDelegateHandle ViewHandle, StartedHandle, EndHandle, StatHandle, SavedHandle, PreSaveHandle;
	float TitleTime = 0.f;

	float DayElapsed = 0.f;
	bool bLateToastShown = false;
	bool bPodcastPlaying = false;
	FRotator SunBaseRotation = FRotator::ZeroRotator;
	float SunBaseIntensity = 0.f;
	FLinearColor SunBaseColor = FLinearColor::White;
	TArray<FString> SceneQueue;
	FString ActiveSceneId;
	/** Hunk id of the running conversation (from the dialogue subsystem), for choosing its music. */
	FString MusicConvId;
	TFunction<void()> SceneChainDone;
	FTransform TitleCameraBase;
};
