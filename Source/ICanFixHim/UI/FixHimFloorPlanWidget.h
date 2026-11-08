// I Can Fix Him - AI Game Jam 2026

#pragma once

#include "CoreMinimal.h"
#include "UI/FixHimUI.h"
#include "FixHimFloorPlanWidget.generated.h"

class UCanvasPanel;
class UBorder;

/** Blueprint-style 2D floor plan. Click a room to walk (well, teleport) there. */
UCLASS()
class ICANFIXHIM_API UFixHimFloorPlanWidget : public UFixHimWidget
{
	GENERATED_BODY()

public:
	/** Re-reads rooms + save state. Call each time the map opens. */
	void Refresh();

protected:
	virtual void BuildUI() override;
	virtual void NativeTick(const FGeometry& MyGeometry, float InDeltaTime) override;
	/** Click outside the blueprint sheet = close the map (same as M / Tab). */
	virtual bool HandleClickOutside() override;
	virtual UWidget* GetOutsideClickCard() const override;

private:
	FVector2D WorldToMap(const FVector2D& World) const;

	UPROPERTY() TObjectPtr<UCanvasPanel> Canvas;
	UPROPERTY() TObjectPtr<UBorder> Sheet;
	UPROPERTY() TObjectPtr<UBorder> PlayerMarker;

	FBox2D WorldBounds = FBox2D(ForceInit);
	FVector2D MapSize = FVector2D(980.f, 640.f);
	float MapScale = 1.f;
	FVector2D MapOffset = FVector2D::ZeroVector;
	float Age = 0.f;
};
