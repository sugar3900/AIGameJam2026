// I Can Fix Him - AI Game Jam 2026
//
// In-memory representation of the Twine-style branching dialogue loaded from
// Content/ICanFixHim/Data/Dialogue/*.json. See docs/04 Tech/Dialogue Format.md.

#pragma once

#include "CoreMinimal.h"

/** "romance": 1, "lukey.friction": 2, "flag.met_wyatt": 1 */
struct FDialogueEffect
{
	FString Key;
	int32 Value = 0;
};

struct FDialogueChoice
{
	FString Text;
	FString Condition;
	FString Goto;
	TArray<FDialogueEffect> Effects;
};

/** A clickable highlighted word inside a line, written as [word] or [shown text|topicId]. */
struct FDialogueTopic
{
	FString Goto;
	FString Condition;
	TArray<FDialogueEffect> Effects;
};

enum class EDialogueSpeaker : uint8
{
	Hunk,
	Player,
	Narration,
	/** A declared extra speaker ("Bev: ...", "Dan: ...") - see FHunkDefinition::Speakers. */
	Named
};

struct FDialogueLine
{
	EDialogueSpeaker Speaker = EDialogueSpeaker::Hunk;
	FString SpeakerName;
	FString Text;
};

struct FDialogueNode
{
	FString Id;
	TArray<FDialogueLine> Lines;
	TArray<FDialogueChoice> Choices;
	TMap<FString, FDialogueTopic> Topics;
	TArray<FDialogueEffect> Effects;
	FString Goto;
	/** Ends the conversation after the last line. */
	bool bEnd = false;
	/** Arc ending id (romance_success, ...) or "auto". Implies bEnd and repairs the malady. */
	FString Ending;
	/** Presentation effect played when the node is entered: "fade" (fade to black), "hearts". */
	FString Fx;
	FString FxText;
};

struct FDialogueEntry
{
	FString Condition;
	FString Node;
};

/** A primitive glued onto the hunk's skeleton to make him read as "his" malady. */
struct FHunkProp
{
	FString Shape = TEXT("cube"); // cube | sphere | cylinder | plane
	FName Socket = NAME_None;
	FVector Location = FVector::ZeroVector;
	FRotator Rotation = FRotator::ZeroRotator;
	FVector Scale = FVector::OneVector;
	FLinearColor Color = FLinearColor::White;
	float Emissive = 0.f;
};

struct FHunkEnding
{
	FString Title;
	FString Text;
};

struct FHunkDefinition
{
	FString Id;
	/** "hunk" (a love interest with a malady), or a story script such as "podcast" / "epilogue". */
	FString Kind = TEXT("hunk");
	/** Extra speaker names allowed as "Name: text" line prefixes. */
	TArray<FString> Speakers;
	FString Name;
	/** The house problem he embodies, e.g. "Leaky Plumbing". */
	FString Malady;
	FString Room;
	FString Tagline;

	/** Outfit painted onto the mannequin by M_Character. */
	FLinearColor Skin = FLinearColor(0.8f, 0.58f, 0.47f);
	FLinearColor Shirt = FLinearColor(0.8f, 0.6f, 0.5f);
	FLinearColor Pants = FLinearColor(0.15f, 0.18f, 0.28f);
	FLinearColor Shoes = FLinearColor(0.12f, 0.09f, 0.07f);
	/** 1 = plaid shirt. */
	float Pattern = 0.f;
	FLinearColor GlowColor = FLinearColor(1.f, 0.4f, 0.7f);
	float Scale = 1.f;
	TArray<FHunkProp> Props;

	TArray<FDialogueEntry> Entries;
	TMap<FString, FDialogueNode> Nodes;
	TMap<FString, FHunkEnding> Endings;

	const FDialogueNode* FindNode(const FString& NodeId) const { return Nodes.Find(NodeId); }
	bool IsHunk() const { return Kind == TEXT("hunk"); }
};

/** Snapshot the UI renders. */
struct FDialogueView
{
	FString HunkId;
	FString HunkName;
	EDialogueSpeaker Speaker = EDialogueSpeaker::Hunk;
	/** Set when Speaker == Named. */
	FString SpeakerName;
	/** Text with [topic] markup still in place and {player}/{name} substituted. */
	FString Text;
	TArray<FString> Choices;
	/** Topic ids that are currently clickable. */
	TArray<FString> ActiveTopics;
	FString Fx;
	FString FxText;
	bool bIsLastLine = false;
	bool bWillEnd = false;
};
