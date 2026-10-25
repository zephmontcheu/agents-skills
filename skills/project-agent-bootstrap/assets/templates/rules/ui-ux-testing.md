---
trigger: always_on
---

# UI/UX Testing Rule

After any task that changes the user interface, run the `ui-ux-testing` skill before calling the task done or asking the user for review.

It applies when your work touches files in {{FRONTEND_DIRS}}, components, pages, or layouts, CSS or utility classes, user flows, interactive elements (buttons, forms, modals), or animations.

The skill checks the change in a real browser: console errors, layout, interactivity, responsiveness, and accessibility. Fix what fails and run it again.
