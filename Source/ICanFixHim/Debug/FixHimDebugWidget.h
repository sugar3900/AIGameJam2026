// I Can Fix Him - AI Game Jam 2026

#pragma once

#include "CoreMinimal.h"
#include "ICanFixHim.h"
#include "UI/FixHimUI.h"
#include "FixHimDebugWidget.generated.h"

#if FIXHIM_DEBUG
class UEditableTextBox;
class UFixHimButton;
class UFixHimDebugComponent;
class UTextBlock;
class UVerticalBox;
class UHorizontalBox;
class UFixHimSaveSubsystem;
#endif

/**
 * Compact side panel over the live save data (the StoryWriter "State" panel, in game): week and
 * day skipping, player name, flags, per-character stats, and the auto-play controls.
 * The root is not hit-testable, so the game keeps running (and receiving clicks) around the panel.
 *
 * An empty shell in shipping builds (see FixHimDebug.h); the widget tree owns every child, so the
 * members below are plain pointers rather than UPROPERTYs.
 */
UCLASS()
class UFixHimDebugWidget : public UFixHimWidget
{
	GENERATED_BODY()

#if FIXHIM_DEBUG
public:
	void Setup(UFixHimDebugComponent* InOwner);
	/** Re-reads everything from the save data (also runs a few times a second while shown). */
	void SyncAll();

protected:
	virtual void BuildUI() override;
	virtual void NativeTick(const FGeometry& MyGeometry, float InDeltaTime) override;

private:
	using FSyncList = TArray<TFunction<void()>>;

	UFixHimSaveSubsystem* Save() const;
	void BuildFlagList();
	void BuildHunkSection(const FString& HunkId);

	/** Label [-] value [+] (values are kept in Min..Max; Set is only called with the clamped result). */
	void AddStepper(UHorizontalBox* Row, const FString& Label, int32 Min, int32 Max, TFunction<int32()> Get, TFunction<void(int32)> Set, FSyncList& SyncList, float LabelWidth = 62.f);
	UVerticalBox* AddSection(const FString& Title);
	UFixHimButton* MakeSmallButton(const FString& Label, TFunction<void()> OnClick);

	TWeakObjectPtr<UFixHimDebugComponent> Owner;

	TObjectPtr<UVerticalBox> Content;
	TObjectPtr<UVerticalBox> FlagList;
	TObjectPtr<UEditableTextBox> NameBox;
	TObjectPtr<UEditableTextBox> FlagNameBox;
	TObjectPtr<UEditableTextBox> FlagValueBox;
	TObjectPtr<UTextBlock> WeekText;

	FSyncList Syncs;
	FSyncList FlagSyncs;
	FString FlagSignature;
	int32 TargetWeek = 2;
	float SyncTimer = 0.f;
#endif
};
