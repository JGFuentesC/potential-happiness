# Design System: Neon Tokyo — Quiniela 2026 Edition

## 1. Visual Identity & "North Star"
**Concept:** *Electric Nightscape*
A retro-futuristic, cyberpunk-inspired aesthetic. The goal is to make a sports prediction app feel like a high-stakes data terminal in a neon-lit future.

### Core Principles
- **Luminance:** Essential information "glows" against deep, dark backgrounds.
- **Precision:** Clean lines, grid patterns, and technical typography to reflect the accuracy required in predictions.
- **Energy:** High-contrast accents (Neon Pink and Teal) to drive engagement and excitement.

---

## 2. Color Palette

### Primary Backgrounds
- **Deep Space:** `#0a0a12` (Main app background)
- **Terminal Surface:** `#12121f` (Cards, panels, and sidebars)
- **Grid Overlay:** `rgba(255, 255, 255, 0.03)` (Subtle background texture)

### Brand & Accent Colors
- **Cyber Pink (Primary):** `#ff2d78` (Branding, primary CTAs, active states)
- **Neon Teal (Secondary):** `#00ffcc` (Success states, points, secondary highlights)
- **Glitch Purple:** `#7b2ffb` (Special features like "Time Travel" or Bonus)
- **Warning Amber:** `#ffb800` (Lock notices, pending states)

---

## 3. Typography

- **Headings:** `Sora` (Bold/Black) — A geometric sans-serif that feels modern and industrial.
- **Body & Data:** `Space Grotesk` — Highly legible with a technical, monospace-adjacent feel, perfect for numbers and scores.
- **Navigation:** `Space Grotesk` (Uppercase, Tracking: 0.1em).

---

## 4. Component Guidelines

### Match Cards
- **Structure:** Horizontal layout for desktop, vertical for mobile.
- **Interaction:** Inner glow on hover. Prediction inputs should have a subtle border pulse when focused.
- **Status Indicators:** 
    - *Open:* White border.
    - *Locked:* Semi-transparent with a lock icon.
    - *Finished:* Colored border based on win (Teal) or loss (Pink).

### Sidebar Navigation
- **Blur:** `backdrop-blur-md` for a glassmorphism effect.
- **Active State:** A vertical bar of light (Cyber Pink) on the left edge with a subtle drop shadow glow.

### Leaderboard
- **Highlighter:** The top-ranked player should feature a "Grandmaster" gold accent or a unique neon border to signify status.

---

## 5. Interaction Design (UX)
- **Feedback:** Every prediction save should trigger a brief "Data Transmitted" animation or a teal glow pulse on the card.
- **Time Travel UI:** A specialized toggle in the Admin panel that shifts the entire app's accent color to a "Simulated" Purple to warn the admin they are not in real-time.

---

## 6. Icons
- **Style:** Outlined, thin-stroke icons (Material Symbols or Lucide) with a low-opacity glow of the current primary accent color.