# WCAG 2.2 AA Accessibility Audit Checklist for UX & Frontend

This checklist synthesizes the essential Web Content Accessibility Guidelines (WCAG) 2.2 Level AA requirements, with specific emphasis on modern web interactions and new 2.2 criteria.

---

## 1. Perceivable (Information Presentation)

### Contrast
- [ ] **1.4.3 Contrast (Minimum) (AA)**:
  - Standard body text & small copy: $\ge 4.5:1$ contrast against background.
  - Large text ($\ge 18\text{pt}$ or $\ge 14\text{pt}$ bold): $\ge 3:1$ contrast.
- [ ] **1.4.11 Non-Text Contrast (AA)**:
  - Form input borders, active toggles, icons conveying meaning, and chart data elements: $\ge 3:1$ against adjacent colors.

### Responsive Scaling & Spacing
- [ ] **1.4.10 Reflow (AA)**: Layout reflows smoothly up to 400% zoom on a 320 CSS px viewport without horizontal scrolling or content clipping.
- [ ] **1.4.12 Text Spacing (AA)**: No loss of content or functionality when text spacing overrides are applied (line-height 1.5x, paragraph spacing 2x, letter-spacing 0.12x, word-spacing 0.16x).

### Hover and Focus Content
- [ ] **1.4.13 Content on Hover or Focus (AA)**:
  - Dismissible: User can dismiss popover/tooltip via `Escape` key without moving pointer.
  - Hoverable: Pointer can move over the popover content without it disappearing.
  - Persistent: Remains visible until trigger removed, dismissed, or invalid.

---

## 2. Operable (User Interaction & Navigation)

### Touch Targets & Pointer Gestures
- [ ] **2.5.8 Target Size (Minimum) (AA) [NEW in WCAG 2.2]**:
  - All interactive pointer targets (buttons, links, icons, form controls) must be at least **$24 \times 24$ CSS pixels**, or have sufficient surrounding spacing so a 24px diameter circle centered on the target does not intersect another target.
  - *Recommendation*: For primary mobile & touch UX, follow standard platform targets of **$44 \times 44$ CSS pixels**.
- [ ] **2.5.7 Dragging Movements (AA) [NEW in WCAG 2.2]**:
  - Any feature operated by dragging (sliders, kanban cards, list reordering, carousels) must provide a **single-pointer alternative** (e.g., arrow buttons, numeric inputs, or "Move up/down" dropdown actions).

### Keyboard Navigation & Focus Visibility
- [ ] **2.1.1 Keyboard Accessible (A)**: Every feature, modal, dropdown, and tab must be operable via keyboard (`Tab`, `Shift+Tab`, `Enter`, `Space`, Arrows, `Esc`).
- [ ] **2.1.2 No Keyboard Trap (A)**: Modals must trap focus while open, but always allow exit via `Escape` or a focused close button, returning focus to the trigger.
- [ ] **2.4.7 Focus Visible (AA)**: Every interactive element must display a prominent, high-contrast visual focus ring (`focus-visible:ring-2 focus-visible:ring-primary`).
- [ ] **2.4.11 Focus Not Obscured (Minimum) (AA) [NEW in WCAG 2.2]**:
  - When an element receives keyboard focus, it must **never be entirely obscured** by sticky headers, fixed footers, or floating notifications.
  - Implementation requirement: Ensure scrollable containers declare `scroll-padding-top` / `scroll-padding-bottom` matching sticky elements.

---

## 3. Understandable (Predictability & Error Handling)

### Consistency & Help
- [ ] **3.2.6 Findable Help (A) [NEW in WCAG 2.2]**:
  - Support, help links, or chat mechanisms must be placed in a consistent relative location across views (e.g., top header or persistent sidebar).
- [ ] **3.3.7 Redundant Entry (A) [NEW in WCAG 2.2]**:
  - Avoid forcing users to enter the same information twice in the same multi-step flow (e.g., auto-populate billing from shipping; retain multi-step form state).

### Authentication & Cognitive Load
- [ ] **3.3.8 Accessible Authentication (Minimum) (AA) [NEW in WCAG 2.2]**:
  - Do not rely solely on cognitive tests (memorized passwords without paste support, transcribing CAPTCHAs).
  - Native password manager autofill, clipboard pasting, and WebAuthn / Passkeys must be supported.

### Forms & Error Prevention
- [ ] **3.3.1 Error Identification (A)**: Form validation errors must be clearly announced and visually tied to the input via `aria-describedby` and `aria-invalid="true"`.
- [ ] **3.3.3 Error Suggestion (AA)**: Error messages must explain *how* to correct the error, not just state that it failed.

---

## 4. Robust (Semantics & Assistive Tech)

- [ ] **4.1.2 Name, Role, Value (A)**:
  - Custom buttons have `role="button"` or use native `<button>`.
  - Icon-only buttons have explicit `aria-label="Action description"`.
  - Expandable items (drawers, accordions, dropdowns) specify `aria-expanded="true|false"` and `aria-controls="id"`.

