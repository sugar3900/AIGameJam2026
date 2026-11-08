// I Can Fix Him - AI Game Jam 2026

#pragma once

#include "CoreMinimal.h"
#include "FixHimSaveTypes.generated.h"

/** Relationship stats are clamped to 0..StatMax; the dialogue meters fill at StatMax. */
inline constexpr int32 FixHimStatMax = 20;

/** The three relationship axes every hunk tracks. */
UENUM(BlueprintType)
enum class ERelationshipAxis : uint8
{
	Romance,
	Friendship,
	Friction
};

/** Per-hunk progress. Serialized to JSON via FJsonObjectConverter. */
USTRUCT(BlueprintType)
struct FHunkProgress
{
	GENERATED_BODY()

	UPROPERTY(BlueprintReadOnly) int32 Romance = 0;
	UPROPERTY(BlueprintReadOnly) int32 Friendship = 0;
	UPROPERTY(BlueprintReadOnly) int32 Friction = 0;

	/** Completed conversations. */
	UPROPERTY(BlueprintReadOnly) int32 Visits = 0;

	/** Has the intro card been shown? */
	UPROPERTY(BlueprintReadOnly) bool bMet = false;

	/** Has the house problem been repaired (arc complete)? */
	UPROPERTY(BlueprintReadOnly) bool bFixed = false;

	/** romance_success | romance_failure | friend_success | friend_failure, empty while the arc is running. */
	UPROPERTY(BlueprintReadOnly) FString Ending;

	UPROPERTY(BlueprintReadOnly) TArray<FString> SeenNodes;

	/** Week of the last story conversation (one story beat per hunk per day). */
	UPROPERTY(BlueprintReadOnly) int32 LastTalkWeek = 0;
};

USTRUCT(BlueprintType)
struct FFixHimSaveData
{
	GENERATED_BODY()

	UPROPERTY() int32 Version = 1;
	/** Each playable day is one week: 1-4. 5 = the final inspection has happened. */
	UPROPERTY() int32 Week = 1;
	/** The heroine's name, chosen at New Game. Fills {player} in dialogue. */
	UPROPERTY() FString PlayerName;
	UPROPERTY() FString SavedAt;
	UPROPERTY() float PlaySeconds = 0.f;

	UPROPERTY() FString CurrentRoom;
	UPROPERTY() FVector PlayerLocation = FVector::ZeroVector;
	UPROPERTY() float PlayerYaw = 0.f;
	UPROPERTY() bool bHasPlayerTransform = false;

	UPROPERTY() TMap<FString, FHunkProgress> Hunks;
	UPROPERTY() TMap<FString, int32> Flags;
};

/** Player options, saved separately from progress so "New Game" keeps them. */
USTRUCT(BlueprintType)
struct FFixHimOptions
{
	GENERATED_BODY()

	UPROPERTY() float MasterVolume = 1.f;
	UPROPERTY() float MusicVolume = 0.5f;
	UPROPERTY() float MouseSensitivity = 1.f;
	UPROPERTY() bool bInvertY = false;
	/** Multiplier on the typewriter speed. 0 = instant. */
	UPROPERTY() float TextSpeed = 1.f;
	UPROPERTY() bool bFullscreen = false;
};
