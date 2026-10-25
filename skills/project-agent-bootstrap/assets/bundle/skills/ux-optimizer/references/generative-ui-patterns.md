# Generative UI Architecture & Interactive Prototyping Patterns

Generative UI bridges user intent with dynamic, contextually generated interfaces. Within Google Antigravity, Generative UI allows agents to produce rich, interactive HTML widgets that render directly inline in chat or as standalone side-pane artifacts.

---

## 1. Antigravity Generative UI Standards

### Core Environment Constraints
- **Tailwind Dependency**: Use the allowlisted gstatic Tailwind build:
  ```html
  <script src="https://www.gstatic.com/antigravity/web/dev/tailwindcss.min.js"></script>
  ```
- **Semantic Theme Variables**: The host application injects CSS design tokens into the iframe. Always use theme variables so widgets dynamically honor light/dark modes and user palette preferences:
  - Surfaces: `bg-[var(--card)]`, `bg-[var(--background)]`, `bg-[var(--sidebar)]`
  - Text: `text-[var(--foreground)]`, `text-[var(--muted-foreground)]`, `text-[var(--placeholder)]`
  - Borders: `border-[var(--border)]`
  - Accents: `bg-[var(--primary)]`, `text-[var(--primary-foreground)]`, `bg-[var(--accent)]`, `bg-[var(--secondary)]`
- **Typography Floor**: Never use font sizes below `12px` (`text-xs`). Do not hardcode custom `font-size: 10px` or `text-[10px]`.
- **Inline Embed Syntax**:
  ```html
  <agent-embed src="file:///<artifact_path>/widget.html"></agent-embed>
  ```
  For inline embedding, always configure `<body class="bg-transparent text-[var(--foreground)] antialiased p-5">` so the outer container matches the chat stream.

---

## 2. Generative UI Design Patterns

### Pattern A: Before / After Interactive Comparison Slider / Tabs
When proposing a UX overhaul, provide an interactive Generative UI widget allowing the user to toggle between:
1. **Current State**: Visualizing existing pain points, cramped inputs, or low contrast.
2. **Optimized State**: Demonstrating modern spacing, WCAG 2.2 touch targets, clear status badges, and calibrated friction.

### Pattern B: Intent Scaffolding & Stateful Micro-Interactions
- Use animated skeleton shimmers (`animate-pulse bg-[var(--muted)]`) while data or AI reasoning is processing.
- Provide interactive controls (sliders, toggles, filters) that update simulated calculations in real time.
- Include feedback and escape hatches: "Reset to default", "Copy code", "Apply changes".

### Pattern C: Progressive Disclosure Drawer / Accordion
- Display the essential primary summary at the top level.
- Provide collapsible drawers (`details` / `summary` or interactive JS tabs) for technical breakdowns, audit logs, or advanced configuration options.

---

## 3. Boilerplate Template for Generative UI Artifacts

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>UX Prototype</title>
  <script src="https://www.gstatic.com/antigravity/web/dev/tailwindcss.min.js"></script>
</head>
<body class="bg-transparent text-[var(--foreground)] antialiased p-4">
  <div class="bg-[var(--card)] text-[var(--foreground)] border border-[var(--border)] rounded-2xl p-6 shadow-sm max-w-2xl mx-auto space-y-4">
    <!-- Header -->
    <div class="flex items-center justify-between border-b border-[var(--border)] pb-4">
      <div>
        <h3 class="text-base font-semibold text-[var(--foreground)]">UX Prototype: [Feature Name]</h3>
        <p class="text-xs text-[var(--muted-foreground)]">WCAG 2.2 AA Compliant • Calibrated Friction • Modern Micro-interactions</p>
      </div>
      <span class="px-2.5 py-1 text-xs rounded-full font-medium bg-[var(--primary)] text-[var(--primary-foreground)]">
        Interactive Preview
      </span>
    </div>

    <!-- Interactive Component Simulation -->
    <div class="space-y-3 pt-2">
      <!-- Content goes here -->
    </div>
  </div>
</body>
</html>
```

