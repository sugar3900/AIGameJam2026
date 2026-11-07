// I Can Fix Him - AI Game Jam 2026

#pragma once

#include "CoreMinimal.h"
#include "Subsystems/GameInstanceSubsystem.h"
#include "Core/FixHimSaveTypes.h"
#include "FixHimSaveSubsystem.generated.h"

DECLARE_MULTICAST_DELEGATE(FOnFixHimSaved);
DECLARE_MULTICAST_DELEGATE(FOnFixHimPreSave);
DECLARE_MULTICAST_DELEGATE_ThreeParams(FOnStatChanged, const FString& /*HunkId*/, ERelationshipAxis, int32 /*Delta*/);

/**
 * Owns the progress + options structs and persists them as human-readable JSON in Saved/SaveGames/.
 * The game auto-saves after every conversation and room change.
 */
UCLASS()
class ICANFIXHIM_API UFixHimSaveSubsystem : public UGameInstanceSubsystem
{
	GENERATED_BODY()

public:
	static UFixHimSaveSubsystem* Get(const UObject* WorldContext);

	virtual void Initialize(FSubsystemCollectionBase& Collection) override;

	// ---- Progress ---------------------------------------------------------

	bool HasSaveFile() const;
	void NewGame();
	bool LoadGame();
	bool SaveGame();
	void DeleteSave();

	FFixHimSaveData& Data() { return SaveData; }
	const FFixHimSaveData& Data() const { return SaveData; }

	FHunkProgress& Hunk(const FString& HunkId) { return SaveData.Hunks.FindOrAdd(HunkId); }
	const FHunkProgress* FindHunk(const FString& HunkId) const { return SaveData.Hunks.Find(HunkId); }

	int32 GetFlag(const FString& Name) const;
	void AddFlag(const FString& Name, int32 Delta);
	void AddStat(const FString& HunkId, ERelationshipAxis Axis, int32 Delta);

	int32 CountFixed() const;

	/** Fired before writing so gameplay can stash transient state (player transform, room). */
	FOnFixHimPreSave OnPreSave;
	FOnFixHimSaved OnSaved;
	FOnStatChanged OnStatChanged;

	// ---- Options ----------------------------------------------------------

	FFixHimOptions& Options() { return OptionsData; }
	const FFixHimOptions& Options() const { return OptionsData; }
	void SaveOptions();
	void ApplyOptions();

	FString GetSavePath() const;
	FString GetOptionsPath() const;

private:
	UPROPERTY() FFixHimSaveData SaveData;
	UPROPERTY() FFixHimOptions OptionsData;

	double SessionStartTime = 0.0;
};
