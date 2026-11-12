---
name: DevStreet Kinetic Engine
colors:
  surface: '#fcf8fa'
  surface-dim: '#dcd9db'
  surface-bright: '#fcf8fa'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#f6f3f5'
  surface-container: '#f0edef'
  surface-container-high: '#eae7e9'
  surface-container-highest: '#e4e2e4'
  on-surface: '#1b1b1d'
  on-surface-variant: '#45464d'
  inverse-surface: '#303032'
  inverse-on-surface: '#f3f0f2'
  outline: '#76777d'
  outline-variant: '#c6c6cd'
  surface-tint: '#565e74'
  primary: '#000000'
  on-primary: '#ffffff'
  primary-container: '#131b2e'
  on-primary-container: '#7c839b'
  inverse-primary: '#bec6e0'
  secondary: '#a73a00'
  on-secondary: '#ffffff'
  secondary-container: '#fd651e'
  on-secondary-container: '#571a00'
  tertiary: '#000000'
  on-tertiary: '#ffffff'
  tertiary-container: '#271901'
  on-tertiary-container: '#98805d'
  error: '#ba1a1a'
  on-error: '#ffffff'
  error-container: '#ffdad6'
  on-error-container: '#93000a'
  primary-fixed: '#dae2fd'
  primary-fixed-dim: '#bec6e0'
  on-primary-fixed: '#131b2e'
  on-primary-fixed-variant: '#3f465c'
  secondary-fixed: '#ffdbce'
  secondary-fixed-dim: '#ffb599'
  on-secondary-fixed: '#370e00'
  on-secondary-fixed-variant: '#7f2b00'
  tertiary-fixed: '#fcdeb5'
  tertiary-fixed-dim: '#dec29a'
  on-tertiary-fixed: '#271901'
  on-tertiary-fixed-variant: '#574425'
  background: '#fcf8fa'
  on-background: '#1b1b1d'
  surface-variant: '#e4e2e4'
typography:
  headline-xl:
    fontFamily: Poppins
    fontSize: 40px
    fontWeight: '700'
    lineHeight: 48px
    letterSpacing: -0.02em
  headline-xl-mobile:
    fontFamily: Poppins
    fontSize: 30px
    fontWeight: '700'
    lineHeight: 38px
    letterSpacing: -0.015em
  headline-lg:
    fontFamily: Poppins
    fontSize: 32px
    fontWeight: '600'
    lineHeight: 40px
    letterSpacing: -0.015em
  headline-lg-mobile:
    fontFamily: Poppins
    fontSize: 24px
    fontWeight: '600'
    lineHeight: 32px
    letterSpacing: -0.01em
  headline-md:
    fontFamily: Poppins
    fontSize: 24px
    fontWeight: '600'
    lineHeight: 32px
    letterSpacing: -0.01em
  headline-sm:
    fontFamily: Poppins
    fontSize: 18px
    fontWeight: '600'
    lineHeight: 26px
  body-lg:
    fontFamily: Poppins
    fontSize: 16px
    fontWeight: '400'
    lineHeight: 26px
  body-md:
    fontFamily: Poppins
    fontSize: 14px
    fontWeight: '400'
    lineHeight: 22px
  body-sm:
    fontFamily: Poppins
    fontSize: 12px
    fontWeight: '400'
    lineHeight: 18px
  label-lg:
    fontFamily: JetBrains Mono
    fontSize: 14px
    fontWeight: '600'
    lineHeight: 20px
    letterSpacing: -0.01em
  label-md:
    fontFamily: JetBrains Mono
    fontSize: 12px
    fontWeight: '500'
    lineHeight: 16px
    letterSpacing: 0.02em
  label-sm:
    fontFamily: JetBrains Mono
    fontSize: 11px
    fontWeight: '500'
    lineHeight: 14px
    letterSpacing: 0.04em
  code-inline:
    fontFamily: JetBrains Mono
    fontSize: 13px
    fontWeight: '400'
    lineHeight: 18px
rounded:
  sm: 0.25rem
  DEFAULT: 0.5rem
  md: 0.75rem
  lg: 1rem
  xl: 1.5rem
  full: 9999px
spacing:
  gutter: 1.5rem
  gutter-sm: 1rem
  margin: 2rem
  margin-sm: 1rem
  space-xs: 0.25rem
  space-sm: 0.5rem
  space-md: 1rem
  space-lg: 1.5rem
  space-xl: 2rem
  space-2xl: 3rem
---

## Brand & Style

This design system expresses a forward-leaning, engineering-first culture rooted in modern tech hubs and developer communities. The aesthetic bridges high-performance developer tooling (precise, utilitarian, information-dense) with a vibrant, human-centered creative drive.

The design philosophy combines:
- **Modern Developer Pragmatism:** Crisp structure, monospaced metadata, tight alignment, high legibility, and no extraneous decoration.
- **Warm Kinetic Energy:** Intense, focused accents of energetic orange balanced against deep slate and charcoal backdrops.
- **Tonal Clarity:** High-contrast text hierarchy paired with soft background planes that reduce cognitive fatigue during prolonged coding and review sessions.

## Colors

The palette establishes an authoritative, developer-centric hierarchy:

- **Primary (`#0F172A` - Dark Slate / Navy):** Represents stability, logic, and command. Anchors structural navigation, primary action controls, key headlines, and inverted code blocks.
- **Secondary (`#EA580C` - Energetic Orange):** Supplies concentrated kinetic punch. Reserved strictly for active indicators, status highlights, high-priority CTAs, focus indicators, and key metric badges.
- **Tertiary (`#64748B` - Slate Grey):** Manages supportive UI structures, unselected tab items, secondary copy, input placeholders, and structural dividers.
- **Neutral Surface (`#F8FAFC` - Light Slate Canvas):** A crisp, low-glare canvas complemented by pure white (`#FFFFFF`) card containers and sharp edge dividers (`#E2E8F0`).

### Functional Roles
- **Success:** `#10B981` (Emerald) for passing pipelines, verified keys, and successful builds.
- **Warning:** `#F59E0B` (Amber) for pending reviews, merge conflicts, and deprecation notices.
- **Danger / Destructive:** `#EF4444` (Crimson) for branch deletion, critical bugs, and broken builds.

## Typography

The typographic hierarchy utilizes two precise typefaces:

- **Poppins:** Selected for all structural headlines, titles, and body prose. It offers clean proportions with geometric clarity, ensuring swift scanning across dashboards and code documentation.
- **JetBrains Mono:** Selected for developer-first data layers—hashes, branches, versions, endpoint URIs, metrics, technical chips, and key/value tables.

### Rules for Application
- Never set narrative body copy in monospace.
- Set all tags, badges, terminal outputs, and code parameters in `JetBrains Mono`.
- Headings above 24px must use tight negative letter-spacing (`-0.015em` to `-0.02em`) to maintain structural density.

## Layout & Spacing

The layout is built upon an 8pt base grid that enforces balanced data density, mirroring modern repository platforms and terminal tooling:

- **Desktop (1280px+):** 12-column responsive fluid grid with `margin: 2rem` and `gutter: 1.5rem`. Maximum content container spans 1440px.
- **Tablet (768px - 1279px):** 8-column layout with `gutter: 1rem` and `margin: 1.5rem`.
- **Mobile (< 768px):** 4-column layout with `gutter: 0.75rem` and `margin: 1rem`.

Compact element grouping leverages `space-xs` (4px) and `space-sm` (8px) to keep related attributes, author badges, and metadata tags tightly paired.

## Elevation & Depth

This system avoids heavy, blurred drop shadows, relying instead on clean surface transitions, crisp structural outlines, and subtle ambient occlusion.

- **Level 0 (Base Canvas):** Background color `#F8FAFC`. Zero elevation, zero shadow.
- **Level 1 (Card & Module Containers):** Surface `#FFFFFF`, surrounded by a 1px border of `#E2E8F0`. Shadow: `0 1px 3px 0 rgba(15, 23, 42, 0.04), 0 1px 2px -1px rgba(15, 23, 42, 0.02)`.
- **Level 2 (Hover States & Context Panels):** Surface `#FFFFFF` with outline `#CBD5E1`. Shadow: `0 4px 6px -1px rgba(15, 23, 42, 0.07), 0 2px 4px -2px rgba(15, 23, 42, 0.05)`.
- **Level 3 (Dropdowns, Command Palettes, Modals):** Surface `#FFFFFF` with `#0F172A` hairline ring (`rgba(15, 23, 42, 0.08)`). Shadow: `0 20px 25px -5px rgba(15, 23, 42, 0.1), 0 8px 10px -6px rgba(15, 23, 42, 0.06)`.
- **Dark Mode / Inverted Blocks:** Solid `#0F172A` background, border `#1E293B`, subtle top ambient inner light (`1px inset rgba(255, 255, 255, 0.05)`).

## Shapes

The shape system employs deliberate, moderate curvature to maintain a clean engineering aesthetic without feeling cold or brutalist:

- **Standard Containers & Cards:** `rounded-lg` (8px / `0.5rem`) for cards, dialog windows, code review diff panels, and inputs.
- **Outer Shells & Hero Modules:** `rounded-xl` (12px to 16px) for master viewports and feature containers.
- **Tags, Micro-Pills & Key Indicators:** `rounded-sm` (4px) or pill (`9999px`) strictly for status badges (e.g., `v2.4.0`, `merged`, `online`).
- **Inner Controls:** Nested items (such as segmented switches inside a search bar) use `rounded-md` (6px) to nest symmetrically inside 8px-12px outer containers.

## Components

### Buttons
- **Primary:** Background `#0F172A`, text `#FFFFFF`, border none. Hover: `#1E293B`. Focus: ring 2px `#EA580C` with 2px offset.
- **Secondary:** Background `#F1F5F9`, text `#0F172A`, border 1px solid `#E2E8F0`. Hover: `#E2E8F0`.
- **Accent (Kinetic):** Background `#EA580C`, text `#FFFFFF`. Hover: `#C2410C`. Used for deployment triggers, main conversion points, and new creation actions.
- **Outlined:** Background transparent, text `#0F172A`, border 1px solid `#CBD5E1`. Hover: `#F8FAFC` and border `#94A3B8`.
- **Inverted / Dark:** Background `#0F172A`, text `#F8FAFC`, border 1px solid `#334155`.

### Input Fields & Search Bars
- **Search Bar:** Height 40px, background `#F8FAFC` or `#FFFFFF`, border 1px solid `#E2E8F0`, corner radius 8px (`rounded-lg`). Leading icon in `#64748B`. Placeholder text in `#94A3B8`. Monospaced keyboard shortcut badge (`⌘K`) right-aligned with `#F1F5F9` background and `#64748B` label.
- **Form Input:** Height 38px, font `Poppins` 14px. Focus state shifts border directly to `#0F172A` with an ambient ring of `#EA580C` at 20% opacity.

### Chips & Technical Tags
- Built using `JetBrains Mono` at `label-md` or `label-sm`.
- **Repository / Technology Tag:** Height 24px, padding 2px 8px, background `#F1F5F9`, border 1px solid `#E2E8F0`, text `#334155`.
- **Active / Accent Tag:** Background `rgba(234, 88, 12, 0.1)`, border 1px solid `rgba(234, 88, 12, 0.25)`, text `#EA580C`.

### Cards & Code Surfaces
- **Feature Card:** Background `#FFFFFF`, 1px border `#E2E8F0`, radius 12px, padding 20px.
- **Terminal / Code Block:** Background `#0F172A`, border 1px solid `#1E293B`, text `#F8FAFC`, syntax accentuation powered by `#EA580C`, `#38BDF8`, and `#4ADE80`.

### Selection Controls
- **Checkboxes & Radios:** 18px square/circle, border 1.5px `#CBD5E1`, border radius 4px (checkbox). Checked state: fill `#0F172A` with white tick, or accent `#EA580C` for targeted states.