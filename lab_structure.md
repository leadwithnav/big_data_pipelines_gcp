# Interactive SPA Lab Structure & Format Specification (`lab_structure.md`)

This document outlines the standard architecture, layout, design tokens, and JavaScript controller logic used in interactive Single Page Application (SPA) training labs (derived from `lab2.html`). Use this template specification across all hands-on technical labs for consistent UX/UI.

---

## 1. Page Layout Architecture

The application uses a **2-column CSS Grid** (`.app-container`) with a fixed-width sidebar and scrollable main content area.

```
+-------------------------------------------------------------------------+
|                              TOP NAVBAR                                 |
+------------------+------------------------------------------------------+
| SIDEBAR          | MAIN CONTENT AREA                                    |
| - Logo & Title   | - Step Title & Subtitle                              |
| - Progress Bar   | - Callout Cards (Info / Warning / Note)              |
| - Step List      | - OS Switcher Tabs (Linux/macOS vs Windows)           |
| - Theme Toggle   | - Code Blocks with Copy Button                       |
|                  | - Task Checklists                                    |
|                  | - Quiz Cards (Assessment Panel)                      |
|                  | - Certificate Canvas (Final Panel)                   |
+------------------+------------------------------------------------------+
|                  | STICKY FOOTER NAV (Previous / Next Step Buttons)     |
+------------------+------------------------------------------------------+
```

---

## 2. Core HTML Component Hierarchy

```html
<!DOCTYPE html>
<html lang="en" data-theme="dark">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Lab Title</title>
  <!-- Google Fonts: Inter / Outfit (UI) & JetBrains Mono / Fira Code (Monospace) -->
  <style>/* CSS Design System Tokens & Classes */</style>
</head>
<body>

  <!-- Top Navbar -->
  <header class="navbar">
    <div class="brand">
      <div class="brand-logo">N</div>
      <div class="brand-title">Lab Title</div>
    </div>
    <div class="nav-actions">
      <div class="progress-bar-container">
        <div class="progress-bar-fill" id="progressBar"></div>
      </div>
      <span id="progressPercent">0%</span>
      <button class="theme-toggle" onclick="toggleTheme()">
        <span id="themeIcon">🌙</span> Theme
      </button>
    </div>
  </header>

  <!-- Main Wrapper Grid -->
  <div class="main-wrapper">

    <!-- Sidebar Navigation -->
    <aside class="sidebar">
      <div class="sidebar-heading">Lab Modules</div>
      <ul class="step-list" id="stepsList">
        <li class="step-item active" onclick="goToStep(0)">
          <span class="step-number">1</span>
          <span class="step-title">Module Title</span>
        </li>
      </ul>
    </aside>

    <!-- Main Content Area -->
    <main class="content-area">

      <!-- STEP PANEL (One for each step: panel-0, panel-1, etc.) -->
      <section class="content-panel active" id="panel-0">
        <h1>Step 1: Module Title</h1>
        <p class="subtitle">Brief explanation of module objectives.</p>

        <!-- Callout Banner -->
        <div class="callout callout-purple">
          <div class="callout-title">💡 Concept Highlight</div>
          <div class="callout-content">Educational text explaining concepts.</div>
        </div>

        <!-- OS Tab Switcher -->
        <div class="os-tab-bar">
          <button class="os-tab-btn active" data-os="linux" onclick="switchOsTab('linux')">🐧 Linux / macOS</button>
          <button class="os-tab-btn" data-os="powershell" onclick="switchOsTab('powershell')">⚡ Windows (PowerShell)</button>
        </div>

        <!-- OS Command Content -->
        <div class="os-content active" data-os="linux">
          <div class="code-block-container sql">
            <div class="code-header">
              <span class="code-lang-badge">Linux Commands</span>
              <button class="copy-btn" onclick="copyCode(this)">Copy</button>
            </div>
            <pre class="code-content"><code># Command snippet here</code></pre>
          </div>
        </div>

        <div class="os-content" data-os="powershell">
          <div class="code-block-container sql">
            <div class="code-header">
              <span class="code-lang-badge">PowerShell Commands</span>
              <button class="copy-btn" onclick="copyCode(this)">Copy</button>
            </div>
            <pre class="code-content"><code># Command snippet here</code></pre>
          </div>
        </div>

        <!-- Interactive Task Checklist -->
        <ul class="task-checklist">
          <li class="task-checkbox-container" data-task-id="t1_1">
            <div class="custom-checkbox">
              <svg class="check-mark" viewBox="0 0 24 24"><path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z"/></svg>
            </div>
            <div class="task-content">
              <span class="task-label">Task Action Title</span>
              <span class="task-desc">Detailed verification instruction.</span>
            </div>
          </li>
        </ul>
      </section>

      <!-- ASSESSMENT PANEL (Penultimate Step) -->
      <section class="content-panel" id="panel-quiz">
        <h1>Knowledge Assessment</h1>
        <div class="quiz-card">
          <div class="quiz-question">1. Technical Question text?</div>
          <div class="quiz-options">
            <div class="quiz-option" data-correct="true">A) Correct Answer Option</div>
            <div class="quiz-option" data-correct="false">B) Incorrect Option</div>
          </div>
        </div>
      </section>

      <!-- CERTIFICATE PANEL (Final Step) -->
      <section class="content-panel" id="panel-cert">
        <h1>Completion Certificate</h1>
        <div class="cert-canvas-container">
          <input type="text" id="studentNameInput" class="cert-input" placeholder="Enter Your Name" oninput="generateCertificate()">
          <canvas id="certCanvas" width="800" height="500"></canvas>
        </div>
      </section>

    </main>

    <!-- Sticky Bottom Navigation Footer -->
    <footer class="nav-bar">
      <button class="btn-nav btn-prev" id="btnPrev" onclick="changeStep(-1)">← Previous</button>
      <button class="btn-nav btn-next" id="btnNext" onclick="changeStep(1)">Next Step →</button>
    </footer>
  </div>

</body>
</html>
```

---

## 3. CSS Design Tokens System

Use CSS variables to support responsive Dark and Light theme modes:

```css
:root {
  --bg-primary: #0f172a;
  --bg-secondary: #1e293b;
  --bg-card: #1e293b;
  --bg-card-hover: #334155;
  --text-primary: #f8fafc;
  --text-secondary: #94a3b8;
  --text-muted: #64748b;
  --accent-purple: #8b5cf6;
  --accent-blue: #3b82f6;
  --accent-green: #10b981;
  --accent-amber: #f59e0b;
  --accent-red: #ef4444;
  --accent-indigo: #6366f1;
  --border-color: #334155;
  --code-bg: #090d16;
  --sidebar-width: 320px;
  --header-height: 70px;
}

[data-theme="light"] {
  --bg-primary: #f8fafc;
  --bg-secondary: #ffffff;
  --bg-card: #ffffff;
  --bg-card-hover: #f1f5f9;
  --text-primary: #0f172a;
  --text-secondary: #475569;
  --text-muted: #94a3b8;
  --accent-purple: #7c3aed;
  --accent-blue: #2563eb;
  --accent-green: #059669;
  --accent-amber: #d97706;
  --accent-red: #dc2626;
  --border-color: #e2e8f0;
  --code-bg: #0f172a;
}
```

---

## 4. Standard JavaScript Controller Functions

Every lab implementation must include the following JavaScript functions:

| Function Name | Description |
| :--- | :--- |
| `goToStep(stepIndex)` | Hides all `.content-panel` elements, removes active states from sidebar steps, displays `#panel-${stepIndex}`, updates `btnPrev` visibility and `btnNext` button text. |
| `changeStep(delta)` | Navigates forward (`+1`) or backward (`-1`) between steps. |
| `switchOsTab(os)` | Toggles command blocks between `linux` and `powershell` OS tabs. |
| `toggleTheme()` | Switches `data-theme` between `dark` and `light`, updates theme icon (`🌙` / `☀️`), and redraws certificate canvas. |
| `setupChecklists()` & `updateProgress()` | Tracks checked task IDs, calculates completion percentage `(completed / total) * 100`, updates sidebar progress bar and percent badge. |
| `setupQuizListeners()` | Attaches click handlers to `.quiz-option` elements, applies `.correct` (green) or `.incorrect` (red) classes based on `data-correct="true|false"`. |
| `copyCode(btn)` | Copies the text inside `pre.code-content` to the clipboard and shows a temporary "Copied!" message. |
| `generateCertificate()` | Renders an HTML5 Canvas certificate with custom student name, completion date, and gold/purple styling. |

---

## 5. Guidelines for Adding New Modules

1. **Sequential Panel IDs**: Ensure step panels follow consecutive zero-indexed IDs (`panel-0`, `panel-1`, `panel-2`, etc.).
2. **Dual-OS Support**: Always provide both Linux/macOS and Windows PowerShell commands in separate `.os-content` blocks.
3. **No Unneeded File Automations**: Write SQL DDL/DML statements directly into HTML code blocks rather than referencing external `.sql` files.
4. **Interactive Checklists**: Include at least 1 checkbox task per module step to drive user progress tracking.
