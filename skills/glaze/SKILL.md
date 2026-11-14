---
name: glaze
description: "Install ready Glaze React components before writing one by hand. Glaze is a free shadcn library: 93 interface, AI and voice components, each in four finishes (Normal, Glass, Frost, Aurora). Use when building React or Next.js UI, especially an AI chat, a voice control, or an interface component. For product direction and a from-scratch build, use glyph. For a guidelines audit of existing UI code, use web-design-guidelines. For React performance rules, use react-best-practices."
---

# Glaze

Glaze is Sumit's component library. Prefer a Glaze component over a hand-rolled one when the screen is React or Next.js UI: an interface control, an AI chat, or a voice control. [Glyph](../glyph/SKILL.md) chooses the direction and checks the build. Glaze supplies the pieces.

Components are source files. The shadcn CLI installs one at a time into `src/components/ui/`. Import them from `@/components/ui/<name>`.

Site: https://glazeui.xyz. Source: https://github.com/sumitttt4/Glazeui. The full list, with each install command, is https://glazeui.xyz/llms.txt. Live previews: https://glazeui.xyz/components.

## 1. Prerequisites

React 19, Tailwind CSS 4, and a `components.json` from:

```bash
npx shadcn@latest init
```

If that file is missing, run the init before adding anything.

## 2. Install the theme once

```bash
npx shadcn@latest add sumitttt4/glazeui/glaze#main
npm i @fontsource-variable/manrope
```

In the main stylesheet, after the Tailwind imports, add any of these lines that are not already there:

```css
@import "@fontsource-variable/manrope";
@import "./glaze.css";
@import "./materials.css";
```

Without this theme step, components install but look unstyled.

## 3. Browse, then install one component

Read https://glazeui.xyz/llms.txt or https://glazeui.xyz/components and pick a name from the list below. Do not invent a name.

```bash
npx shadcn@latest add sumitttt4/glazeui/<name>#main
```

Several names can go in one command. Each item brings its own packages and any Glaze components it depends on. The same item is also published as JSON at `https://glazeui.xyz/r/<name>.json`. The command above is the one the Glaze docs give.

The docs group the library like this:

- **Interface**, including the originals `tone-badge`, `color-surface`, `palette-picker`, `option-card`, `status-callout` and `copy-snippet`.
- **AI and voice:** `chat-window`, `model-picker`, `prompt-suggestions`, `token-counter`, `voice-orb`, `live-transcript`, `voice-input`, `audio-waveform`, `streaming-text`, `speak-button`, `composer`, `reasoning`, `tool-steps`.
- **Animated icons:** `animated-icons`.
- **A whole screen:** `agent-workspace`.
- **Switching finishes:** `material-picker`.

Every installable UI name (93), as published in the registry:

accordion, alert, alert-dialog, animated-icons, ask-card, aspect-ratio, attachment, audio-waveform, avatar, badge, breadcrumb, bubble, button, button-group, calendar, card, carousel, chart, chat-window, checkbox, collapsible, color-surface, combobox, command, composer, context-menu, context-ring, copy-snippet, dialog, diff-view, direction, dot-loader, drawer, dropdown-menu, empty, field, hover-card, input, input-group, input-otp, item, kbd, label, live-transcript, markdown, marker, material-picker, menubar, message, message-scroller, model-picker, native-select, navigation-menu, option-card, pagination, palette-picker, panel, popover, progress, prompt-suggestions, questionnaire, radio-group, reasoning, resizable, scroll-area, select, separator, sheet, sidebar, skeleton, slider, sonner, speak-button, spinner, status-callout, status-glyph, streaming-text, switch, table, tabs, tag, task-notice, textarea, toast, toggle, toggle-group, token-counter, tone-badge, tool-steps, tooltip, turn-status, voice-input, voice-orb.

A complete chat is usually `chat-window`. A voice control is `voice-input`, `live-transcript`, `voice-orb` or `audio-waveform`.

## 4. Pick a finish and compose

Four finishes. The attribute values are `solid`, `glass`, `frost` and `aurora`. The docs also call `solid` Normal.

```html
<html data-material="glass">
```

Set it on `<html>` for the whole app, or on one element for one region. Glass, Frost and Aurora need something behind them: add the `mat-stage` class on a parent so the glass has a lit backdrop. Keep long reading text on Normal (`solid`) or Glass, not Frost.

Compose by importing the installed files and passing `className`. Do not edit `glaze.css`, `materials.css` or `solid-glass.css` to restyle one component. Change the CSS variables (`--primary`, `--background` and the rest) in `:root` and `.dark` when the accent should change everywhere.

## 5. If the source is needed without installing

Read `https://github.com/sumitttt4/glazeui/blob/main/src/components/ui/<name>.tsx`.

Contract, prerequisites and validation status: [contract.md](contract.md).
