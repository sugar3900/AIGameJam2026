// I Can Fix Him - AI Game Jam 2026

#pragma once

#include "CoreMinimal.h"
#include "Subsystems/GameInstanceSubsystem.h"
#include "Dialogue/DialogueTypes.h"
#include "FixHimDialogueSubsystem.generated.h"

DECLARE_MULTICAST_DELEGATE_OneParam(FOnDialogueView, const FDialogueView&);
DECLARE_MULTICAST_DELEGATE_OneParam(FOnConversationStarted, const FString& /*HunkId*/);
DECLARE_MULTICAST_DELEGATE_TwoParams(FOnConversationEnded, const FString& /*HunkId*/, const FString& /*EndingId, empty if arc continues*/);

/**
 * Loads every hunk's dialogue JSON and runs one conversation at a time.
 *
 * The runtime is deliberately UI-agnostic: widgets listen to OnView and call
 * Advance / Choose / ClickTopic. A future LLM-backed provider can replace the
 * node graph without touching the UI (see docs/04 Tech/Dialogue Format.md).
 */
UCLASS()
class ICANFIXHIM_API UFixHimDialogueSubsystem : public UGameInstanceSubsystem
{
	GENERATED_BODY()

public:
	static UFixHimDialogueSubsystem* Get(const UObject* WorldContext);

	virtual void Initialize(FSubsystemCollectionBase& Collection) override;

	/** Re-reads all JSON from disk (console: FixHim.ReloadDialogue). */
	void ReloadDefinitions();

	const FHunkDefinition* FindHunk(const FString& HunkId) const { return Hunks.Find(HunkId); }
	const TMap<FString, FHunkDefinition>& GetAllHunks() const { return Hunks; }
	const FHunkDefinition* FindHunkForRoom(const FString& RoomId) const;
	/** Number of love interests (kind == "hunk"), excluding podcast / epilogue scripts. */
	int32 CountStoryHunks() const;
	/** Story hunks whose arc has ended (any ending). Conditions see this as "fixedcount". */
	int32 CountFixedStoryHunks() const;
	/** The final inspection passes when every story hunk is fixed. */
	bool IsHouseFixed() const { const int32 N = CountStoryHunks(); return N > 0 && CountFixedStoryHunks() >= N; }

	// ---- Conversation -----------------------------------------------------

	bool StartConversation(const FString& HunkId);
	/** Next line, or follow goto / end when the node is finished. No-op while choices are shown. */
	void Advance();
	void Choose(int32 VisibleChoiceIndex);
	void ClickTopic(const FString& TopicId);
	/** Force-close (e.g. returning to the main menu). Does not count as a visit. */
	void AbortConversation();

	bool IsActive() const { return !ActiveHunkId.IsEmpty(); }
	const FString& GetActiveHunkId() const { return ActiveHunkId; }
	const FDialogueView& GetView() const { return View; }

	/** Resolve a condition identifier for a given hunk context. Public for debugging / tests. */
	int32 ResolveVariable(const FString& HunkId, const FString& Identifier) const;

	/** First entry node whose condition is true (used for non-interactive scripts like the radio). */
	const FDialogueNode* ResolveEntryNode(const FString& DefinitionId) const;

	/** Ending the default resolver would pick from current stats. */
	FString ResolveAutoEnding(const FString& HunkId) const;

	FOnDialogueView OnView;
	FOnConversationStarted OnConversationStarted;
	FOnConversationEnded OnConversationEnded;

	/** Validation messages from the last load (broken gotos, bad conditions...). */
	const TArray<FString>& GetLoadErrors() const { return LoadErrors; }

private:
	bool LoadHunkFile(const FString& Path);
	void Validate(const FHunkDefinition& Def);

	void EnterNode(const FString& NodeId);
	/** Pop the aside stack and re-show the line the aside was clicked on. */
	void ReturnFromAside();
	void FinishConversation();
	void ApplyEffects(const TArray<FDialogueEffect>& Effects);
	void RebuildView();
	FString Substitute(const FString& In) const;
	TArray<int32> GetVisibleChoiceIndices() const;
	bool IsTrue(const FString& Condition) const;

	TMap<FString, FHunkDefinition> Hunks;
	TArray<FString> LoadErrors;

	FString ActiveHunkId;
	FString ActiveNodeId;
	int32 LineIndex = 0;
	FString PendingEnding;
	bool bCountVisit = true;
	FDialogueView View;
	/** Guards against goto loops that never show a line. */
	int32 JumpsWithoutLines = 0;

	/** Where each open aside returns to (innermost last). */
	struct FReturnPoint
	{
		FString NodeId;
		int32 LineIndex = 0;
	};
	TArray<FReturnPoint> ReturnStack;
	/** "nodeId/topicId" of aside topics already clicked this conversation. */
	TSet<FString> SpentAsides;
	/** Set while RebuildView re-shows a line after an aside. */
	bool bResumingLine = false;
};
