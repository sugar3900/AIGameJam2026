// I Can Fix Him - AI Game Jam 2026

#pragma once

#include "CoreMinimal.h"
#include "FixHimSaveTypes.generated.h"

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
};

USTRUCT(BlueprintType)
struct FFixHimSaveData
{
	GENERATED_BODY()

	UPROPERTY() int32 Version = 1;
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
	UPROPERTY() float MouseSensitivity = 1.f;
	UPROPERTY() bool bInvertY = false;
	/** Multiplier on the typewriter speed. 0 = instant. */
	UPROPERTY() float TextSpeed = 1.f;
	UPROPERTY() bool bFullscreen = false;
};
