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

	/** Builds a styled pill button with a centred label. */
	static UFixHimButton* Make(UWidgetTree* Tree, const FString& Label, TFunction<void()> OnClick, int32 FontSize = 22, bool bPrimary = true);

	UTextBlock* Label = nullptr;

private:
	UFUNCTION()
	void HandleClicked();

	TFunction<void()> OnClick;
};

UCLASS()
class ICANFIXHIM_API UFixHimSlider : public USlider
{
	GENERATED_BODY()

public:
	void Init(TFunction<void(float)> InOnChanged);

private:
	UFUNCTION()
	void HandleChanged(float NewValue);

	TFunction<void(float)> OnChanged;
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

protected:
	virtual TSharedRef<SWidget> RebuildWidget() override;

	/** Create widgets and set WidgetTree->RootWidget. */
	virtual void BuildUI() PURE_VIRTUAL(UFixHimWidget::BuildUI, );

	/** A centred rounded card with a title, returned content box for children. */
	UVerticalBox* MakeCardScreen(const FString& Title, float Width = 520.f);
};
