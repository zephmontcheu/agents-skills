---
name: ui-ux-testing
description: >-
  Use this skill when you make changes to the UI/UX. It provides instructions on how to use browser tools to verify layout, responsiveness, interactivity, accessibility, and console errors.
---

# UI/UX Testing Procedures

Whenever you make changes to UI or UX code, you MUST rigorously test those changes in a browser environment to ensure they work as intended. 

## Pre-requisites

Ensure that the local development server is running; if it isn't, start it with the project's dev command (see `AGENTS.md`). Read its URL from the dev command output (common defaults: Vite `http://localhost:5173`, Next.js `http://localhost:3000`).

## Testing Checklist

Use whatever browser tools your agent has (Playwright MCP, Chrome DevTools MCP, a built-in browser) to perform the following checks on the modified pages:

1. **Console Errors**: Check the browser's developer console. There must be no new errors or warnings caused by your changes.
2. **Visual Layout and Rendering**: Visually inspect the page. Ensure elements do not overlap, text is readable, and the layout conforms to the expected design or prior state.
3. **Interactivity**: Actively test the functionality of the components you modified. Click buttons, fill out forms, and trigger states to ensure the UI behaves as expected.
4. **Responsiveness**: Resize the viewport or emulate different devices (mobile, tablet, desktop) to ensure the UI remains usable and aesthetically pleasing across screen sizes.
5. **Accessibility**: Verify that your changes maintain accessibility standards. Check for adequate color contrast, proper ARIA attributes, and ensure the new elements can be navigated via keyboard.

## Action on Failure

If any of the above checks fail, you must fix the underlying issue in the code, and then repeat this testing process from the beginning. You cannot consider a UI/UX task complete until all these tests pass successfully in the browser.

