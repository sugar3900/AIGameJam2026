#pragma once
#include "UI/FixHimUI.h"
#include "FixHimDesignReview.generated.h"
/** In-engine component catalogue. Console: FixHim.DesignSystem. Does not alter progress. */
UCLASS()
class ICANFIXHIM_API UFixHimDesignReviewWidget : public UFixHimWidget
{
 GENERATED_BODY()
public:
 TFunction<void()> OnClose;
protected:
 virtual void BuildUI() override;
 virtual bool HandleClickOutside() override;
};
