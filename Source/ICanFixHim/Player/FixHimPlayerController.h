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
class UFixHimOptionsWidget;
class UFixHimCreditsWidget;
class UFixHimFloorPlanWidget;
class UFixHimIntroCardWidget;
class UFixHimEndingCardWidget;
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
	Ending,
	Traveling
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

	EFixHimState GetState() const { return State; }

	// ---- Menu API (called by widgets) -------------------------------------
	void StartNewGame();
	void ContinueGame();
	void OpenOptions();
	void OpenCredits();
	void CloseSubMenu();
	void SetPaused(bool bPause);
	void ReturnToMainMenu();
	void QuitToDesktop();
	void CloseEndingCard();

	// ---- World API ---------------------------------------------------------
	void BeginEncounter(AFixHimMalady* Malady);
	void AdvanceDialogue();
	void ToggleFloorPlan();
	void TravelToRoom(AFixHimRoom* Room);
	void NotifyEnteredRoom(AFixHimRoom* Room);
	void NotifyLeftRoom(AFixHimRoom* Room);
	const FString& GetCurrentRoomId() const { return CurrentRoomId; }

	// ---- Debug / automation (console) -------------------------------------
	UFUNCTION(Exec) void FixHimNewGame();
	UFUNCTION(Exec) void FixHimTalk(const FString& HunkId);
	UFUNCTION(Exec) void FixHimAdvance(int32 Times = 1);
	UFUNCTION(Exec) void FixHimChoose(int32 OneBasedIndex);
	UFUNCTION(Exec) void FixHimTopic(const FString& Topic);
	UFUNCTION(Exec) void FixHimMap();
	/** Simulates a click: interacts with whatever is under the reticle, or dismisses the ending card. */
	UFUNCTION(Exec) void FixHimClick();
	UFUNCTION(Exec) void FixHimPause(bool bPause);
	UFUNCTION(Exec) void FixHimOptions();
	/** Plays the active conversation to the end, picking choices from a comma list of 1-based indices (default 1). */
	UFUNCTION(Exec) void FixHimAuto(const FString& Choices);
	UFUNCTION(Exec) void FixHimGoto(const FString& RoomId);
	UFUNCTION(Exec) void FixHimLook(float Yaw, float Pitch);
	UFUNCTION(Exec) void FixHimShot(const FString& Name);
	UFUNCTION(Exec) void FixHimDump();
	/** Runs a ';'-separated list of console commands. "wait <seconds>" pauses the script. */
	UFUNCTION(Exec) void FixHimScript(const FString& Script);

private:
	void BuildInput();
	void EnterState(EFixHimState NewState);
	void ApplyInputModeForState();
	void UpdateHover();
	void SetHovered(AFixHimInteractable* NewHovered);

	void StartDialogue();
	void HandleDialogueView(const FDialogueView& View);
	void HandleConversationEnded(const FString& HunkId, const FString& EndingId);
	void HandleStatChanged(const FString& HunkId, ERelationshipAxis Axis, int32 Delta);
	void HandleSaved();
	void HandlePreSave();
	void BeginPlaying(bool bFromSave);
	void RefreshRepairs();
	void ShowWidget(UUserWidget* Widget, int32 ZOrder);
	void HideWidget(UUserWidget* Widget);
	void RunNextScriptStep();

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
	UPROPERTY(Transient) TObjectPtr<UFixHimOptionsWidget> OptionsWidget;
	UPROPERTY(Transient) TObjectPtr<UFixHimCreditsWidget> CreditsWidget;
	UPROPERTY(Transient) TObjectPtr<UFixHimFloorPlanWidget> FloorPlanWidget;
	UPROPERTY(Transient) TObjectPtr<UFixHimIntroCardWidget> IntroWidget;
	UPROPERTY(Transient) TObjectPtr<UFixHimEndingCardWidget> EndingWidget;
	UPROPERTY(Transient) TObjectPtr<UUserWidget> SubMenu;

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
	FDelegateHandle ViewHandle, EndHandle, StatHandle, SavedHandle, PreSaveHandle;
	float TitleTime = 0.f;
	FTransform TitleCameraBase;
};
