// I Can Fix Him - AI Game Jam 2026

#include "UI/FixHimCards.h"
#include "Player/FixHimPlayerController.h"
#include "Audio/FixHimSfxSubsystem.h"
#include "World/FixHimHunk.h"
#include "Dialogue/DialogueTypes.h"
#include "Core/FixHimSettings.h"
#include "Core/FixHimSaveSubsystem.h"
#include "Blueprint/WidgetTree.h"
#include "Components/Border.h"
#include "Components/HorizontalBox.h"
#include "Components/HorizontalBoxSlot.h"
#include "Components/Image.h"
#include "Components/Overlay.h"
#include "Components/OverlaySlot.h"
#include "Components/SizeBox.h"
#include "Components/TextBlock.h"
#include "Components/VerticalBox.h"
#include "Components/VerticalBoxSlot.h"
#include "Engine/TextureRenderTarget2D.h"
#include "Engine/Texture2D.h"
#include "Materials/MaterialInstanceDynamic.h"
#include "Misc/Paths.h"

using namespace FixHimUI;

// ---------------------------------------------------------------------------
// Intro card

void UFixHimIntroCardWidget::BuildUI()
{
	UOverlay* Root = WidgetTree->ConstructWidget<UOverlay>();
	// Visible (not hit-test invisible) so a click anywhere on the card reaches NativeOnMouseButtonDown; the
	// children don't take clicks.
	Root->SetVisibility(ESlateVisibility::Visible);
	RootWidget = Root;
	WidgetTree->RootWidget = Root;

	UBorder* Dim = WidgetTree->ConstructWidget<UBorder>();
	Dim->SetBrushColor(FixHimDesign::Scrim);
	UOverlaySlot* DimSlot = Root->AddChildToOverlay(Dim);
	DimSlot->SetHorizontalAlignment(HAlign_Fill);
	DimSlot->SetVerticalAlignment(VAlign_Fill);

	// Two tilted colour bands sweeping across the screen.
	auto MakeBand = [&](const FLinearColor& Color, float Height, float Angle) -> UBorder*
	{
		USizeBox* Box = WidgetTree->ConstructWidget<USizeBox>();
		Box->SetHeightOverride(Height);
		Box->SetWidthOverride(3200.f);
		UBorder* B = WidgetTree->ConstructWidget<UFixHimSurface>();
		B->SetBrushColor(Color);
		Box->AddChild(B);
		// Slanted contour is shared; never rotate the complete band.
		UOverlaySlot* S = Root->AddChildToOverlay(Box);
		S->SetHorizontalAlignment(HAlign_Center);
		S->SetVerticalAlignment(VAlign_Center);
		return B;
	};
	// One shared teal contour; no second orange slab.
	Band = MakeBand(PlumSoft, 330.f, -12.f);

	UHorizontalBox* Row = WidgetTree->ConstructWidget<UHorizontalBox>();
	UOverlaySlot* RowSlot = Root->AddChildToOverlay(Row);
	RowSlot->SetHorizontalAlignment(HAlign_Center);
	RowSlot->SetVerticalAlignment(VAlign_Center);

	USizeBox* SilBox = WidgetTree->ConstructWidget<USizeBox>();
	SilBox->SetWidthOverride(420.f);
	SilBox->SetHeightOverride(420.f);
	Silhouette = WidgetTree->ConstructWidget<UImage>();
	auto *PortraitFrame=WidgetTree->ConstructWidget<UBorder>();
	PortraitFrame->SetBrush(Rounded(Plum,20,HotPink,4));
	PortraitFrame->SetPadding(FMargin(6));
	SilBox->AddChild(PortraitFrame); PortraitFrame->SetContent(Silhouette);
	Row->AddChildToHorizontalBox(SilBox)->SetVerticalAlignment(VAlign_Center);

	UVerticalBox* Col = WidgetTree->ConstructWidget<UFixHimStack>();
	USizeBox* TextSize=WidgetTree->ConstructWidget<USizeBox>(); TextSize->SetWidthOverride(1000); TextSize->AddChild(Col);
 UHorizontalBoxSlot* ColSlot = Row->AddChildToHorizontalBox(TextSize);
	ColSlot->SetVerticalAlignment(VAlign_Center);
	ColSlot->SetPadding(FMargin(30.f, 0.f, 0.f, 0.f));

	Kicker = MakeText(WidgetTree, TEXT("SOMETHING IN THIS HOUSE IS BROKEN..."), 26, Cream, TEXT("Bold"));
	Col->AddChildToVerticalBox(Kicker);
	MaladyName = MakeText(WidgetTree, TEXT("MALADY"),72, FLinearColor::White, TEXT("Display"));
	MaladyName->SetAutoWrapText(true);
 MaladyName->SetShadowOffset(FVector2D(6.f, 6.f));
	MaladyName->SetShadowColorAndOpacity(FLinearColor(Plum.R, Plum.G, Plum.B, 0.9f));
	Col->AddChildToVerticalBox(MaladyName)->SetPadding(FMargin(0.f, -10.f, 0.f, 0.f));
	Tagline = MakeText(WidgetTree, TEXT(""), 26, Cream, TEXT("Semibold"));
	Tagline->SetAutoWrapText(true);
 Col->AddChildToVerticalBox(Tagline);

	// "Click to continue" pill near the bottom, fading in once the card has landed.
	UBorder* HintPill = WidgetTree->ConstructWidget<UFixHimSurface>();
	HintPill->SetBrush(Rounded(Cream, 18.f));
	HintPill->SetPadding(FMargin(28.f, 8.f, 36.f, 8.f + FixHimDesign::Extrusion));
	Hint = MakeText(WidgetTree, TEXT("Continue  /  Enter"), 22, Plum, TEXT("Display"));
	HintPill->SetContent(Hint);
	HintPill->SetVisibility(ESlateVisibility::HitTestInvisible);
	HintPill->SetRenderOpacity(0.f);
	UOverlaySlot* HintSlot = Root->AddChildToOverlay(HintPill);
	HintSlot->SetHorizontalAlignment(HAlign_Center);
	HintSlot->SetVerticalAlignment(VAlign_Bottom);
	HintSlot->SetPadding(FMargin(0.f, 0.f, 0.f, 90.f));
	for (UWidget* W : { static_cast<UWidget*>(Dim), static_cast<UWidget*>(Row) })
	{
		W->SetVisibility(ESlateVisibility::HitTestInvisible);
	}
}

void UFixHimIntroCardWidget::Skip()
{
	if (Age < MinShowSeconds || bLeaving || bDone)
	{
		return;
	}
	bLeaving = true;
	LeaveAge = Age;
	FixHim::Sfx(this, "DialogueAdvance");
}

void UFixHimIntroCardWidget::ForceSkip()
{
	Age = FMath::Max(Age, MinShowSeconds);
	Skip();
}

FReply UFixHimIntroCardWidget::NativeOnMouseButtonDown(const FGeometry& InGeometry, const FPointerEvent& InMouseEvent)
{
	Skip();
	return FReply::Handled();
}

void UFixHimIntroCardWidget::Setup(const FHunkDefinition& Def, AFixHimHunk* Hunk, TFunction<void()> InOnFinished)
{
	OnFinished = MoveTemp(InOnFinished);
	FixHim::Sfx(this, "IntroCard");
	MaladyName->SetText(FText::FromString(Def.Malady.ToUpper()));
	Tagline->SetText(FText::FromString(Def.Tagline));
	Band->SetBrushColor(PlumSoft);

	if (Hunk)
	{
		Hunk->CapturePortraitNow();
		if (UMaterialInterface* Mat = UFixHimSettings::Get()->PortraitMaterial.LoadSynchronous())
		{
			UMaterialInstanceDynamic* MID = UMaterialInstanceDynamic::Create(Mat, this);
			MID->SetTextureParameterValue(TEXT("Portrait"), Hunk->GetPortrait());
			MID->SetScalarParameterValue(TEXT("Silhouette"),0.f);
			MID->SetScalarParameterValue(TEXT("Transparent"), 1.f);
			Silhouette->SetBrushFromMaterial(MID);
		}
		else
		{
			Silhouette->SetBrushResourceObject(Hunk->GetPortrait());
			Silhouette->SetColorAndOpacity(FLinearColor::Black);
		}
	}
 if(!Def.Portrait.IsEmpty())
 {
  FString Path=Def.Portrait;
  if(!Path.Contains(TEXT("."))) Path+=TEXT(".")+FPaths::GetBaseFilename(Path);
  if(auto* Painted=LoadObject<UTexture2D>(nullptr,*Path)) { Silhouette->SetBrushFromTexture(Painted); Silhouette->SetColorAndOpacity(FLinearColor::White); }
 }
 Age = 0.f;
 LeaveAge = 0.f;
	bLeaving = false;
	bDone = false;
}

void UFixHimIntroCardWidget::NativeTick(const FGeometry& MyGeometry, float InDeltaTime)
{
	Super::NativeTick(MyGeometry, InDeltaTime);
	Age += InDeltaTime;

	const bool Reduced=FixHimDesign::ReducedMotion();
 const float In=Reduced ? 1.f : EaseOutBack(Age/.45f);
	// Holds until clicked, then swoops out.
	const float Out = bLeaving ? FMath::Clamp((Age - LeaveAge) / OutSeconds, 0.f, 1.f) : 0.f;
	const float W = MyGeometry.GetLocalSize().X;

	if (Band)
	{
		Band->GetParent()->SetRenderTranslation(FVector2D(Reduced ? 0.f : FMath::Lerp(-W * 1.6f, 0.f, In) + Out * W * 1.6f, 0.f));
	}
	if (Band2)
	{
		const float In2=Reduced ? 1.f : EaseOutBack((Age-.08f)/.45f);
		Band2->GetParent()->SetRenderTranslation(FVector2D(Reduced ? 0.f : FMath::Lerp(W * 1.6f, 0.f, In2) - Out * W * 1.6f, 0.f));
	}
	if (Silhouette)
	{
		const float S=Reduced ? 1.f : EaseOutBack((Age-.2f)/.5f);
		Silhouette->SetRenderScale(FVector2D(Reduced ? 1.f : FMath::Max(0.01f, S * (1.f - Out))));
		Silhouette->SetRenderTransformAngle(0);
	}
	const float TextIn = FMath::Clamp((Age - 0.35f) / 0.3f, 0.f, 1.f);
	if (MaladyName)
	{
		MaladyName->SetRenderOpacity(TextIn * (1.f - Out));
		MaladyName->SetRenderScale(FVector2D(Reduced ? 1.f : FMath::Lerp(1.08f,1.f,FMath::Clamp((Age-.35f)/.4f,0.f,1.f))));
	}
	if (Kicker)
	{
		Kicker->SetRenderOpacity(FMath::Clamp(Age / 0.3f, 0.f, 1.f) * (1.f - Out));
	}
	if (Tagline)
	{
		Tagline->SetRenderOpacity(FMath::Clamp((Age - 0.9f) / 0.4f, 0.f, 1.f) * (1.f - Out));
	}
	if (Hint)
	{
		// Fade in, then a slow gentle pulse while waiting.
		const float HintIn = FMath::Clamp((Age - HintSeconds) / 0.4f, 0.f, 1.f);
		const float Pulse = Reduced ? 1.f : .75f+.25f*FMath::Sin((Age-HintSeconds)*3.f);
		if (UWidget* Pill = Hint->GetParent())
		{
			Pill->SetRenderOpacity(HintIn * Pulse * (1.f - Out));
		}
	}
	if (RootWidget)
	{
		RootWidget->SetRenderOpacity(1.f - Out * 0.8f);
	}

	if (!bDone && bLeaving && Out >= 1.f)
	{
		bDone = true;
		if (OnFinished)
		{
			OnFinished();
		}
	}
}

// ---------------------------------------------------------------------------
// Ending card

void UFixHimEndingCardWidget::BuildUI()
{
	UVerticalBox* Col = MakeCardScreen(TEXT(""), 880.f); // wide enough that the grid-stepped title keeps two lines
	OpenSfx = NAME_None; // the ending jingle covers it
	OutsideClickMinAge = 0.8f;
	Card = CardSurface;
	Col->ClearChildren();

	Kind = MakeText(WidgetTree, TEXT("ENDING"), 20, Pink, TEXT("Bold"));
	Kind->SetJustification(ETextJustify::Center);
	Col->AddChildToVerticalBox(Kind);

	Title = MakeText(WidgetTree, TEXT("Title"), 44, HotPink, TEXT("Display"));
	Title->SetJustification(ETextJustify::Center);
	Title->SetAutoWrapText(true);
	Col->AddChildToVerticalBox(Title)->SetPadding(FMargin(0.f, 4.f, 0.f, 14.f));

	Body = MakeText(WidgetTree, TEXT(""), 22, Plum);
	Body->SetJustification(ETextJustify::Center);
	Body->SetAutoWrapText(true);
	Col->AddChildToVerticalBox(Body)->SetPadding(FMargin(0.f, 0.f, 0.f, 16.f));

	Progress = MakeText(WidgetTree, TEXT(""), 18, PlumSoft, TEXT("Italic"));
	Progress->SetJustification(ETextJustify::Center);
	Progress->SetAutoWrapText(true);
	Col->AddChildToVerticalBox(Progress)->SetPadding(FMargin(0.f, 0.f, 0.f, 18.f));

	TWeakObjectPtr<UFixHimEndingCardWidget> Self(this);
	USizeBox* Box = WidgetTree->ConstructWidget<USizeBox>();
	Box->SetMinDesiredHeight(72.f);
	Box->AddChild(UFixHimButton::Make(WidgetTree, TEXT("Continue"), [Self]() { if (Self.IsValid() && Self->GetFixHimPC()) { Self->GetFixHimPC()->CloseEndingCard(); } }, 22, true));
	CardActions->AddChildToVerticalBox(Box);
}

void UFixHimEndingCardWidget::Setup(const FHunkDefinition& Def, const FString& EndingId, int32 FixedCount, int32 TotalCount)
{
	FString KindText;
	FLinearColor KindColor = Pink;
	if (EndingId == TEXT("romance_success")) { KindText = TEXT("ROMANCE  -  HAPPILY EVER AFTER"); KindColor = HotPink; }
	else if (EndingId == TEXT("romance_failure")) { KindText = TEXT("ROMANCE  -  IT'S NOT ME, IT'S YOUR FOUNDATION"); KindColor = Plum; }
	else if (EndingId == TEXT("friend_success")) { KindText = TEXT("FRIENDSHIP  -  BESTIES"); KindColor = PlumSoft; }
	else { KindText = TEXT("FRIENDSHIP  -  SWORN ENEMIES"); KindColor = Plum; }

	FixHim::Sfx(this, EndingId == TEXT("romance_success") ? "EndingRomance" : EndingId == TEXT("friend_success") ? "EndingFriend" : "EndingFail");
	Kind->SetText(FText::FromString(KindText));
	Kind->SetColorAndOpacity(FSlateColor(KindColor));

	const FHunkEnding* Ending = Def.Endings.Find(EndingId);
	Title->SetText(FText::FromString(Ending ? Ending->Title : Def.Name));
	const UFixHimSaveSubsystem* SaveSub = UFixHimSaveSubsystem::Get(this);
	const FString PlayerName = SaveSub ? SaveSub->GetPlayerName() : UFixHimSettings::Get()->PlayerName;
	Body->SetText(FText::FromString(Ending ? Ending->Text.Replace(TEXT("{player}"), *PlayerName) : FString()));

	// The house tally gets its own line, with non-breaking spaces so it never splits.
	FString Tally = FString::Printf(TEXT("The house is %d / %d fixed."), FixedCount, TotalCount);
	Tally.ReplaceInline(TEXT(" "), TEXT("\u00A0"));
	const FString Fixed = FString::Printf(TEXT("%s repaired.\n%s"), *Def.Malady, *Tally);
	Progress->SetText(FText::FromString(FixedCount >= TotalCount ? Fixed + TEXT("\nEvery man in this house has been fixed. Or at least seen. Home sweet home.") : Fixed));
	Age = 0.f;
}

bool UFixHimEndingCardWidget::HandleClickOutside()
{
	if (AFixHimPlayerController* PC = GetFixHimPC())
	{
		PC->CloseEndingCard();
		return true;
	}
	return false;
}

void UFixHimEndingCardWidget::NativeTick(const FGeometry& MyGeometry, float InDeltaTime)
{
	Super::NativeTick(MyGeometry, InDeltaTime);
	Age += InDeltaTime;
	if (Card)
	{
		const float S=FixHimDesign::ReducedMotion() ? 1.f : FMath::Lerp(.96f,1.f,FMath::Clamp(Age/.2f,0.f,1.f));
		Card->SetRenderScale(FVector2D(FMath::Max(0.01f, S)));
	}
}
