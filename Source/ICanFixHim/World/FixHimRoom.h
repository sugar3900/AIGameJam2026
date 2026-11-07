// I Can Fix Him - AI Game Jam 2026

#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "FixHimRoom.generated.h"

class UBoxComponent;
class UArrowComponent;

/**
 * A room of the apartment. The box defines both the gameplay volume (entering /
 * leaving) and the rectangle drawn on the 2D floor plan. EntryPoint is where the
 * floor-plan fast travel drops the player.
 */
UCLASS()
class ICANFIXHIM_API AFixHimRoom : public AActor
{
	GENERATED_BODY()

public:
	AFixHimRoom();

	virtual void BeginPlay() override;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Room")
	FString RoomId;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Room")
	FText DisplayName;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Room")
	FLinearColor MapColor = FLinearColor(0.95f, 0.75f, 0.8f);

	/** Rooms that are drawn on the plan but not reachable yet (future hunks). */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Room")
	bool bLocked = false;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Components")
	TObjectPtr<UBoxComponent> Bounds;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Components")
	TObjectPtr<UArrowComponent> EntryPoint;

	/** World-space XY rectangle of the room. */
	FBox2D GetFloorRect() const;
	FTransform GetEntryTransform() const;
	bool ContainsPoint(const FVector& WorldPoint) const;

private:
	UFUNCTION()
	void HandleBeginOverlap(UPrimitiveComponent* OverlappedComp, AActor* Other, UPrimitiveComponent* OtherComp, int32 BodyIndex, bool bFromSweep, const FHitResult& Sweep);

	UFUNCTION()
	void HandleEndOverlap(UPrimitiveComponent* OverlappedComp, AActor* Other, UPrimitiveComponent* OtherComp, int32 BodyIndex);
};
