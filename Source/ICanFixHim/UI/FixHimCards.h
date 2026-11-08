// I Can Fix Him - AI Game Jam 2026

#pragma once

#include "CoreMinimal.h"
#include "UI/FixHimUI.h"
#include "FixHimCards.generated.h"

class UBorder;
class UImage;
class UTextBlock;
class UWidget;
class AFixHimHunk;
struct FHunkDefinition;

/**
 * First-meeting splash: the house problem's name and the hunk's silhouette swoop in and stay until the player clicks
 * (a "click to continue" hint fades in), then swoop out. Clicks in the first MinShowSeconds are ignored so a
 * double-click on the fixture can't skip it by accident.
 */
UCLASS()
class ICANFIXHIM_API UFixHimIntroCardWidget : public UFixHimWidget
{
	GENERATED_BODY()

public:
	void Setup(const FHunkDefinition& Def, AFixHimHunk* Hunk, TFunction<void()> InOnFinished);

	static constexpr float MinShowSeconds = 0.5f;
	static constexpr float OutSeconds = 0.4f;
	/** When the "click to continue" hint starts fading in. */
	static constexpr float HintSeconds = 1.2f;

	/** Click (or key) to continue: starts the exit swoop, then finishes. Ignored for the first MinShowSeconds. */
	void Skip();
	/** Ignores MinShowSeconds (automation). */
	void ForceSkip();
	bool IsWaitingForClick() const { return !bLeaving && !bDone; }

protected:
	virtual void BuildUI() override;
	virtual void NativeTick(const FGeometry& MyGeometry, float InDeltaTime) override;
	virtual FReply NativeOnMouseButtonDown(const FGeometry& InGeometry, const FPointerEvent& InMouseEvent) override;

private:
	UPROPERTY() TObjectPtr<UBorder> Band;
	UPROPERTY() TObjectPtr<UBorder> Band2;
	UPROPERTY() TObjectPtr<UImage> Silhouette;
	UPROPERTY() TObjectPtr<UTextBlock> Kicker;
	UPROPERTY() TObjectPtr<UTextBlock> MaladyName;
	UPROPERTY() TObjectPtr<UTextBlock> Tagline;
	UPROPERTY() TObjectPtr<UTextBlock> Hint;
	UPROPERTY() TObjectPtr<UWidget> RootWidget;

	TFunction<void()> OnFinished;
	float Age = 0.f;
	float LeaveAge = 0.f;
	bool bLeaving = false;
	bool bDone = false;
};

/** Shown when an arc concludes. */
UCLASS()
class ICANFIXHIM_API UFixHimEndingCardWidget : public UFixHimWidget
{
	GENERATED_BODY()

public:
	void Setup(const FHunkDefinition& Def, const FString& EndingId, int32 FixedCount, int32 TotalCount);

protected:
	virtual void BuildUI() override;
	virtual void NativeTick(const FGeometry& MyGeometry, float InDeltaTime) override;
	/** Click outside = Continue (after a short beat, so the click that ended the conversation can't skip it). */
	virtual bool HandleClickOutside() override;

private:
	UPROPERTY() TObjectPtr<UTextBlock> Kind;
	UPROPERTY() TObjectPtr<UTextBlock> Title;
	UPROPERTY() TObjectPtr<UTextBlock> Body;
	UPROPERTY() TObjectPtr<UTextBlock> Progress;
	UPROPERTY() TObjectPtr<UBorder> Card;
	float Age = 0.f;
};
