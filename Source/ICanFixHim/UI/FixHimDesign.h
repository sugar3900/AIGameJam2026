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
inline const FLinearColor Friendship = FLinearColor::FromSRGBColor(FColor::FromHex(TEXT("76CADB")));
inline const FLinearColor Disabled = FLinearColor::FromSRGBColor(FColor::FromHex(TEXT("E1E1DE")));
inline const FLinearColor DisabledInk = FLinearColor::FromSRGBColor(FColor::FromHex(TEXT("565C60")));
inline const FLinearColor Scrim = Ink.CopyWithNewOpacity(.72f);
inline constexpr float Slant = 0.2125565617f;        // tan(12 degrees)
inline constexpr float DisplayShear = 0.0897720008f; // tan(12) - tan(7)
inline constexpr float HitHeight = 48.f;
inline constexpr int32 Caption = 16, Body = 22, Reply = 22, Label = 24, Heading = 36, Hero = 72;
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
