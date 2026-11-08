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
#include "Materials/MaterialInstanceDynamic.h"

using namespace FixHimUI;

// ---------------------------------------------------------------------------
// Intro card

void UFixHimIntroCardWidget::BuildUI()
{
	UOverlay* Root = WidgetTree->ConstructWidget<UOverlay>();
	Root->SetVisibility(ESlateVisibility::HitTestInvisible);
	RootWidget = Root;
	WidgetTree->RootWidget = Root;

	UBorder* Dim = WidgetTree->ConstructWidget<UBorder>();
	Dim->SetBrushColor(FLinearColor(0.08f, 0.f, 0.06f, 0.6f));
	UOverlaySlot* DimSlot = Root->AddChildToOverlay(Dim);
	DimSlot->SetHorizontalAlignment(HAlign_Fill);
	DimSlot->SetVerticalAlignment(VAlign_Fill);

	// Two tilted colour bands sweeping across the screen.
	auto MakeBand = [&](const FLinearColor& Color, float Height, float Angle) -> UBorder*
	{
		USizeBox* Box = WidgetTree->ConstructWidget<USizeBox>();
		Box->SetHeightOverride(Height);
		Box->SetWidthOverride(3200.f);
		UBorder* B = WidgetTree->ConstructWidget<UBorder>();
		B->SetBrushColor(Color);
		Box->AddChild(B);
		Box->SetRenderTransformAngle(Angle);
		UOverlaySlot* S = Root->AddChildToOverlay(Box);
		S->SetHorizontalAlignment(HAlign_Center);
		S->SetVerticalAlignment(VAlign_Center);
		return B;
	};
	Band2 = MakeBand(Gold, 380.f, -9.f);
	Band = MakeBand(HotPink, 330.f, -7.f);

	UHorizontalBox* Row = WidgetTree->ConstructWidget<UHorizontalBox>();
	UOverlaySlot* RowSlot = Root->AddChildToOverlay(Row);
	RowSlot->SetHorizontalAlignment(HAlign_Center);
	RowSlot->SetVerticalAlignment(VAlign_Center);

	USizeBox* SilBox = WidgetTree->ConstructWidget<USizeBox>();
	SilBox->SetWidthOverride(420.f);
	SilBox->SetHeightOverride(420.f);
	Silhouette = WidgetTree->ConstructWidget<UImage>();
	SilBox->AddChild(Silhouette);
	Row->AddChildToHorizontalBox(SilBox)->SetVerticalAlignment(VAlign_Center);

	UVerticalBox* Col = WidgetTree->ConstructWidget<UVerticalBox>();
	UHorizontalBoxSlot* ColSlot = Row->AddChildToHorizontalBox(Col);
	ColSlot->SetVerticalAlignment(VAlign_Center);
	ColSlot->SetPadding(FMargin(30.f, 0.f, 0.f, 0.f));

	Kicker = MakeText(WidgetTree, TEXT("SOMETHING IN THIS HOUSE IS BROKEN..."), 26, Cream, TEXT("Bold"));
	Col->AddChildToVerticalBox(Kicker);
	MaladyName = MakeText(WidgetTree, TEXT("MALADY"), 96, FLinearColor::White, TEXT("Bold"));
	MaladyName->SetShadowOffset(FVector2D(6.f, 6.f));
	MaladyName->SetShadowColorAndOpacity(FLinearColor(Plum.R, Plum.G, Plum.B, 0.9f));
	Col->AddChildToVerticalBox(MaladyName)->SetPadding(FMargin(0.f, -10.f, 0.f, 0.f));
	Tagline = MakeText(WidgetTree, TEXT(""), 26, Plum, TEXT("BoldItalic"));
	Col->AddChildToVerticalBox(Tagline);
}

void UFixHimIntroCardWidget::Setup(const FHunkDefinition& Def, AFixHimHunk* Hunk, TFunction<void()> InOnFinished)
{
	OnFinished = MoveTemp(InOnFinished);
	FixHim::Sfx(this, "IntroCard");
	MaladyName->SetText(FText::FromString(Def.Malady.ToUpper()));
	Tagline->SetText(FText::FromString(Def.Tagline));
	Band->SetBrushColor(Def.GlowColor.CopyWithNewOpacity(1.f));

	if (Hunk)
	{
		Hunk->CapturePortraitNow();
		if (UMaterialInterface* Mat = UFixHimSettings::Get()->PortraitMaterial.LoadSynchronous())
		{
			UMaterialInstanceDynamic* MID = UMaterialInstanceDynamic::Create(Mat, this);
			MID->SetTextureParameterValue(TEXT("Portrait"), Hunk->GetPortrait());
			MID->SetScalarParameterValue(TEXT("Silhouette"), 1.f);
			MID->SetScalarParameterValue(TEXT("Transparent"), 1.f);
			Silhouette->SetBrushFromMaterial(MID);
		}
		else
		{
			Silhouette->SetBrushResourceObject(Hunk->GetPortrait());
			Silhouette->SetColorAndOpacity(FLinearColor::Black);
		}
	}
	Age = 0.f;
	bDone = false;
}

void UFixHimIntroCardWidget::NativeTick(const FGeometry& MyGeometry, float InDeltaTime)
{
	Super::NativeTick(MyGeometry, InDeltaTime);
	Age += InDeltaTime;

	const float In = EaseOutBack(Age / 0.45f);
	const float Out = FMath::Clamp((Age - (Duration - 0.4f)) / 0.4f, 0.f, 1.f);
	const float W = MyGeometry.GetLocalSize().X;

	if (Band)
	{
		Band->GetParent()->SetRenderTranslation(FVector2D(FMath::Lerp(-W * 1.6f, 0.f, In) + Out * W * 1.6f, 0.f));
	}
	if (Band2)
	{
		const float In2 = EaseOutBack((Age - 0.08f) / 0.45f);
		Band2->GetParent()->SetRenderTranslation(FVector2D(FMath::Lerp(W * 1.6f, 0.f, In2) - Out * W * 1.6f, 0.f));
	}
	if (Silhouette)
	{
		const float S = EaseOutBack((Age - 0.2f) / 0.5f);
		Silhouette->SetRenderScale(FVector2D(FMath::Max(0.01f, S * (1.f - Out))));
		Silhouette->SetRenderTransformAngle(FMath::Sin(Age * 2.f) * 3.f);
	}
	const float TextIn = FMath::Clamp((Age - 0.35f) / 0.3f, 0.f, 1.f);
	if (MaladyName)
	{
		MaladyName->SetRenderOpacity(TextIn * (1.f - Out));
		MaladyName->SetRenderScale(FVector2D(FMath::Lerp(1.6f, 1.f, EaseOutBack((Age - 0.35f) / 0.4f))));
	}
	if (Kicker)
	{
		Kicker->SetRenderOpacity(FMath::Clamp(Age / 0.3f, 0.f, 1.f) * (1.f - Out));
	}
	if (Tagline)
	{
		Tagline->SetRenderOpacity(FMath::Clamp((Age - 0.9f) / 0.4f, 0.f, 1.f) * (1.f - Out));
	}
	if (RootWidget)
	{
		RootWidget->SetRenderOpacity(1.f - Out * 0.8f);
	}

	if (!bDone && Age >= Duration)
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
	UVerticalBox* Col = MakeCardScreen(TEXT(""), 760.f);
	OpenSfx = NAME_None; // the ending jingle covers it
	if (UBorder* CardBorder = Cast<UBorder>(Col->GetParent()))
	{
		Card = CardBorder;
	}
	Col->ClearChildren();

	Kind = MakeText(WidgetTree, TEXT("ENDING"), 20, Pink, TEXT("Bold"));
	Kind->SetJustification(ETextJustify::Center);
	Col->AddChildToVerticalBox(Kind);

	Title = MakeText(WidgetTree, TEXT("Title"), 44, HotPink, TEXT("Bold"));
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
	Box->SetHeightOverride(56.f);
	Box->AddChild(UFixHimButton::Make(WidgetTree, TEXT("Continue"), [Self]() { if (Self.IsValid() && Self->GetFixHimPC()) { Self->GetFixHimPC()->CloseEndingCard(); } }, 22, true));
	Col->AddChildToVerticalBox(Box);
}

void UFixHimEndingCardWidget::Setup(const FHunkDefinition& Def, const FString& EndingId, int32 FixedCount, int32 TotalCount)
{
	FString KindText;
	FLinearColor KindColor = Pink;
	if (EndingId == TEXT("romance_success")) { KindText = TEXT("ROMANCE  -  HAPPILY EVER AFTER"); KindColor = HotPink; }
	else if (EndingId == TEXT("romance_failure")) { KindText = TEXT("ROMANCE  -  IT'S NOT ME, IT'S YOUR FOUNDATION"); KindColor = Ember; }
	else if (EndingId == TEXT("friend_success")) { KindText = TEXT("FRIENDSHIP  -  BESTIES"); KindColor = Mint; }
	else { KindText = TEXT("FRIENDSHIP  -  SWORN ENEMIES"); KindColor = Ember; }

	FixHim::Sfx(this, EndingId == TEXT("romance_success") ? "EndingRomance" : EndingId == TEXT("friend_success") ? "EndingFriend" : "EndingFail");
	Kind->SetText(FText::FromString(KindText));
	Kind->SetColorAndOpacity(FSlateColor(KindColor));

	const FHunkEnding* Ending = Def.Endings.Find(EndingId);
	Title->SetText(FText::FromString(Ending ? Ending->Title : Def.Name));
	const UFixHimSaveSubsystem* SaveSub = UFixHimSaveSubsystem::Get(this);
	const FString PlayerName = SaveSub ? SaveSub->GetPlayerName() : UFixHimSettings::Get()->PlayerName;
	Body->SetText(FText::FromString(Ending ? Ending->Text.Replace(TEXT("{player}"), *PlayerName) : FString()));

	const FString Fixed = FString::Printf(TEXT("%s repaired.  The house is %d / %d fixed."), *Def.Malady, FixedCount, TotalCount);
	Progress->SetText(FText::FromString(FixedCount >= TotalCount ? Fixed + TEXT("\nEvery man in this house has been fixed. Or at least seen. Home sweet home.") : Fixed));
	Age = 0.f;
}

void UFixHimEndingCardWidget::NativeTick(const FGeometry& MyGeometry, float InDeltaTime)
{
	Super::NativeTick(MyGeometry, InDeltaTime);
	Age += InDeltaTime;
	if (Card)
	{
		const float S = EaseOutBack(Age / 0.5f);
		Card->SetRenderScale(FVector2D(FMath::Max(0.01f, S)));
	}
}
