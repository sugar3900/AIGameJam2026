// I Can Fix Him - AI Game Jam 2026

#pragma once

#include "CoreMinimal.h"
#include "Subsystems/GameInstanceSubsystem.h"
#include "FixHimWarmupSubsystem.generated.h"

/**
 * Prepares everything gameplay loads on demand while the startup loading screen is up, so nothing compiles or pops in
 * the first time it is shown. Lives on the game instance: warmed once per session, and the assets stay loaded across
 * the level reload that returning to the title performs.
 *
 * - Loads every gameplay material, mesh and texture (settings assets plus each hunk's look) and keeps them loaded.
 *   Effect and dialogue materials would otherwise be garbage collected between uses and reload, which in the editor
 *   fetches or compiles their shaders again mid-game.
 * - Spawns one hidden instance of every entrance/exit effect so its components request their pipeline states
 *   (PSO precaching) now rather than on the first real entrance in a packaged build.
 * - Reports ready once outstanding shader/texture compilation (editor) and PSO precache requests have drained.
 *
 * Driven by AFixHimPlayerController: Begin() from BeginPlay, Update() every tick until it returns true.
 */
UCLASS()
class ICANFIXHIM_API UFixHimWarmupSubsystem : public UGameInstanceSubsystem
{
	GENERATED_BODY()

public:
	static UFixHimWarmupSubsystem* Get(const UObject* WorldContext);

	/** True once a warmup has completed this session; later level loads need no loading screen. */
	bool IsWarmed() const { return bWarmed; }

	/** Loads and retains the gameplay assets and builds the hidden effects in World. Asset loading is synchronous. */
	void Begin(UWorld& World);
	/** Call once per frame after Begin. Returns true once everything is prepared; never gives up early. */
	bool Update();
	/** 0..1, advances as individual shader/texture/PSO items finish; never goes backwards. */
	float GetProgress() const { return Progress; }

private:
	void LoadGameplayAssets();
	void WarmEffects(UWorld& World);
	/** Shader maps / textures still compiling (editor) plus PSO precache requests still in flight. */
	int32 CountRemainingWork() const;

	/** Strong references so warmed assets stay loaded (and their shaders stay ready) for the whole session. */
	UPROPERTY(Transient)
	TArray<TObjectPtr<UObject>> Retained;

	bool bStarted = false;
	bool bWarmed = false;
	double StartTime = 0.0;
	double NextReportTime = 0.0;
	double NextTraceTime = 0.0;
	double LastUpdateTime = 0.0;
	/** Frame time (each frame clamped) since the bar last moved; caps how far the next step may go. */
	float AdvanceBudgetSeconds = 0.f;
	int32 FramesTicked = 0;
	int32 IdleFrames = 0;
	int32 PeakRemaining = 0;
	/** Outstanding work last frame; drops between frames count as finished items. */
	int32 LastRemaining = 0;
	float Progress = 0.f;
};
