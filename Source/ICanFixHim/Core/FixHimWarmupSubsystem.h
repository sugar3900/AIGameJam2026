// I Can Fix Him - AI Game Jam 2026

#pragma once

#include "CoreMinimal.h"
#include "Subsystems/WorldSubsystem.h"
#include "FixHimWarmupSubsystem.generated.h"

/**
 * Prepares everything gameplay loads on demand while the loading screen is up, before the title, so nothing compiles
 * or pops in the first time it is shown. The game has a single level, so this runs once per session.
 *
 * - Loads every gameplay material, mesh and texture (settings assets plus each hunk's look) and keeps them loaded
 *   for the whole session. Effect and dialogue materials would otherwise be garbage collected between uses and
 *   reload, which in the editor fetches or compiles their shaders again mid-game.
 * - Spawns one hidden instance of every entrance/exit effect so its components request their pipeline states
 *   (PSO precaching) now rather than on the first real entrance in a packaged build.
 * - Reports ready once outstanding shader/texture compilation (editor) and PSO precache requests have drained.
 *   Nothing blocks the game thread, so the loading screen keeps drawing meanwhile.
 */
UCLASS()
class ICANFIXHIM_API UFixHimWarmupSubsystem : public UTickableWorldSubsystem
{
	GENERATED_BODY()

public:
	static UFixHimWarmupSubsystem* Get(const UObject* WorldContext);

	/** True once everything has been prepared (or the safety timeout passed). */
	bool IsReady() const { return bReady; }
	/** 0..1, never goes backwards. */
	float GetProgress() const { return Progress; }

	virtual void OnWorldBeginPlay(UWorld& InWorld) override;
	virtual void Tick(float DeltaTime) override;
	virtual TStatId GetStatId() const override;

protected:
	virtual bool DoesSupportWorldType(const EWorldType::Type WorldType) const override;

private:
	void LoadGameplayAssets();
	void WarmEffects(UWorld& World);
	/** Shader maps / textures still compiling (editor) plus PSO precache requests still in flight. */
	int32 CountRemainingWork() const;

	/** Strong references so warmed assets stay loaded (and their shaders stay ready) between uses. */
	UPROPERTY(Transient)
	TArray<TObjectPtr<UObject>> Retained;

	bool bStarted = false;
	bool bReady = false;
	double StartTime = 0.0;
	int32 FramesTicked = 0;
	int32 IdleFrames = 0;
	int32 PeakRemaining = 0;
	float Progress = 0.f;
};
