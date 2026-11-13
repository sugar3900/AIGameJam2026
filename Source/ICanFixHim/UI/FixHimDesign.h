// Shared design tokens and scalable surface construction. No generated screen-specific art.
#pragma once
#include "CoreMinimal.h"
#include "Components/Border.h"
#include "Components/VerticalBox.h"
#include "FixHimDesign.generated.h"

class UImage;
class UWidgetTree;

namespace FixHimDesign
{
inline const FLinearColor Teal = FLinearColor::FromSRGBColor(FColor::FromHex(TEXT("1F7384")));
inline const FLinearColor Ink = FLinearColor::FromSRGBColor(FColor::FromHex(TEXT("11414A")));
inline const FLinearColor Cream = FLinearColor::FromSRGBColor(FColor::FromHex(TEXT("FFF5E5")));
inline const FLinearColor Orange = FLinearColor::FromSRGBColor(FColor::FromHex(TEXT("FF7900")));
inline const FLinearColor Pink = FLinearColor::FromSRGBColor(FColor::FromHex(TEXT("D9005C")));
/** Extrusions under pink and cream (orange-keyline) surfaces: darker than their keyline so the depth reads. */
inline const FLinearColor PinkDepth = FLinearColor::FromSRGBColor(FColor::FromHex(TEXT("99003F")));
inline const FLinearColor OrangeDepth = FLinearColor::FromSRGBColor(FColor::FromHex(TEXT("B35500"))); // keyline orange at 70% value, same hue
inline const FLinearColor Friendship = FLinearColor::FromSRGBColor(FColor::FromHex(TEXT("76CADB")));
inline const FLinearColor Disabled = FLinearColor::FromSRGBColor(FColor::FromHex(TEXT("E1E1DE")));
inline const FLinearColor DisabledInk = FLinearColor::FromSRGBColor(FColor::FromHex(TEXT("565C60")));
inline const FLinearColor Scrim = Ink.CopyWithNewOpacity(.72f);
inline constexpr float Slant = 0.2125565617f;        // tan(12 degrees)
// Text is set in upright faces and sheared the full 12 degrees, so glyphs and wrapped lines both follow the grid.
inline constexpr float DisplayShear = Slant;
/** Keyline (outline) widths. Buttons and plates use ButtonBorder; popup cards and panels use twice that. */
inline constexpr float ButtonBorder = 6.f, PopupBorder = 12.f;
/**
 * The extrusion matches the keyline: one layer, Border units down and half that sideways, so buttons and plates
 * get half the popups' depth. The face leaves DepthReserve(B) of its box for it.
 */
inline FVector2f DepthOffset(float Border) { return FVector2f(Border * .5f, Border); }
/** Popup-weight surfaces add a 50% ink shadow this far beyond their extrusion. */
inline constexpr bool HasShadow(float Border) { return Border >= PopupBorder; }
inline constexpr float ShadowExtraX = 3.f, ShadowExtraY = 6.f, ShadowOpacity = .5f;
inline FVector2f ShadowOffset(float Border) { return DepthOffset(Border) + FVector2f(ShadowExtraX, ShadowExtraY); }
inline constexpr float DepthReserveX(float Border) { return Border * .5f + 3.f + (HasShadow(Border) ? ShadowExtraX : 0.f); }
inline constexpr float DepthReserveY(float Border) { return Border + 3.f + (HasShadow(Border) ? ShadowExtraY : 0.f); }
/**
 * Vertical centring on slanted surfaces: the face excludes the extrusion reserve at the bottom, so text is centred
 * when bottom padding = top padding + Extrusion (button-weight plates). Barlow's line box (ascender 1.0 em,
 * descender 0.2 em) puts the capitals' centre 0.05 em below the box centre; CapCentre lifts labels by that much.
 */
inline constexpr float Extrusion = DepthReserveY(ButtonBorder), CapCentre = -.05f;
inline constexpr float HitHeight = 48.f;
inline constexpr int32 Caption = 16, Body = 22, Line = 26, Reply = 26, Label = 24, Heading = 36, Hero = 72;
ICANFIXHIM_API bool ReducedMotion();
ICANFIXHIM_API float TextScale();
ICANFIXHIM_API UImage *Icon(UWidgetTree *Tree, const FString &Name, const FLinearColor &Tint);
} // namespace FixHimDesign

/** A UBorder-compatible surface: its content is upright, only its painted contour slants. */
UCLASS()
class ICANFIXHIM_API UFixHimSurface : public UBorder
{
	GENERATED_BODY()
  public:
	bool bBorderless = false;
	/** Corner radius of a borderless surface (title backdrop: 22; interaction prompt: small, for crisp corners). */
	float BorderlessRadius = 22.f;
	/** Keyline width; raise to FixHimDesign::PopupBorder for popup cards and panels. */
	float BorderWidth = FixHimDesign::ButtonBorder;
  protected:
	virtual TSharedRef<SWidget> RebuildWidget() override;
};

/** Upright children whose anchors follow the same 12-degree columns as the surface. */
UCLASS()
class ICANFIXHIM_API UFixHimStack : public UVerticalBox
{
	GENERATED_BODY()
  protected:
	virtual TSharedRef<SWidget> RebuildWidget() override;
};
