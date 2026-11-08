// I Can Fix Him - AI Game Jam 2026

#pragma once

#include "CoreMinimal.h"
#include "UI/FixHimUI.h"
#include "Dialogue/DialogueTypes.h"
#include "Core/FixHimSaveTypes.h"
#include "FixHimDialogueWidget.generated.h"

class UBorder;
class UCanvasPanel;
class UImage;
class UProgressBar;
class USizeBox;
class UTextBlock;
class UVerticalBox;
class UWrapBox;
class UMaterialInstanceDynamic;
class AFixHimHunk;

/**
 * Visual-novel dialogue box covering the bottom quarter of the screen:
 * live portrait, name plate, typewriter text with clickable [topic] words,
 * choices, relationship meters, and full-screen fx (fade to black, hearts).
 */
UCLASS()
class ICANFIXHIM_API UFixHimDialogueWidget : public UFixHimWidget
{
	GENERATED_BODY()

public:
	void BindHunk(AFixHimHunk* Hunk, const FString& HunkId);
	/** Scenes with no hunk (inspection, epilogue): hide the portrait and meters. */
	void BindScript(const FString& ScriptId, const FString& Title);
	void ShowView(const FDialogueView& View);

	/** True while a full-screen effect is playing; input should wait. */
	bool IsBusy() const { return FxPhase != EFxPhase::None; }
	/** If the typewriter is still running, finish it and return true. */
	bool TryCompleteTyping();

	void OnStatChanged(const FString& HunkId, ERelationshipAxis Axis, int32 Delta);
	/** Remove floating hearts / stat pills left over from the previous conversation. */
	void ClearFx();

protected:
	virtual void BuildUI() override;
	virtual void NativeTick(const FGeometry& MyGeometry, float InDeltaTime) override;
	virtual FReply NativeOnMouseButtonDown(const FGeometry& InGeometry, const FPointerEvent& InMouseEvent) override;

private:
	struct FToken
	{
		FString Text;
		FString Topic;
	};

	void ParseTokens(const FString& Marked);
	void BuildWordWrap();
	void BuildChoices();
	void RefreshMeters();
	void SpawnHearts(int32 Count);
	void SpawnFloater(const FString& Text, const FLinearColor& Color);

	UPROPERTY() TObjectPtr<USizeBox> PanelSize;
	UPROPERTY() TObjectPtr<UImage> Portrait;
	UPROPERTY() TObjectPtr<UWidget> PortraitBox;
	UPROPERTY() TObjectPtr<UWidget> MetersBox;
	UPROPERTY() TObjectPtr<UMaterialInstanceDynamic> PortraitMID;
	UPROPERTY() TObjectPtr<UBorder> NamePill;
	UPROPERTY() TObjectPtr<UTextBlock> NameText;
	UPROPERTY() TObjectPtr<UTextBlock> MaladyText;
	UPROPERTY() TObjectPtr<UTextBlock> TypingText;
	UPROPERTY() TObjectPtr<UWrapBox> WordWrap;
	UPROPERTY() TObjectPtr<UVerticalBox> ChoiceBox;
	UPROPERTY() TObjectPtr<UTextBlock> ContinueHint;
	UPROPERTY() TObjectPtr<UProgressBar> RomanceBar;
	UPROPERTY() TObjectPtr<UProgressBar> FriendBar;
	UPROPERTY() TObjectPtr<UProgressBar> FrictionBar;
	UPROPERTY() TObjectPtr<UVerticalBox> FloaterBox;
	UPROPERTY() TObjectPtr<UCanvasPanel> FxCanvas;
	UPROPERTY() TObjectPtr<UBorder> FadeCurtain;
	UPROPERTY() TObjectPtr<UTextBlock> FadeText;

	struct FFloater
	{
		TWeakObjectPtr<UWidget> Widget;
		float Age = 0.f;
		float Life = 1.5f;
		FVector2D Velocity = FVector2D::ZeroVector;
		FVector2D Pos = FVector2D::ZeroVector;
		bool bCanvas = false;
	};
	TArray<FFloater> Floaters;

	enum class EFxPhase : uint8 { None, FadeOut, Hold, FadeIn };
	EFxPhase FxPhase = EFxPhase::None;
	float FxTimer = 0.f;

	FDialogueView Current;
	TArray<FToken> Tokens;
	FString PlainText;
	float CharsShown = 0.f;
	int32 LastTypeTick = 0;
	bool bTyping = false;
	float HintBlink = 0.f;
	FVector2D ViewSize = FVector2D(1920.f, 1080.f);
	FString HunkId;
};
