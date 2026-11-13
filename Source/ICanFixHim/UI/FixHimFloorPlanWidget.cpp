// I Can Fix Him - AI Game Jam 2026

#include "UI/FixHimFloorPlanWidget.h"
#include "Player/FixHimPlayerController.h"
#include "World/FixHimRoom.h"
#include "World/FixHimMalady.h"
#include "Core/FixHimSaveSubsystem.h"
#include "Dialogue/FixHimDialogueSubsystem.h"
#include "Blueprint/WidgetTree.h"
#include "Components/Border.h"
#include "Components/CanvasPanel.h"
#include "Components/CanvasPanelSlot.h"
#include "Components/Overlay.h"
#include "Components/OverlaySlot.h"
#include "Components/SizeBox.h"
#include "Components/TextBlock.h"
#include "Components/VerticalBox.h"
#include "Components/VerticalBoxSlot.h"
#include "EngineUtils.h"
#include "GameFramework/Pawn.h"

using namespace FixHimUI;

void UFixHimFloorPlanWidget::BuildUI()
{
	UOverlay *Root = WidgetTree->ConstructWidget<UOverlay>();
	WidgetTree->RootWidget = Root;

	UBorder *Dim = WidgetTree->ConstructWidget<UBorder>();
	Dim->SetBrushColor(FixHimDesign::Scrim);
	UOverlaySlot *DimSlot = Root->AddChildToOverlay(Dim);
	DimSlot->SetHorizontalAlignment(HAlign_Fill);
	DimSlot->SetVerticalAlignment(VAlign_Fill);

	Sheet = WidgetTree->ConstructWidget<UFixHimSurface>();
	Sheet->SetBrush(Rounded(Blueprint, 18.f, FLinearColor(0.75f, 0.85f, 1.f, 0.9f), 3.f));
	Sheet->SetPadding(FMargin(32, 28, 48, 36));
	UOverlaySlot *SheetSlot = Root->AddChildToOverlay(Sheet);
	SheetSlot->SetHorizontalAlignment(HAlign_Center);
	SheetSlot->SetVerticalAlignment(VAlign_Center);

	UVerticalBox *Col = WidgetTree->ConstructWidget<UFixHimStack>();
	Sheet->SetContent(Col);

	UTextBlock *Title = MakeText(WidgetTree, TEXT("FLOOR PLAN  -  12 HEARTBREAK LANE"), 32, Cream, TEXT("Display"));
	Col->AddChildToVerticalBox(Title)->SetPadding(FMargin(0.f, 0.f, 0.f, 4.f));
	UTextBlock *Sub = MakeText(WidgetTree, TEXT("Click a room to go there.  [M] or click outside to close"), 16,
	                           Cream.CopyWithNewOpacity(.85f), TEXT("Italic"));
	Col->AddChildToVerticalBox(Sub)->SetPadding(FMargin(0.f, 0.f, 0.f, 14.f));

	USizeBox *MapBox = WidgetTree->ConstructWidget<USizeBox>();
	MapBox->SetWidthOverride(MapSize.X);
	MapBox->SetHeightOverride(MapSize.Y);
	Canvas = WidgetTree->ConstructWidget<UCanvasPanel>();
	MapBox->AddChild(Canvas);
	Col->AddChildToVerticalBox(MapBox);
}

UWidget *UFixHimFloorPlanWidget::GetOutsideClickCard() const
{
	return Sheet;
}

bool UFixHimFloorPlanWidget::HandleClickOutside()
{
	AFixHimPlayerController *PC = GetFixHimPC();
	if (PC && PC->GetState() == EFixHimState::FloorPlan)
	{
		PC->ToggleFloorPlan();
		return true;
	}
	return false;
}

FVector2D UFixHimFloorPlanWidget::WorldToMap(const FVector2D &World) const
{
	// Screen right = world +Y, screen up = world +X (looking down with north up).
	const FVector2D Rel(World.Y - WorldBounds.Min.Y, WorldBounds.Max.X - World.X);
	return MapOffset + Rel * MapScale;
}

void UFixHimFloorPlanWidget::Refresh()
{
	if (!Canvas)
	{
		return;
	}
	Canvas->ClearChildren();
	PlayerMarker = nullptr;

	TArray<AFixHimRoom *> Rooms;
	WorldBounds = FBox2D(ForceInit);
	for (TActorIterator<AFixHimRoom> It(GetWorld()); It; ++It)
	{
		Rooms.Add(*It);
		WorldBounds += It->GetFloorRect();
	}
	if (Rooms.IsEmpty())
	{
		return;
	}

	const FVector2D Extent(WorldBounds.Max.Y - WorldBounds.Min.Y, WorldBounds.Max.X - WorldBounds.Min.X);
	MapScale = FMath::Min((MapSize.X - 20.f) / Extent.X, (MapSize.Y - 20.f) / Extent.Y);
	MapOffset = (MapSize - Extent * MapScale) * 0.5f;

	const UFixHimSaveSubsystem *Save = UFixHimSaveSubsystem::Get(this);
	const UFixHimDialogueSubsystem *Dialogue = UFixHimDialogueSubsystem::Get(this);
	AFixHimPlayerController *PC = GetFixHimPC();
	const FString CurrentRoom = PC ? PC->GetCurrentRoomId() : FString();

	for (AFixHimRoom *Room : Rooms)
	{
		const FBox2D R = Room->GetFloorRect();
		const FVector2D A = WorldToMap(FVector2D(R.Max.X, R.Min.Y));
		const FVector2D B = WorldToMap(FVector2D(R.Min.X, R.Max.Y));
		const FVector2D Pos(FMath::Min(A.X, B.X), FMath::Min(A.Y, B.Y));
		const FVector2D Size = (B - A).GetAbs();

		const bool bHere = Room->RoomId == CurrentRoom;
		const FLinearColor Line(0.85f, 0.92f, 1.f, Room->bLocked ? 0.35f : 1.f);
		const FLinearColor Fill = Room->bLocked ? Plum.CopyWithNewOpacity(.4f) : bHere ? Pink : Plum;
		const bool ExternalLabel = Size.X < 120.f * FixHimDesign::TextScale();

		UVerticalBox *Info = WidgetTree->ConstructWidget<UVerticalBox>();
		UTextBlock *Name = MakeText(WidgetTree, Room->DisplayName.ToString().ToUpper(), 20, Line, TEXT("Bold"));
		Name->SetJustification(ETextJustify::Center);
		Name->SetAutoWrapText(true);
		Name->SetWrappingPolicy(ETextWrappingPolicy::DefaultWrapping);
		if (!ExternalLabel)
			Info->AddChildToVerticalBox(Name)->SetHorizontalAlignment(HAlign_Fill);

		FString Status;
		FLinearColor StatusColor = FLinearColor(0.8f, 0.88f, 1.f, 0.9f);
		if (Room->bSubVolume)
		{
			// Part of another room (e.g. a closet): name only; that room's own cell carries the status.
		}
		else if (Room->bLocked)
		{
			Status = TEXT("coming soon");
		}
		else if (const FHunkDefinition *Def = Dialogue ? Dialogue->FindHunkForRoom(Room->RoomId) : nullptr)
		{
			const FHunkProgress *P = Save ? Save->FindHunk(Def->Id) : nullptr;
			if (!P || !P->bMet)
			{
				Status = FString::Printf(TEXT("%s?"), *Def->Malady);
				StatusColor = Cream;
			}
			else if (P->bFixed)
			{
				Status = FString::Printf(TEXT("%s  -  fixed"), *Def->Name);
				StatusColor = Cream;
			}
			else
			{
				Status = FString::Printf(TEXT("%s  -  %s"), *Def->Name, *Def->Malady);
				StatusColor = Blush;
			}
		}
		if (!Status.IsEmpty())
		{
			UTextBlock *St = MakeText(WidgetTree, Status, 15, StatusColor, TEXT("Italic"));
			St->SetJustification(ETextJustify::Center);
			St->SetAutoWrapText(true);
			Info->AddChildToVerticalBox(St)->SetHorizontalAlignment(HAlign_Fill);
		}
		if (bHere && !Room->bSubVolume && !ExternalLabel)
		{
			UTextBlock *You = MakeText(WidgetTree, TEXT("you are here"), 13, FLinearColor::White, TEXT("Bold"));
			You->SetAutoWrapText(true);
			You->SetJustification(ETextJustify::Center);
			Info->AddChildToVerticalBox(You)->SetHorizontalAlignment(HAlign_Fill);
		}

		UWidget *Cell = nullptr;
		if (Room->bLocked || Room->bSubVolume) // sub-volumes are not travel destinations
		{
			UBorder *Locked = WidgetTree->ConstructWidget<UBorder>();
			Locked->SetBrush(Rounded(Fill, 4.f, Line, 2.f));
			Locked->SetHorizontalAlignment(HAlign_Center);
			Locked->SetVerticalAlignment(VAlign_Center);
			Locked->SetContent(Info);
			Cell = Locked;
		}
		else
		{
			UFixHimButton *Btn = WidgetTree->ConstructWidget<UFixHimButton>();
			FButtonStyle Style = ButtonStyle(Fill, FLinearColor(Pink.R, Pink.G, Pink.B, 0.6f), HotPink, 4.f, Line);
			Btn->SetStyle(Style);
			Btn->AddChild(Info);
			TWeakObjectPtr<AFixHimRoom> WeakRoom(Room);
			TWeakObjectPtr<UFixHimFloorPlanWidget> Self(this);
			Btn->Init([WeakRoom, Self]() {
				if (WeakRoom.IsValid() && Self.IsValid() && Self->GetFixHimPC())
				{
					Self->GetFixHimPC()->TravelToRoom(WeakRoom.Get());
				}
			});
			Cell = Btn;
		}

		UCanvasPanelSlot *S = Canvas->AddChildToCanvas(Cell);
		S->SetPosition(Pos + FVector2D(3.f));
		S->SetSize(Size - FVector2D(6.f));
		if (ExternalLabel)
		{
			// Full words overhang the narrow footprint; geometry and travel destinations stay truthful.
			auto *Tag = WidgetTree->ConstructWidget<UFixHimSurface>();
			Tag->SetBrush(Rounded(bHere ? Pink : Cream, 12));
			Tag->SetPadding(FMargin(24, 10, 30, 24));
			Name->SetAutoWrapText(false);
			Name->SetColorAndOpacity(FSlateColor(bHere ? FLinearColor::White : Plum));
			auto *Labels = WidgetTree->ConstructWidget<UVerticalBox>();
			Labels->AddChildToVerticalBox(Name);
			if (bHere)
				Labels->AddChildToVerticalBox(
				    MakeText(WidgetTree, TEXT("YOU ARE HERE"), 12, FLinearColor::White, TEXT("Semibold")));
			Tag->SetContent(Labels);
			Tag->SetVisibility(ESlateVisibility::HitTestInvisible);
			auto *TagSlot = Canvas->AddChildToCanvas(Tag);
			TagSlot->SetAutoSize(true);
			TagSlot->SetAlignment(FVector2D(.5f, .5f));
			TagSlot->SetPosition(Pos + Size * .5f);
			TagSlot->SetZOrder(10);
		}
	}

	PlayerMarker = WidgetTree->ConstructWidget<UBorder>();
	PlayerMarker->SetBrush(Rounded(HotPink, 9.f, FLinearColor::White, 3.f));
	PlayerMarker->SetVisibility(ESlateVisibility::HitTestInvisible);
	UCanvasPanelSlot *MS = Canvas->AddChildToCanvas(PlayerMarker);
	MS->SetSize(FVector2D(18.f, 18.f));
	MS->SetAlignment(FVector2D(0.5f, 0.5f));
}

void UFixHimFloorPlanWidget::NativeTick(const FGeometry &MyGeometry, float InDeltaTime)
{
	Super::NativeTick(MyGeometry, InDeltaTime);
	Age += InDeltaTime;
	if (!PlayerMarker)
	{
		return;
	}
	const APlayerController *PC = GetOwningPlayer();
	const APawn *Pawn = PC ? PC->GetPawn() : nullptr;
	if (Pawn)
	{
		if (UCanvasPanelSlot *S = Cast<UCanvasPanelSlot>(PlayerMarker->Slot))
		{
			S->SetPosition(WorldToMap(FVector2D(Pawn->GetActorLocation())));
		}
		PlayerMarker->SetRenderScale(
		    FVector2D(FixHimDesign::ReducedMotion() ? 1.f : 1.f + .25f * FMath::Sin(Age * 6.f)));
	}
}
