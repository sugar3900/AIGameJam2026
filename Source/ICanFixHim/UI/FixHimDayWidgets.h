// I Can Fix Him - AI Game Jam 2026
//
// Widgets for the week-by-week flow: the radio podcast overlay, the
// fade-to-black week card, and the end-of-game keepsake screen.

#pragma once

#include "CoreMinimal.h"
#include "UI/FixHimUI.h"
#include "Dialogue/DialogueTypes.h"
#include "FixHimDayWidgets.generated.h"

class UBorder;
class UImage;
class UTextBlock;
class UVerticalBox;
class USizeBox;
class UTextureRenderTarget2D;
class AFixHimHunk;

/**
 * Non-blocking "ON AIR" caption panel. Plays one podcast episode line by line
 * while the player keeps exploring, then calls OnFinished.
 */
UCLASS()
class ICANFIXHIM_API UFixHimRadioWidget : public UFixHimWidget
{
	GENERATED_BODY()

public:
	void Play(const FString& ShowName, const FDialogueNode& Episode, TFunction<void()> InOnFinished);
	void Stop();
	bool IsPlaying() const { return bPlaying; }

protected:
	virtual void BuildUI() override;
	virtual void NativeTick(const FGeometry& MyGeometry, float InDeltaTime) override;

private:
	void ShowLine(int32 Index);

	UPROPERTY() TObjectPtr<UBorder> Panel;
	UPROPERTY() TObjectPtr<UTextBlock> Header;
	UPROPERTY() TObjectPtr<UTextBlock> Speaker;
	UPROPERTY() TObjectPtr<UTextBlock> Line;
	UPROPERTY() TObjectPtr<UBorder> OnAirDot;

	TArray<FDialogueLine> Lines;
	TFunction<void()> OnFinished;
	int32 LineIndex = 0;
	float LineTimer = 0.f;
	float LineDuration = 0.f;
	float Age = 0.f;
	bool bPlaying = false;
};

/**
 * Full-screen fade: (optional fade to black) -> midpoint callback -> title card -> fade back in -> done.
 * Used for "Week 2", the inspection-day card and the start of the game.
 */
UCLASS()
class ICANFIXHIM_API UFixHimTransitionWidget : public UFixHimWidget
{
	GENERATED_BODY()

public:
	void Play(const FString& Title, const FString& Subtitle, bool bStartBlack, bool bFadeBackIn, TFunction<void()> InOnMidpoint, TFunction<void()> InOnDone);
	bool IsPlaying() const { return Phase != EPhase::Idle; }

protected:
	virtual void BuildUI() override;
	virtual void NativeTick(const FGeometry& MyGeometry, float InDeltaTime) override;

private:
	enum class EPhase : uint8 { Idle, FadeOut, Card, FadeIn };

	UPROPERTY() TObjectPtr<UBorder> Curtain;
	UPROPERTY() TObjectPtr<UTextBlock> TitleText;
	UPROPERTY() TObjectPtr<UTextBlock> SubtitleText;

	TFunction<void()> OnMidpoint;
	TFunction<void()> OnDone;
	EPhase Phase = EPhase::Idle;
	float Timer = 0.f;
	bool bFadeIn = true;
};

/** One love interest the player ended up with romantically. */
struct FFixHimKeepsakeEntry
{
	FString HunkId;
	FString Name;
	FString EndingTitle;
	TWeakObjectPtr<AFixHimHunk> Hunk;
};

/** After the epilogue: "Want to see him?" then a big portrait, then back to the title. */
UCLASS()
class ICANFIXHIM_API UFixHimKeepsakeWidget : public UFixHimWidget
{
	GENERATED_BODY()

public:
	void Setup(const TArray<FFixHimKeepsakeEntry>& InEntries);
	void ShowChooser();
	void ShowPortrait(int32 Index);

protected:
	virtual void BuildUI() override;
	virtual void NativeTick(const FGeometry& MyGeometry, float InDeltaTime) override;

private:

	UPROPERTY() TObjectPtr<UVerticalBox> Content;
	UPROPERTY() TObjectPtr<UBorder> Card;
	UPROPERTY() TObjectPtr<UTextureRenderTarget2D> KeepsakeTarget;

	TArray<FFixHimKeepsakeEntry> Entries;
	float Age = 0.f;
};
