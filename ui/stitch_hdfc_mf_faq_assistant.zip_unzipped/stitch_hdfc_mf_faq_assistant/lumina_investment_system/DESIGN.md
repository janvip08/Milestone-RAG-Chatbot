---
name: Lumina Investment System
colors:
  surface: '#07122a'
  surface-dim: '#07122a'
  surface-bright: '#2f3952'
  surface-container-lowest: '#030d25'
  surface-container-low: '#101b33'
  surface-container: '#151f37'
  surface-container-high: '#1f2942'
  surface-container-highest: '#2a344e'
  on-surface: '#d9e2ff'
  on-surface-variant: '#bacac1'
  inverse-surface: '#d9e2ff'
  inverse-on-surface: '#263049'
  outline: '#85948c'
  outline-variant: '#3c4a43'
  surface-tint: '#2fe0aa'
  primary: '#44edb7'
  on-primary: '#003828'
  primary-container: '#00d09c'
  on-primary-container: '#00533c'
  inverse-primary: '#006c4f'
  secondary: '#4cd6fb'
  on-secondary: '#003642'
  secondary-container: '#00b2d6'
  on-secondary-container: '#003f4e'
  tertiary: '#d0d3e1'
  on-tertiary: '#2c303b'
  tertiary-container: '#b4b7c5'
  on-tertiary-container: '#444854'
  error: '#ffb4ab'
  on-error: '#690005'
  error-container: '#93000a'
  on-error-container: '#ffdad6'
  primary-fixed: '#59fdc5'
  primary-fixed-dim: '#2fe0aa'
  on-primary-fixed: '#002116'
  on-primary-fixed-variant: '#00513b'
  secondary-fixed: '#b3ebff'
  secondary-fixed-dim: '#4cd6fb'
  on-secondary-fixed: '#001f27'
  on-secondary-fixed-variant: '#004e5f'
  tertiary-fixed: '#dfe2f1'
  tertiary-fixed-dim: '#c3c6d4'
  on-tertiary-fixed: '#171b26'
  on-tertiary-fixed-variant: '#434652'
  background: '#07122a'
  on-background: '#d9e2ff'
  surface-variant: '#2a344e'
typography:
  display-lg:
    fontFamily: Outfit
    fontSize: 48px
    fontWeight: '700'
    lineHeight: 56px
    letterSpacing: -0.02em
  headline-lg:
    fontFamily: Outfit
    fontSize: 32px
    fontWeight: '600'
    lineHeight: 40px
    letterSpacing: -0.01em
  headline-lg-mobile:
    fontFamily: Outfit
    fontSize: 28px
    fontWeight: '600'
    lineHeight: 36px
  headline-md:
    fontFamily: Outfit
    fontSize: 24px
    fontWeight: '600'
    lineHeight: 32px
  body-lg:
    fontFamily: Inter
    fontSize: 18px
    fontWeight: '400'
    lineHeight: 28px
  body-md:
    fontFamily: Inter
    fontSize: 16px
    fontWeight: '400'
    lineHeight: 24px
  label-md:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: '500'
    lineHeight: 20px
    letterSpacing: 0.01em
  label-sm:
    fontFamily: Inter
    fontSize: 12px
    fontWeight: '600'
    lineHeight: 16px
    letterSpacing: 0.05em
rounded:
  sm: 0.25rem
  DEFAULT: 0.5rem
  md: 0.75rem
  lg: 1rem
  xl: 1.5rem
  full: 9999px
spacing:
  unit: 4px
  xs: 4px
  sm: 8px
  md: 16px
  lg: 24px
  xl: 40px
  xxl: 64px
  gutter: 24px
  margin-mobile: 16px
  margin-desktop: 48px
---

## Brand & Style
The design system is engineered for high-stakes financial environments where precision meets modern aesthetics. It targets sophisticated investors who value clarity and a forward-thinking technical edge. 

The visual style is **Glassmorphic Modernism**. It leverages deep-space backgrounds with translucent surface layers to create a sense of infinite depth. High-contrast neon accents provide immediate visual feedback and highlight critical growth metrics. The emotional response is one of calm confidence, professional reliability, and technological advancement.

## Colors
This design system utilizes a sophisticated dark palette anchored by a "Deep Space" primary background. 

- **Primary Neon Mint (#00d09c):** Reserved for "Buy" actions, positive growth trends, and primary calls-to-action.
- **Secondary Bright Cyan (#00b4d8):** Used for informative highlights, secondary interactive elements, and focused states.
- **Typography Tiers:** High-impact information uses Pure White (#ffffff). Functional body copy uses Soft Gray-White (#e2e8f0) to reduce eye strain. Metadata and labels utilize Muted Cool Gray (#8892b0).
- **Surface Strategy:** Backgrounds are never flat; they use a layered approach with 80% opacity containers to allow subtle radial glows to bleed through from the base layer.

## Typography
The typography strategy pairs the geometric, premium feel of **Outfit** for headings with the high-legibility of **Inter** for data-dense body content.

Headlines should always utilize white (#ffffff) to punch through the dark background. Body text uses a slightly softened white (#e2e8f0) to ensure long-form reading comfort. Numerical data, especially in dashboards, should prioritize tabular figures where possible to ensure alignment in columns of fluctuating values.

## Layout & Spacing
This design system employs a **Fluid Grid** model with generous margins to evoke a premium, "un-cluttered" feel. 

- **Desktop:** 12-column grid with 24px gutters. Max-width container of 1440px.
- **Mobile:** 4-column grid with 16px gutters and 16px side margins.
- **Spacing Philosophy:** All spacing must be a multiple of 4px. Use 'xl' (40px) and 'xxl' (64px) for vertical section breathing room to maintain the high-end editorial feel. Components like cards should use 'lg' (24px) internal padding to ensure data isn't cramped.

## Elevation & Depth
Depth is created through **Glassmorphism** rather than traditional drop shadows. 

1.  **Base Layer:** The solid background (#0d111b) occasionally features soft, low-opacity radial gradients in Mint or Cyan (10-15% opacity) to simulate "under-glow" behind key content areas.
2.  **Surface Layer:** Cards and modals use #171e2e at 80% opacity with a `backdrop-filter: blur(12px)`.
3.  **Stroke:** Every elevated surface must have a 1px solid border (#24314c). For active or "hovered" states, this border can transition to the Primary Neon Mint or a subtle gradient.
4.  **Inner Glow:** To enhance the glass effect, apply a very subtle white inner-border (0.5px) at 10% opacity on the top and left edges.

## Shapes
Shapes are consistently rounded to soften the technical nature of financial data. 

Standard components (Cards, Inputs) use a **0.5rem (8px)** corner radius. Larger containers or prominent modal overlays use **1rem (16px)**. Interactive elements like "Chips" or "Pills" for filtering utilize a fully rounded (capsule) radius to differentiate them from actionable buttons or data containers.

## Components
- **Buttons:** Primary buttons are solid Neon Mint with black text for maximum contrast. Secondary buttons use a "Ghost" style with a Cyan border and Cyan text.
- **Cards:** Glassmorphic containers with 24px padding. They should include a 1px border (#24314c). Hover states should increase the border brightness slightly.
- **Inputs:** Darker than the surface layer (#0a0d14) with a 1px border. On focus, the border glows with a 0.5px Cyan solid stroke and a 4px Cyan outer blur.
- **Chips:** Small, pill-shaped tags used for stock categories or status. For positive growth, use a 10% Mint background with solid Mint text.
- **Lists:** Clean rows with 1px bottom borders (#24314c). Include a subtle chevron in #8892b0 for navigable items.
- **Charts/Graphs:** Use Primary Mint for positive trends and a soft Red-Pink for negative. Background grid lines on charts should be barely visible (#24314c at 50% opacity).