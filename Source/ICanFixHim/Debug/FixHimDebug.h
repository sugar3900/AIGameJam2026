// I Can Fix Him - AI Game Jam 2026
//
// In-game debug tools (editor and development builds only): a State panel modelled on the
// StoryWriter tool, day skipping, and an auto-play that plays conversations / podcast / splash
// cards out by itself. Toggle the panel with \ (backslash) or Insert.
//
// UHT does not allow UCLASS / UPROPERTY inside preprocessor blocks, so the reflected class is
// declared unconditionally as an empty shell; everything else (members, code, input, UI) is
// compiled only when FIXHIM_DEBUG is set (editor / non-shipping), and nothing creates the class
// in shipping builds.

#pragma once

#include "CoreMinimal.h"
#include "ICanFixHim.h"
#include "Components/ActorComponent.h"
#include "FixHimDebug.generated.h"

#if FIXHIM_DEBUG
class AFixHimPlayerController;
class UFixHimDebugWidget;

/** Which choice auto-play picks when a conversation offers some. */
enum class EFixHimAutoChoice : uint8
{
	First,
	Random,
	Last
};
#endif

/**
 * Lives on the player controller. Owns the debug input binding and the debug panel, and (while
 * auto-play is on) drives the conversation the same way the player's clicks would.
 */
UCLASS()
class UFixHimDebugComponent : public UActorComponent
{
	GENERATED_BODY()

public:
	// UHT must see the constructor so generated construction uses our tick setup.
	UFixHimDebugComponent();

#if FIXHIM_DEBUG

	/** Creates and registers the component on the controller; call once after its input is built. */
	static UFixHimDebugComponent* Install(AFixHimPlayerController* PC);

	virtual void TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction) override;
	virtual void OnComponentDestroyed(bool bDestroyingHierarchy) override;
	virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;

	void TogglePanel();
	bool IsPanelOpen() const;

	AFixHimPlayerController* GetPC() const;

	// Auto-play settings (edited by the panel).
	bool bAutoPlay = false;
	/** Seconds between auto-play steps. */
	float StepDelay = 0.2f;
	EFixHimAutoChoice ChoicePolicy = EFixHimAutoChoice::First;

private:
	/** One auto-play step: advance a line, pick a choice, skip a splash card or a podcast caption. */
	void AutoStep();

	// Not a UPROPERTY (see the header comment): the panel is kept alive by its viewport slot while shown.
	TWeakObjectPtr<UFixHimDebugWidget> Panel;

	/** Slate-level key listener that toggles the panel (see the .cpp); registered in Install. */
	TSharedPtr<class FFixHimDebugKeys> KeyProcessor;
	void RemoveKeyProcessor();

	float StepTimer = 0.f;
#endif
};
