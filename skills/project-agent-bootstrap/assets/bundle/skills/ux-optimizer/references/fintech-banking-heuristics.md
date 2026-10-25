# FinTech & Banking UX Heuristics & Calibrated Friction Guide

In financial technology, **trust is the product**. The stakes involve real money, privacy, and user security. Designing financial UX requires balancing fluid speed with protective safety.

---

## 1. The Principle of Calibrated Friction

Standard UX dogma says "minimize all friction". In financial applications, this is dangerously incomplete. We must distinguish between **Nuisance Friction** and **Protective Friction**.

### Eliminate Nuisance Friction (Speed & Comfort)
- **Automatic Formatting**: Automatically format card numbers (`#### #### #### ####`), currency inputs, IBANs, and phone numbers with spacing while typing.
- **Smart Defaults**: Pre-select the user's primary checking account, default to recent payees, auto-detect transfer type (SEPA, Instant, Wire).
- **One/Two-Click Access**: Critical daily tasks (balance check, transaction history, statement download) should never be buried more than 2 clicks deep.
- **Data Persistence**: If a session times out or a multi-step transfer fails validation, preserve all valid user inputs rather than wiping the form.

### Introduce Protective Friction (Psychological Safety & Reversibility)
- **High-Stakes Gateways**: High-value transfers, new beneficiary additions, card freezes/unfreezes, and security credential changes must require an explicit confirmation step.
- **Summary Preview Card**: Before initiating an irreversible transaction, present an explicit confirmation card displaying:
  - Exact debit amount & receiving currency.
  - Recipient full name & IBAN/Account identifier.
  - Transfer fees (if any) and expected delivery window.
  - Source account and remaining balance *after* the operation.
- **Reversible Grace Period / Undo Window**: Where possible, provide a 5-10 second "Undo / Cancel transfer" banner immediately after execution.

---

## 2. Visual Precision & Data Density

Financial users demand clarity, rigor, and density over generic decorative fluff:

### Numbers & Tabular Alignment
- **Tabular Figures**: Always format financial numbers with monospace figures (`font-mono` or `font-feature-settings: 'tnum'`). This prevents numbers from shifting horizontally when updating and ensures decimal points align perfectly in tables.
- **Explicit Balance Distinction**: Clearly differentiate between:
  - *Available Balance* (immediately spendable).
  - *Current / Ledger Balance* (including pending authorizations).
- **Status Badges**: Every transaction row must have an explicit status badge:
  - `Completed / Settled` (emerald / green).
  - `Pending / Processing` (amber / yellow).
  - `Failed / Declined` (rose / red).
  - `Scheduled` (sky / blue).

---

## 3. Micro-Interactions & State Transparency

### < 100ms Feedback Loop
- **Instant Click Reaction**: When a user clicks a button (e.g., "Confirm Transfer"), morph the CTA into an active processing state with a spinner or progress bar. Never leave a button in an ambiguous static state.
- **Multi-Stage Processing**: For operations taking > 1.5 seconds, show a multi-step indicator:
  `Initiated ➔ Verifying Security ➔ Transmitting Funds ➔ Completed`.

### Error Recovery Over Cryptic Codes
- Never display raw backend exceptions (e.g. `PrismaClientKnownRequestError` or `HTTP 500`).
- Display human, actionable guidance:
  - *What happened*: "Your transfer of €250 could not be completed."
  - *Why*: "The amount exceeds your current available daily limit of €200."
  - *Action*: "Adjust transfer amount" or "Manage daily limits".

