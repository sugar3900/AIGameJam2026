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

/** First-meeting splash: the house problem's name and the hunk's silhouette swoop in, then vanish. */
UCLASS()
class ICANFIXHIM_API UFixHimIntroCardWidget : public UFixHimWidget
{
	GENERATED_BODY()

public:
	void Setup(const FHunkDefinition& Def, AFixHimHunk* Hunk, TFunction<void()> InOnFinished);

	static constexpr float Duration = 3.4f;

protected:
	virtual void BuildUI() override;
	virtual void NativeTick(const FGeometry& MyGeometry, float InDeltaTime) override;

private:
	UPROPERTY() TObjectPtr<UBorder> Band;
	UPROPERTY() TObjectPtr<UBorder> Band2;
	UPROPERTY() TObjectPtr<UImage> Silhouette;
	UPROPERTY() TObjectPtr<UTextBlock> Kicker;
	UPROPERTY() TObjectPtr<UTextBlock> MaladyName;
	UPROPERTY() TObjectPtr<UTextBlock> Tagline;
	UPROPERTY() TObjectPtr<UWidget> RootWidget;

	TFunction<void()> OnFinished;
	float Age = 0.f;
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

private:
	UPROPERTY() TObjectPtr<UTextBlock> Kind;
	UPROPERTY() TObjectPtr<UTextBlock> Title;
	UPROPERTY() TObjectPtr<UTextBlock> Body;
	UPROPERTY() TObjectPtr<UTextBlock> Progress;
	UPROPERTY() TObjectPtr<UBorder> Card;
	float Age = 0.f;
};
