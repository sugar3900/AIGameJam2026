#include "UI/FixHimDesign.h"
#include "UI/FixHimUI.h"
#include "Core/FixHimSaveSubsystem.h"
#include "Blueprint/WidgetTree.h"
#include "Components/BorderSlot.h"
#include "Components/ButtonSlot.h"
#include "Components/VerticalBoxSlot.h"
#include "Widgets/SBoxPanel.h"
#include "Components/Image.h"
#include "Engine/Texture2D.h"
#include "Engine/Engine.h"
#include "Framework/Application/SlateApplication.h"
#include "Rendering/DrawElementTypes.h"
#include "Rendering/SlateRenderer.h"
#include "Styling/CoreStyle.h"
#include "Widgets/Input/SButton.h"
#include "Widgets/Layout/SBorder.h"

namespace
{
 // Rounded rectangle in a sheared coordinate frame, tessellated with an antialiased outer fringe.
 void Shape(FSlateWindowElementList& Out, int32 Layer, const FGeometry& G, FVector2f Origin,
   FVector2f Size, float Radius, bool Slanted, FLinearColor Top, FLinearColor Bottom, FLinearColor Tint)
 {
  if (Size.X < 2 || Size.Y < 2) return;
  const float Lean = Slanted ? FixHimDesign::Slant : 0.f;
  const float W = Size.X - Size.Y * Lean;
  if (W < 2) return;
  Radius = FMath::Min(Radius, FMath::Min(W, Size.Y) * .5f);
  TArray<FVector2f> Points;
  for (int Corner = 0; Corner < 4; ++Corner)
  {
   const FVector2f C(Corner == 0 || Corner == 3 ? W - Radius : Radius,
    Corner < 2 ? Size.Y - Radius : Radius);
   for (int J = 0; J <= 10; ++J)
   {
    const float A = (Corner * 90.f + J * 9.f) * PI / 180.f;
    FVector2f P = C + FVector2f(FMath::Cos(A), FMath::Sin(A)) * Radius;
    P.X += (Size.Y - P.Y) * Lean;
    Points.Add(P + Origin);
   }
  }
  const FVector2f Center = Origin + Size * .5f;
  const auto Color = [&](FVector2f P, float Alpha)
  {
   FLinearColor C = FMath::Lerp(Top, Bottom, FMath::Clamp((P.Y-Origin.Y)/Size.Y, 0.f, 1.f)) * Tint;
   C.A *= Alpha;
   return C.ToFColor(true); // Slate RHI packs vertex colors in sRGB, like the stock batcher.
  };
  TArray<FSlateVertex> V;
  TArray<SlateIndex> Indices;
  const auto Add = [&](FVector2f P, float Alpha)
  {
   V.Add(FSlateVertex::Make<ESlateVertexRounding::Disabled>(G.GetAccumulatedRenderTransform(), P,
    FVector2f(.5f,.5f), Color(P,Alpha)));
  };
  Add(Center,1);
  const float Fringe = 1.f / G.GetAccumulatedLayoutTransform().GetScale();
  for (int I=0; I<Points.Num(); ++I)
  {
   const FVector2f P = Points[I];
   const FVector2f Prev = Points[(I+Points.Num()-1)%Points.Num()];
   const FVector2f Next = Points[(I+1)%Points.Num()];
   FVector2f Tangent = (Next-Prev).GetSafeNormal();
   Add(P,1); Add(P + FVector2f(Tangent.Y,-Tangent.X)*Fringe,0);
  }
  for (int I=0; I<Points.Num(); ++I)
  {
   const SlateIndex A=1+I*2, B=1+((I+1)%Points.Num())*2;
   Indices.Append({0,A,B,A,SlateIndex(A+1),B,SlateIndex(A+1),SlateIndex(B+1),B});
  }
  const FSlateResourceHandle Resource = FSlateApplication::Get().GetRenderer()->GetResourceHandle(*FCoreStyle::Get().GetBrush("WhiteBrush"));
  FSlateDrawElement::MakeCustomVerts(Out,Layer,Resource,V,Indices,nullptr,0,0);
 }
 void Surface(FSlateWindowElementList& Out,int32 Layer,const FGeometry& G,FLinearColor Fill,
   FLinearColor Tint,bool Slanted,bool Focused,bool Pressed,bool Enabled)
 {
  using namespace FixHimDesign;
  const FVector2f Size(G.GetLocalSize());
  const float R = Size.Y > 140 ? 22.f : 12.f;
  const FVector2f FaceSize = Size-FVector2f(12,15);
  FLinearColor Top=Fill, Bottom=Fill;
  if (Fill.Equals(Teal,.015f)) { Top=FLinearColor::FromSRGBColor(FColor::FromHex(TEXT("287F91"))); Bottom=FLinearColor::FromSRGBColor(FColor::FromHex(TEXT("1A697A"))); }
  if (Fill.Equals(Pink,.015f)) { Top=FLinearColor::FromSRGBColor(FColor::FromHex(TEXT("E80C70"))); Bottom=FLinearColor::FromSRGBColor(FColor::FromHex(TEXT("C90055"))); }
  const FVector2f Offset=Pressed ? FVector2f(3,4) : FVector2f(0,0);
  Shape(Out,Layer,G,FVector2f(9,12),FaceSize,R,Slanted,Ink,Ink,Tint);
  const auto Edge=Enabled ? Orange : DisabledInk;
  Shape(Out,Layer+1,G,FVector2f(4,7),FaceSize,R,Slanted,Edge,Edge,Tint);
  Shape(Out,Layer+2,G,Offset,FaceSize,R,Slanted,Focused ? FLinearColor::White : Edge,Focused ? FLinearColor::White : Edge,Tint);
  Shape(Out,Layer+3,G,Offset+FVector2f(3,3),FaceSize-FVector2f(6,6),R-3,Slanted,Top,Bottom,Tint);
  if (Focused)
  {
   // A visible white diamond is a focus cue independent of fill color.
   TArray<FVector2f> P={FVector2f(17,Size.Y*.5f-4),FVector2f(21,Size.Y*.5f),FVector2f(17,Size.Y*.5f+4),FVector2f(13,Size.Y*.5f),FVector2f(17,Size.Y*.5f-4)};
   FSlateDrawElement::MakeLines(Out,Layer+4,G.ToPaintGeometry(),P,ESlateDrawEffect::None,FLinearColor::White*Tint,true,2);
  }
 }
 class SDesignBorder : public SBorder
 {
 public:
  virtual int32 OnPaint(const FPaintArgs& A,const FGeometry& G,const FSlateRect& C,FSlateWindowElementList& Out,int32 L,const FWidgetStyle& S,bool E) const override
  {
   const FSlateBrush* B=GetBorderImage();
   const auto Fill=(B ? B->GetTint(S) : FLinearColor::White)*GetBorderBackgroundColor().GetColor(S);
   Surface(Out,L,G,Fill,S.GetColorAndOpacityTint(),true,false,false,ShouldBeEnabled(E));
   return SCompoundWidget::OnPaint(A,G,C,Out,L+5,S,E);
  }
 };
 class SDesignButton : public SButton
 {
 public:
  TWeakObjectPtr<UFixHimButton> Owner;
  virtual int32 OnPaint(const FPaintArgs& A,const FGeometry& G,const FSlateRect& C,FSlateWindowElementList& Out,int32 L,const FWidgetStyle& S,bool E) const override
  {
   if(Owner.IsValid() && Owner->bInlineTopic)
   {
    const FVector2f Size(G.GetLocalSize());
    TArray<FVector2f> Line={FVector2f(2,Size.Y-2),FVector2f(Size.X-2,Size.Y-2)};
    FSlateDrawElement::MakeLines(Out,L,G.ToPaintGeometry(),Line,ESlateDrawEffect::None,FixHimDesign::Pink*S.GetColorAndOpacityTint(),true,HasKeyboardFocus() || IsHovered() ? 3.f : 1.5f);
    return SCompoundWidget::OnPaint(A,G,C,Out,L+1,S,E);
   }
   if (!Owner.IsValid() || !Owner->bDesignSurface) return SButton::OnPaint(A,G,C,Out,L,S,E);
   using namespace FixHimDesign;
   const bool Enabled=ShouldBeEnabled(E), Focused=HasKeyboardFocus() || IsHovered() || Owner->bSelected;
   const bool Pressed=IsPressed() || Owner->bPreviewPressed;
   const bool Active=Focused || Pressed;
   const FLinearColor Fill=!Enabled ? Disabled : Owner->bPrimary || Active ? Pink : Cream;
   Surface(Out,L,G,Fill,S.GetColorAndOpacityTint(),true,Focused,Pressed,Enabled);
   FWidgetStyle ChildStyle=S;
   ChildStyle.SetForegroundColor(!Enabled ? DisabledInk : Owner->bPrimary || Active ? FLinearColor::White : Ink);
   // Use foreground on descendants while retaining stock SButton's input/focus/capture behavior.
   return SCompoundWidget::OnPaint(A,G,C,Out,L+5,ChildStyle,Enabled);
  }
 };
}

TSharedRef<SWidget> UFixHimSurface::RebuildWidget()
{
 MyBorder=SNew(SDesignBorder);
 if (GetChildrenCount()) CastChecked<UBorderSlot>(GetContentSlot())->BuildSlot(MyBorder.ToSharedRef());
 return MyBorder.ToSharedRef();
}
TSharedRef<SWidget> UFixHimButton::RebuildWidget()
{
 auto Button=SNew(SDesignButton)
  .OnClicked(BIND_UOBJECT_DELEGATE(FOnClicked,SlateHandleClicked))
  .OnPressed(BIND_UOBJECT_DELEGATE(FSimpleDelegate,SlateHandlePressed))
  .OnReleased(BIND_UOBJECT_DELEGATE(FSimpleDelegate,SlateHandleReleased))
  .OnHovered_UObject(this,&UFixHimButton::SlateHandleHovered)
  .OnUnhovered_UObject(this,&UFixHimButton::SlateHandleUnhovered)
  .OnReceivedFocus_UObject(this,&UFixHimButton::SlateHandleOnReceivedFocus)
  .OnLostFocus_UObject(this,&UFixHimButton::SlateHandleOnLostFocus)
  .ButtonStyle(&GetStyle()).IsFocusable(true)
  .ForegroundColor_Lambda([this]() -> FSlateColor
  {
   if(!bDesignSurface) return FSlateColor::UseForeground();
   return FSlateColor(!GetIsEnabled() ? FixHimDesign::DisabledInk : bPrimary || bSelected || bPreviewPressed || IsHovered() || HasKeyboardFocus() ? FLinearColor::White : FixHimDesign::Ink);
  });
 Button->Owner=this;
 MyButton=Button;
 if (GetChildrenCount()) CastChecked<UButtonSlot>(GetContentSlot())->BuildSlot(MyButton.ToSharedRef());
 return MyButton.ToSharedRef();
}
namespace FixHimDesign
{
 bool ReducedMotion()
 {
  for (const auto& Context : GEngine->GetWorldContexts())
   if (auto* Save=UFixHimSaveSubsystem::Get(Context.World())) return Save->Options().bReducedMotion;
  return false;
 }
 float TextScale()
 {
  for (const auto& Context : GEngine->GetWorldContexts())
   if (auto* Save=UFixHimSaveSubsystem::Get(Context.World())) return Save->Options().UITextScale;
  return 1.f;
 }
 UImage* Icon(UWidgetTree* Tree,const FString& Name,const FLinearColor& Tint)
 {
  UImage* I=Tree->ConstructWidget<UImage>();
  const FString Path=FString::Printf(TEXT("/Game/ICanFixHim/UI/Design/Icons/T_Icon_%s.T_Icon_%s"),*Name,*Name);
  I->SetBrushFromTexture(LoadObject<UTexture2D>(nullptr,*Path));
  I->SetColorAndOpacity(Tint);
  I->SetVisibility(ESlateVisibility::HitTestInvisible);
  return I;
 }
}

namespace
{
 class SDesignStack : public SVerticalBox
 {
 protected:
  virtual FVector2D ComputeDesiredSize(float Scale) const override
  {
   const FVector2D Size=SVerticalBox::ComputeDesiredSize(Scale);
   return Size+FVector2D(Size.Y*FixHimDesign::Slant,0);
  }
  virtual void OnArrangeChildren(const FGeometry& G,FArrangedChildren& Children) const override
  {
   const FVector2D Size=G.GetLocalSize();
   const float Inset=Size.Y*FixHimDesign::Slant;
   FArrangedChildren Base(Children.GetFilter());
   const FGeometry Inner=G.MakeChild(FVector2D(FMath::Max(1.f,Size.X-Inset),Size.Y),FSlateLayoutTransform());
   SVerticalBox::OnArrangeChildren(Inner,Base);
   for(const FArrangedWidget& Child : Base.GetInternalArray())
   {
    FVector2D Pos=G.AbsoluteToLocal(Child.Geometry.GetAbsolutePosition());
    Pos.X+=(Size.Y-Pos.Y-Child.Geometry.GetLocalSize().Y*.5f)*FixHimDesign::Slant;
    Children.AddWidget(G.MakeChild(Child.Widget,Pos,Child.Geometry.GetLocalSize()));
   }
  }
 };
}
TSharedRef<SWidget> UFixHimStack::RebuildWidget()
{
 MyVerticalBox=SNew(SDesignStack);
 for(UPanelSlot* Slot : Slots)
  if(auto* V=Cast<UVerticalBoxSlot>(Slot)) V->BuildSlot(MyVerticalBox.ToSharedRef());
 return MyVerticalBox.ToSharedRef();
}
