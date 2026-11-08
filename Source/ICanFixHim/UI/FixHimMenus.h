// I Can Fix Him - AI Game Jam 2026

#pragma once

#include "CoreMinimal.h"
#include "UI/FixHimUI.h"
#include "FixHimMenus.generated.h"

class UFixHimButton;

UCLASS()
class ICANFIXHIM_API UFixHimTitleWidget : public UFixHimWidget
{
	GENERATED_BODY()

public:
	void RefreshContinue();

protected:
	virtual void BuildUI() override;
	virtual void NativeTick(const FGeometry& MyGeometry, float InDeltaTime) override;

private:
	UPROPERTY() TObjectPtr<UFixHimButton> ContinueButton;
	UPROPERTY() TObjectPtr<UWidget> TitleBlock;
	float Age = 0.f;
};

/** New Game: "What's your name?" The Move In button is greyed out until something is typed. */
UCLASS()
class ICANFIXHIM_API UFixHimNameEntryWidget : public UFixHimWidget
{
	GENERATED_BODY()

protected:
	virtual void BuildUI() override;
	virtual void NativeConstruct() override;

private:
	UFUNCTION() void HandleTextChanged(const FText& Text);
	UFUNCTION() void HandleTextCommitted(const FText& Text, ETextCommit::Type CommitMethod);
	void Submit();
	FString CurrentName() const;

	UPROPERTY() TObjectPtr<class UEditableTextBox> NameBox;
	UPROPERTY() TObjectPtr<UFixHimButton> MoveInButton;
};

UCLASS()
class ICANFIXHIM_API UFixHimPauseWidget : public UFixHimWidget
{
	GENERATED_BODY()

protected:
	virtual void BuildUI() override;
};

/** Popup from clicking the front door: End Day or Cancel. */
UCLASS()
class ICANFIXHIM_API UFixHimDoorPromptWidget : public UFixHimWidget
{
	GENERATED_BODY()

public:
	/** Enables or disables End Day (and explains why) from the controller's current state. */
	void Refresh();

protected:
	virtual void BuildUI() override;

private:
	UPROPERTY() TObjectPtr<UFixHimButton> EndDayButton;
	UPROPERTY() TObjectPtr<UTextBlock> BodyText;
};

UCLASS()
class ICANFIXHIM_API UFixHimOptionsWidget : public UFixHimWidget
{
	GENERATED_BODY()

protected:
	virtual void BuildUI() override;
};

UCLASS()
class ICANFIXHIM_API UFixHimCreditsWidget : public UFixHimWidget
{
	GENERATED_BODY()

protected:
	virtual void BuildUI() override;
};
