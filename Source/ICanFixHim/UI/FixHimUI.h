// I Can Fix Him - AI Game Jam 2026
//
// Code-built UMG. Every screen is a UFixHimWidget subclass that assembles its
// widget tree in BuildUI(), so the whole UI lives in reviewable, diffable C++.

#pragma once

#include "CoreMinimal.h"
#include "Blueprint/UserWidget.h"
#include "Components/Button.h"
#include "Components/Slider.h"
#include "Components/CheckBox.h"
#include "Styling/SlateTypes.h"
#include "FixHimUI.generated.h"

class UTextBlock;
class UBorder;
class UVerticalBox;
class UWidgetTree;
class AFixHimPlayerController;

namespace FixHimUI
{
	inline float EaseOutBack(float T)
	{
		const float C1 = 1.70158f;
		const float C3 = C1 + 1.f;
		T = FMath::Clamp(T, 0.f, 1.f);
		return 1.f + C3 * FMath::Pow(T - 1.f, 3.f) + C1 * FMath::Pow(T - 1.f, 2.f);
	}

	// Palette: flirty pink renovation chic.
	inline const FLinearColor Pink = FLinearColor::FromSRGBColor(FColor(0xFF, 0x5C, 0xA8));
	inline const FLinearColor HotPink = FLinearColor::FromSRGBColor(FColor(0xFF, 0x2E, 0x88));
	inline const FLinearColor Blush = FLinearColor::FromSRGBColor(FColor(0xFF, 0xD6, 0xE8));
	inline const FLinearColor Cream = FLinearColor::FromSRGBColor(FColor(0xFF, 0xF7, 0xF0));
	inline const FLinearColor Plum = FLinearColor::FromSRGBColor(FColor(0x3B, 0x14, 0x34));
	inline const FLinearColor PlumSoft = FLinearColor::FromSRGBColor(FColor(0x6E, 0x3A, 0x64));
	inline const FLinearColor Gold = FLinearColor::FromSRGBColor(FColor(0xFF, 0xC8, 0x57));
	inline const FLinearColor Mint = FLinearColor::FromSRGBColor(FColor(0x5F, 0xD3, 0xB4));
	inline const FLinearColor Ember = FLinearColor::FromSRGBColor(FColor(0xFF, 0x7A, 0x45));
	inline const FLinearColor Blueprint = FLinearColor::FromSRGBColor(FColor(0x1E, 0x3A, 0x6E));

	ICANFIXHIM_API FSlateFontInfo Font(int32 Size, const TCHAR* Typeface = TEXT("Regular"));
	ICANFIXHIM_API FSlateBrush Rounded(const FLinearColor& Fill, float Radius, const FLinearColor& Outline = FLinearColor::Transparent, float OutlineWidth = 0.f);
	ICANFIXHIM_API FButtonStyle ButtonStyle(const FLinearColor& Normal, const FLinearColor& Hovered, const FLinearColor& Pressed, float Radius = 14.f, const FLinearColor& Outline = FLinearColor::Transparent);

	ICANFIXHIM_API UTextBlock* MakeText(UWidgetTree* Tree, const FString& Text, int32 Size, const FLinearColor& Color, const TCHAR* Typeface = TEXT("Regular"));
}

/** UButton with a native lambda click handler (dynamic delegates can't capture). */
UCLASS()
class ICANFIXHIM_API UFixHimButton : public UButton
{
	GENERATED_BODY()

public:
	void Init(TFunction<void()> InOnClick);

	/** Sound played on click (see Audio/FixHimSfxSubsystem); Make() picks ButtonBack for "Back"/"Cancel"/"Close" labels. */
	FName ClickSfx = TEXT("ButtonClick");

	/** Builds a styled pill button with a centred label. */
	static UFixHimButton* Make(UWidgetTree* Tree, const FString& Label, TFunction<void()> OnClick, int32 FontSize = 22, bool bPrimary = true);

	UTextBlock* Label = nullptr;

private:
	UFUNCTION()
	void HandleClicked();
	UFUNCTION()
	void HandleHovered();

	TFunction<void()> OnClick;
};

UCLASS()
class ICANFIXHIM_API UFixHimSlider : public USlider
{
	GENERATED_BODY()

public:
	void Init(TFunction<void(float)> InOnChanged);

	/**
	 * Big, easy-to-grab look for menus: a thick rounded track and a large round handle. Wrap the slider in a box at
	 * least BigHitHeight tall (and fill it vertically) so the whole row height is clickable; a click anywhere on the
	 * track jumps the value there and keeps dragging (SSlider behaviour).
	 */
	void ApplyBigStyle(const FLinearColor& Track, const FLinearColor& Handle);
	static constexpr float BigHitHeight = 48.f;

private:
	UFUNCTION()
	void HandleChanged(float NewValue);

	TFunction<void(float)> OnChanged;
	int32 LastTickStep = INDEX_NONE;
};

UCLASS()
class ICANFIXHIM_API UFixHimCheckBox : public UCheckBox
{
	GENERATED_BODY()

public:
	void Init(TFunction<void(bool)> InOnChanged);

private:
	UFUNCTION()
	void HandleChanged(bool bChecked);

	TFunction<void(bool)> OnChanged;
};

/** Base for code-built screens. */
UCLASS(Abstract)
class ICANFIXHIM_API UFixHimWidget : public UUserWidget
{
	GENERATED_BODY()

public:
	AFixHimPlayerController* GetFixHimPC() const;

	/**
	 * Automation (FixHimClickAt): acts as a left click at an absolute (Slate desktop) position, hit-testing this screen's
	 * own widgets by their cached geometry. A slider / button / check box under the point gets the real Slate mouse
	 * down + up (so the hit box and click-to-jump are the shipped behaviour); otherwise it is a click on the screen
	 * itself (click outside the card closes it, etc.). Returns what happened, for the log.
	 */
	virtual FString SimulateClickAt(const FVector2D& ScreenPos);

protected:
	virtual TSharedRef<SWidget> RebuildWidget() override;
	virtual void NativeConstruct() override;
	virtual void NativeDestruct() override;
	virtual void NativeTick(const FGeometry& MyGeometry, float InDeltaTime) override;

	/** Sounds for the card pop-in / dismissal (card screens only); screens with their own cues can change these. */
	FName OpenSfx = TEXT("ModalOpen");
	FName CloseSfx = TEXT("ModalClose");

	/** Create widgets and set WidgetTree->RootWidget. */
	virtual void BuildUI() PURE_VIRTUAL(UFixHimWidget::BuildUI, );

	/**
	 * Click-outside-to-close for popups: a left click that lands outside GetOutsideClickCard() (the MakeCardScreen card
	 * by default) calls this. Do what the popup's Back / Close / Cancel button does and return true; the default does
	 * nothing (screens that need a decision, the dialogue box, the HUD). Ignored for OutsideClickMinAge seconds after the
	 * screen appears, so the click that opened it (or a double click) can't close it straight away.
	 */
	virtual bool HandleClickOutside() { return false; }
	virtual UWidget* GetOutsideClickCard() const { return PopCard; }
	float OutsideClickMinAge = 0.3f;
	/** Seconds since the widget was last added to the screen. */
	float ShownAge = 0.f;

	virtual FReply NativeOnMouseButtonDown(const FGeometry& InGeometry, const FPointerEvent& InMouseEvent) override;

	/** A centred rounded card with a title, returned content box for children. */
	UVerticalBox* MakeCardScreen(const FString& Title, float Width = 520.f);

private:
	/** The card from MakeCardScreen; it grows in with a small overshoot every time the widget is shown. */
	UPROPERTY() TObjectPtr<UWidget> PopCard;
	float PopAge = 0.f;
};
