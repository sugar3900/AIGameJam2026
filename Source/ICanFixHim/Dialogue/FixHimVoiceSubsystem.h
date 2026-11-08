// I Can Fix Him - AI Game Jam 2026

#pragma once

#include "CoreMinimal.h"
#include "Subsystems/GameInstanceSubsystem.h"
#include "Dialogue/DialogueTypes.h"
#include "FixHimVoiceSubsystem.generated.h"

class UAudioComponent;

/**
 * Plays voice-over for dialogue lines. A line is voiced when a sound wave named
 * VO_<script>_<node>_<lineIndex> exists anywhere under /Game/ICanFixHim/Audio/VO
 * (made by Tools/Audio/generate_vo.py + Tools/Editor/import_vo.py). Lines without
 * a clip (narration, the player, unrecorded characters) are silent.
 *
 * Starts the clip when the line appears, cuts it off when the player clicks on,
 * and stops when the conversation ends. No code changes are needed to voice
 * another character: generate and import the files.
 */
UCLASS()
class ICANFIXHIM_API UFixHimVoiceSubsystem : public UGameInstanceSubsystem
{
	GENERATED_BODY()

public:
	static UFixHimVoiceSubsystem* Get(const UObject* WorldContext);

	virtual void Initialize(FSubsystemCollectionBase& Collection) override;
	virtual void Deinitialize() override;

	/** Rescan the VO folder (after importing new clips while the game is running). */
	void RebuildIndex();
	bool HasLine(const FString& ScriptId, const FString& NodeId, int32 LineIndex) const;
	void Stop(float FadeSeconds = 0.08f);
	int32 NumIndexed() const { return Index.Num(); }
	/** True while a voice line is audible (the music ducks under it). */
	bool IsPlaying() const;

	static FString MakeKey(const FString& ScriptId, const FString& NodeId, int32 LineIndex);

private:
	void HandleView(const FDialogueView& View);
	void HandleEnded(const FString& HunkId, const FString& EndingId);

	/** Asset name -> sound wave path. */
	TMap<FString, FSoftObjectPath> Index;
	TWeakObjectPtr<UAudioComponent> Playing;
	FString PlayingKey;
	FDelegateHandle ViewHandle, EndHandle, AbortHandle;
};
