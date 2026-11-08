// I Can Fix Him - AI Game Jam 2026

#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Character.h"
#include "FixHimHunk.generated.h"

class USceneCaptureComponent2D;
class UMaterialInstanceDynamic;
class UTextureRenderTarget2D;
struct FHunkDefinition;

/**
 * The man trapped inside a house malady. Spawned hidden by AFixHimMalady and
 * popped into existence when the player clicks the glowing fixture.
 * Owns a scene capture used for the dialogue portrait and the intro silhouette.
 */
UCLASS()
class ICANFIXHIM_API AFixHimHunk : public ACharacter
{
	GENERATED_BODY()

public:
	AFixHimHunk();

	virtual void BeginPlay() override;
	virtual void Tick(float DeltaSeconds) override;

	/** Apply body tint, scale and props from the dialogue JSON. */
	void ApplyDefinition(const FHunkDefinition& Def);

	/**
	 * Gentle entrance: after a short beat he grows out of the fixture at From (world location, usually the malady's
	 * centre) to his stand location with a soft ease, while sparkles spiral up and a soft chime plays. Total ~1.25 s.
	 */
	void Appear(const FVector& From);
	void Appear() { Appear(GetActorLocation()); }
	/**
	 * bBubblePop: he swells slightly and pops like a soap bubble (sparkles, bubbles, BubblePop sound). Otherwise he
	 * is hidden at once with no sound (day transitions, finale, debug).
	 */
	void Disappear(bool bBubblePop = true);
	/** Seconds from Appear() until he's fully grown in. */
	static constexpr float AppearDelay = 0.3f;
	static constexpr float AppearGrowSeconds = 0.95f;
	/** How long each style's transition takes. Arrivals must stay within AppearGrowSeconds; the bubble "pop" out is quick. */
	static float InSeconds(int32 Style) { static const float V[] = { 0.8f, 0.8f, 0.95f, 0.7f }; return V[Style]; }
	static float OutSeconds(int32 Style) { static const float V[] = { 0.22f, 0.6f, 0.85f, 0.5f }; return V[Style]; }
	bool IsPresent() const { return bPresent; }
	/** True while he is forming or being taken apart (the fixture can't be used until it is over). */
	bool IsTransitioning() const { return PopAnim != EPopAnim::None; }

	/** The dialogue portrait is a still taken when the hunk first appears; this makes sure one exists (capturing now if not). */
	void SetPortraitLive(bool bLive);
	UTextureRenderTarget2D* GetPortrait() const { return PortraitTarget; }
	/** Re-render the portrait target. bAsStill marks the result as the dialogue still (taken once, on first appearance). */
	void CapturePortraitNow(bool bAsStill = false);

	/** One-off head-to-waist capture into Target (used for the end-of-game keepsake). */
	void CaptureKeepsake(UTextureRenderTarget2D* Target);

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Hunk")
	FString HunkId;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Components")
	TObjectPtr<USceneCaptureComponent2D> PortraitCapture;

private:
	void SetPresentImmediate(bool bVisible);

	UPROPERTY(Transient)
	TObjectPtr<UTextureRenderTarget2D> PortraitTarget;

	enum class EPopAnim : uint8 { None, Appear, Pop };
	/**
	 * How he arrives or leaves, set per character in the dialogue JSON (look.entrance / look.exit):
	 *   Bubble  forms in a shimmer of transparent bubbles / pops out like a soap bubble (the default)
	 *   Sparkle forms on a spiral of glitter / vanishes in a burst of it
	 *   Spores  materialises out of a cloud of black spores / dissolves into one
	 *   Surge   forms from an electrical surge / is torn apart by one
	 * Nothing ever grows or shrinks: every style runs the M_Hunk dissolve shader (Tools/Editor/add_hunk_dissolve.py)
	 * with its own edge look.
	 */
	enum class EEntrance : uint8 { Bubble, Sparkle, Spores, Surge };
	static EEntrance ParseEntrance(const FString& Name);
	/** Spawn the burst and sound for a transition at a world location. bIn: arriving, otherwise leaving. */
	void PlayEntranceFx(const FVector& At, bool bIn);
	/** Drive the dissolve shader for the given transition (0 = nothing of him exists, 1 = fully formed). */
	void SetForm(float Alpha, EEntrance Style);
	EEntrance Enter = EEntrance::Bubble;
	EEntrance Leave = EEntrance::Bubble;
	float FormAlpha = 1.f;
	float LeaveStartForm = 1.f;
	bool bLeaveFxPlayed = false;
	UPROPERTY(Transient)
	TArray<TObjectPtr<UMaterialInstanceDynamic>> FormMIDs;

	float BaseScale = 1.f;
	/** The hunk's glow colour (look.glow), tints his sparkles and bubbles. */
	FLinearColor GlowColor = FLinearColor(1.f, 0.4f, 0.7f);
	EPopAnim PopAnim = EPopAnim::None;
	float PopTime = 0.f;
	FVector AppearTo = FVector::ZeroVector;
	bool bPresent = false;
	bool bHasStill = false;
	FTimerHandle StillTimer;
	float Age = 0.f;
};
