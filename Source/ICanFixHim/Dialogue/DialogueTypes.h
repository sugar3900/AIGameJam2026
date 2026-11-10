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
	/**
	 * "aside": true - a one-off detour: the chain it starts ends in a "return" node, which
	 * resumes the line the topic was clicked on. Spent after one click (per conversation).
	 * Otherwise (and for string shorthand topics) the topic is a one-way divert.
	 */
	bool bAside = false;
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
	/** From an inline {fx:name} tag: plays when this line appears (e.g. "hearts"). */
	FString Fx;
	/** From inline {sfx:Name} tags (any number): SFX cues played when this line first appears. */
	TArray<FString> Sfx;
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
	/**
	 * Presentation effect played when the node is entered: "fade" (fade to black), "hearts".
	 * Lines can also carry their own inline {fx:name} tag.
	 */
	FString Fx;
	FString FxText;
	/** "sfx": "Name" (or an array of names): SFX cues played with the node's first line. */
	TArray<FString> Sfx;
	/** "return": true - when this node's lines run out (and it has no choices), resume the line an aside topic was clicked on. */
	bool bReturn = false;
};

struct FDialogueEntry
{
	FString Condition;
	FString Node;
	/** false for "come back next week" chatter that shouldn't advance his story. */
	bool bCounts = true;
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

	/**
	 * Object path of a rigged character model (look.mesh in JSON), e.g.
	 * "/Game/ICanFixHim/Characters/BlackMold/SK_BlackMold". When set it replaces the painted
	 * mannequin: outfit colours, eyes and props are ignored. Assets under /Game/ICanFixHim/Characters
	 * are always cooked (Config/DefaultGame.ini) since only this JSON string references them.
	 */
	FString Mesh;
	/** Looping idle animation for Mesh (look.idle), retargeted onto its skeleton by Tools/Editor/import_characters.py. */
	FString Idle;
	/** Optional painted portrait texture (look.portrait); empty uses the scene capture. */
	FString Portrait;
	/** How he arrives / leaves (look.entrance, look.exit): bubble (default), sparkle, spores or surge. Empty exit = same as entrance. */
	FString Entrance;
	FString Exit;

	/** Outfit painted onto the mannequin by M_Character (fallback when Mesh is empty). */
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
	/**
	 * Node and 0-based line index this view shows. Lets listeners tell a new line from a
	 * re-broadcast, and is the voice-over lookup key (VO_<script>_<node>_<line>).
	 */
	FString NodeId;
	int32 LineIndex = 0;
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
	/**
	 * SFX cues for this line (node "sfx" on line 0, then the line's {sfx:Name} tags). Played by the dialogue
	 * subsystem when the view is broadcast; empty when bIsReturn.
	 */
	TArray<FString> Sfx;
	bool bIsLastLine = false;
	bool bWillEnd = false;
	/**
	 * Re-presenting a line already shown (back from an aside's "return" node or a hypertext
	 * tangent): the line is not new, only its options. No fx; voice-over is not replayed.
	 */
	bool bIsReturn = false;
	/** Reading a hypertext node: a dead end that returns to the node it was opened from. */
	bool bInTangent = false;
};
