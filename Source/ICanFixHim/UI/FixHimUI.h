// I Can Fix Him - AI Game Jam 2026
//
// Code-built UMG. Every screen is a UFixHimWidget subclass that assembles its
// widget tree in BuildUI(), so the whole UI lives in reviewable, diffable C++.

#pragma once

#include "CoreMinimal.h"
#include "UI/FixHimDesign.h"
#include "Blueprint/UserWidget.h"
#include "Components/Button.h"
#include "Components/Slider.h"
#include "Components/CheckBox.h"
#include "Styling/SlateTypes.h"
#include "FixHimUI.generated.h"

class UTextBlock;
class UImage;
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

// Compatibility names for existing screens; all resolve to the shared selected palette.
inline const FLinearColor Pink = FixHimDesign::Pink;
inline const FLinearColor HotPink = FixHimDesign::Pink;
inline const FLinearColor Blush = FixHimDesign::Friendship;
inline const FLinearColor Cream = FixHimDesign::Cream;
inline const FLinearColor Plum = FixHimDesign::Ink;
inline const FLinearColor PlumSoft = FixHimDesign::Teal;
inline const FLinearColor Gold = FixHimDesign::Orange;
inline const FLinearColor Mint = FixHimDesign::Friendship;
inline const FLinearColor Ember = FixHimDesign::Orange;
inline const FLinearColor Blueprint = FixHimDesign::Teal;

ICANFIXHIM_API FSlateFontInfo Font(int32 Size, const TCHAR *Typeface = TEXT("Regular"));
ICANFIXHIM_API FSlateBrush Rounded(const FLinearColor &Fill, float Radius,
                                   const FLinearColor &Outline = FLinearColor::Transparent, float OutlineWidth = 0.f);
ICANFIXHIM_API FButtonStyle ButtonStyle(const FLinearColor &Normal, const FLinearColor &Hovered,
                                        const FLinearColor &Pressed, float Radius = 14.f,
                                        const FLinearColor &Outline = FLinearColor::Transparent);

ICANFIXHIM_API UTextBlock *MakeText(UWidgetTree *Tree, const FString &Text, int32 Size, const FLinearColor &Color,
                                    const TCHAR *Typeface = TEXT("Regular"));
} // namespace FixHimUI

UENUM()
enum class EFixHimButtonVariant : uint8
{
	Primary,
	Secondary,
	Reply,
	Topic,
	Spatial
};

/** UButton with a native lambda click handler (dynamic delegates can't capture). */
UCLASS()
class ICANFIXHIM_API UFixHimButton : public UButton
{
	GENERATED_BODY()

  public:
	void Init(TFunction<void()> InOnClick);

	/** Sound played on click (see Audio/FixHimSfxSubsystem); Make() picks ButtonBack for "Back"/"Cancel"/"Close"
	 * labels. */
	FName ClickSfx = TEXT("ButtonClick");

	/** Builds a styled pill button with a centred label. */
	static UFixHimButton *Make(UWidgetTree *Tree, const FString &Label, TFunction<void()> OnClick, int32 FontSize = 22,
	                           bool bPrimary = true, const FString &LeadingIcon = FString());
	/**
	 * Large standalone button for menus that sit straight on the scene (title): taller face, a StandaloneLabel
	 * label, a bigger icon and the popup-weight 50% ink shadow, since there is no panel underneath.
	 */
	static UFixHimButton *MakeStandalone(UWidgetTree *Tree, const FString &Label, TFunction<void()> OnClick,
	                                     bool bPrimary, const FString &LeadingIcon);

	UPROPERTY() TObjectPtr<UTextBlock> Label;
	/** Leading icon, if any. Orange on cream faces, white on pink, disabled ink when disabled (see GetIconTint). */
	UPROPERTY() TObjectPtr<UImage> LeadingIcon;
	bool bStandalone = false;
	bool bDesignSurface = false;
	bool bInlineTopic = false;
	EFixHimButtonVariant Variant = EFixHimButtonVariant::Spatial;
	bool bPrimary = true;
	bool bSelected = false;
	int32 LabelSize = 22;
	bool bPreviewPressed = false; // component review only
	void SetVariant(bool Primary, bool Selected = false);
	void SetVariant(EFixHimButtonVariant InVariant);

  protected:
	virtual TSharedRef<SWidget> RebuildWidget() override;

  private:
	UFUNCTION()
	FLinearColor GetIconTint();
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
	void ApplyBigStyle(const FLinearColor &Track, const FLinearColor &Handle);
	static constexpr float BigHitHeight = 48.f;

  protected:
	virtual TSharedRef<SWidget> RebuildWidget() override;

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

  protected:
	virtual TSharedRef<SWidget> RebuildWidget() override;

  private:
	UFUNCTION()
	void HandleChanged(bool bChecked);

	TFunction<void(bool)> OnChanged;
};

/** Base for code-built screens. */
UCLASS(Abstract)
class ICANFIXHIM_API UFixHimWidget : public UUserWidget
{
	friend class FFixHimDesignSystemTest;
	GENERATED_BODY()

  public:
	AFixHimPlayerController *GetFixHimPC() const;

	/**
	 * Automation (FixHimClickAt): acts as a left click at an absolute (Slate desktop) position, hit-testing this
	 * screen's own widgets by their cached geometry. A slider / button / check box under the point gets the real Slate
	 * mouse down + up (so the hit box and click-to-jump are the shipped behaviour); otherwise it is a click on the
	 * screen itself (click outside the card closes it, etc.). Returns what happened, for the log.
	 */
	virtual FString SimulateClickAt(const FVector2D &ScreenPos);

  protected:
	virtual TSharedRef<SWidget> RebuildWidget() override;
	virtual void NativeConstruct() override;
	virtual void NativeDestruct() override;
	virtual void NativeTick(const FGeometry &MyGeometry, float InDeltaTime) override;
	virtual FReply NativeOnKeyDown(const FGeometry &Geometry, const FKeyEvent &Event) override;

	/** Sounds for the card pop-in / dismissal (card screens only); screens with their own cues can change these. */
	FName OpenSfx = TEXT("ModalOpen");
	FName CloseSfx = TEXT("ModalClose");

	/** Create widgets and set WidgetTree->RootWidget. */
	virtual void BuildUI() PURE_VIRTUAL(UFixHimWidget::BuildUI, );

	/**
	 * Click-outside-to-close for popups: a left click that lands outside GetOutsideClickCard() (the MakeCardScreen card
	 * by default) calls this. Do what the popup's Back / Close / Cancel button does and return true; the default does
	 * nothing (screens that need a decision, the dialogue box, the HUD). Ignored for OutsideClickMinAge seconds after
	 * the screen appears, so the click that opened it (or a double click) can't close it straight away.
	 */
	virtual bool HandleClickOutside()
	{
		return false;
	}
	virtual UWidget *GetOutsideClickCard() const
	{
		return PopCard;
	}
	float OutsideClickMinAge = 0.3f;
	/** Seconds since the widget was last added to the screen. */
	float ShownAge = 0.f;

	/** Optional preferred initial action, for example Continue when a save exists. */
	UPROPERTY() TObjectPtr<UWidget> InitialFocusTarget;

	virtual FReply NativeOnMouseButtonDown(const FGeometry &InGeometry, const FPointerEvent &InMouseEvent) override;

	/** Fixed actions outside the scrolling card body. */
	UPROPERTY() TObjectPtr<UVerticalBox> CardActions;

	/** A centred rounded card with a title, returned content box for children. */
	UVerticalBox *MakeCardScreen(const FString &Title, float Width = 520.f);

	/** The cream surface built by MakeCardScreen. */
	UPROPERTY() TObjectPtr<UBorder> CardSurface;

	/**
	 * Wraps a slanted surface so a teal title plate straddles its top edge: the plate's face is centred vertically
	 * on that edge and inset equally from both slanted sides. Surface padding grows to clear the plate. Returns the
	 * widget to place in the layout (the surface alone when Title is empty).
	 */
	UWidget *MakeHeaderedSurface(UBorder *Surface, const FString &Title, const FMargin &Padding);
	/** As above with a custom header row; Inset is the space kept from each slanted side at the top edge. */
	UWidget *MakeHeaderedSurface(UBorder *Surface, UWidget *Header, const FMargin &Padding, float Inset = 36.f);

  private:
	/** The card from MakeCardScreen; it grows in with a small overshoot every time the widget is shown. */
	UPROPERTY() TObjectPtr<UWidget> PopCard;
	float PopAge = 0.f;

	struct FHeaderLayout
	{
		TWeakObjectPtr<UWidget> Header;
		TWeakObjectPtr<UBorder> Surface;
		FMargin Padding;
		float Inset = 36.f;
		/** Balance left/right padding so 12-degree stack rows centre on the slanted face (card screens). */
		bool bCentreRows = false;
		FVector2D Measured = FVector2D(-1, -1);
	};
	TArray<FHeaderLayout> HeaderLayouts;
	/** Re-fits straddling headers to their measured plate and surface sizes (text size and content can change).
	 * Returns true if anything moved. */
	bool SyncHeaderLayouts();
	/** The pop card stays invisible until its layout (wrapping, header fit) stops changing, then pops in. */
	bool bPopSettled = false;
	int32 PopStableFrames = 0;
	FVector2D PopLastSize = FVector2D::ZeroVector;
	bool bInitialFocus = false;
};
