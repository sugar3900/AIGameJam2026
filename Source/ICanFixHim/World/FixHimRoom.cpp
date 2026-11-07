// I Can Fix Him - AI Game Jam 2026

#include "World/FixHimRoom.h"
#include "Player/FixHimPlayerController.h"
#include "Components/BoxComponent.h"
#include "Components/ArrowComponent.h"
#include "GameFramework/Pawn.h"

AFixHimRoom::AFixHimRoom()
{
	PrimaryActorTick.bCanEverTick = false;

	Bounds = CreateDefaultSubobject<UBoxComponent>(TEXT("Bounds"));
	SetRootComponent(Bounds);
	Bounds->SetBoxExtent(FVector(300.f, 300.f, 150.f));
	Bounds->SetCollisionProfileName(TEXT("Trigger"));
	Bounds->SetGenerateOverlapEvents(true);
	Bounds->ShapeColor = FColor(255, 120, 190);
	Bounds->SetLineThickness(3.f);

	EntryPoint = CreateDefaultSubobject<UArrowComponent>(TEXT("EntryPoint"));
	EntryPoint->SetupAttachment(Bounds);
	EntryPoint->ArrowColor = FColor(255, 80, 160);
}

void AFixHimRoom::BeginPlay()
{
	Super::BeginPlay();
	Bounds->OnComponentBeginOverlap.AddDynamic(this, &AFixHimRoom::HandleBeginOverlap);
	Bounds->OnComponentEndOverlap.AddDynamic(this, &AFixHimRoom::HandleEndOverlap);
}

FBox2D AFixHimRoom::GetFloorRect() const
{
	const FVector Ext = Bounds->GetScaledBoxExtent();
	const FVector C = Bounds->GetComponentLocation();
	return FBox2D(FVector2D(C.X - Ext.X, C.Y - Ext.Y), FVector2D(C.X + Ext.X, C.Y + Ext.Y));
}

FTransform AFixHimRoom::GetEntryTransform() const
{
	return EntryPoint->GetComponentTransform();
}

bool AFixHimRoom::ContainsPoint(const FVector& WorldPoint) const
{
	return GetFloorRect().IsInside(FVector2D(WorldPoint));
}

void AFixHimRoom::HandleBeginOverlap(UPrimitiveComponent*, AActor* Other, UPrimitiveComponent*, int32, bool, const FHitResult&)
{
	if (const APawn* Pawn = Cast<APawn>(Other))
	{
		if (AFixHimPlayerController* PC = Cast<AFixHimPlayerController>(Pawn->GetController()))
		{
			PC->NotifyEnteredRoom(this);
		}
	}
}

void AFixHimRoom::HandleEndOverlap(UPrimitiveComponent*, AActor* Other, UPrimitiveComponent*, int32)
{
	if (const APawn* Pawn = Cast<APawn>(Other))
	{
		if (AFixHimPlayerController* PC = Cast<AFixHimPlayerController>(Pawn->GetController()))
		{
			PC->NotifyLeftRoom(this);
		}
	}
}
