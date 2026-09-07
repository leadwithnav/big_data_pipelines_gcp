import os
import json

def get_template(lab_id, lab_badge, lab_title, modules, quiz_questions):
    """
    modules: list of dicts:
      {
        'title': str,
        'subtitle': str,
        'callout': {'type': 'purple|blue|amber|green|red', 'title': str, 'content': str},
        'explanation': str,
        'code_lang': str, # e.g. 'bash', 'python', 'sql'
        'linux_cmd': str,
        'pwsh_cmd': str,
        'tasks': [ {'label': str, 'desc': str}, ... ]
      }
    quiz_questions: list of dicts:
      {
        'question': str,
        'options': [ {'text': str, 'correct': bool}, ... ]
      }
    """
    total_panels = len(modules) + 2 # modules + quiz + cert
    
    # Build Sidebar Steps
    sidebar_items_html = ""
    for idx, mod in enumerate(modules):
        active_cls = "active" if idx == 0 else ""
        sidebar_items_html += f"""
        <li class="step-item {active_cls}" onclick="goToStep({idx})">
          <span class="step-number">{idx + 1}</span>
          <span class="step-title">{mod['title']}</span>
        </li>"""
    
    # Quiz Step in Sidebar
    quiz_idx = len(modules)
    sidebar_items_html += f"""
        <li class="step-item" onclick="goToStep({quiz_idx})">
          <span class="step-number">?</span>
          <span class="step-title">Knowledge Assessment</span>
        </li>"""
        
    # Cert Step in Sidebar
    cert_idx = len(modules) + 1
    sidebar_items_html += f"""
        <li class="step-item" onclick="goToStep({cert_idx})">
          <span class="step-number">★</span>
          <span class="step-title">Certificate</span>
        </li>"""

    # Build Content Panels for Modules
    panels_html = ""
    for idx, mod in enumerate(modules):
        active_cls = "active" if idx == 0 else ""
        
        callout_html = ""
        if mod.get('callout'):
            c = mod['callout']
            callout_html = f"""
        <div class="callout callout-{c.get('type', 'purple')}">
          <div class="callout-title">{c.get('title', '💡 Concept Highlight')}</div>
          <div class="callout-content">{c.get('content', '')}</div>
        </div>"""

        code_lang = mod.get('code_lang', 'bash').upper()
        
        # Build tasks
        tasks_html = ""
        if mod.get('tasks'):
            tasks_html += '<ul class="task-checklist">\n'
            for t_idx, t in enumerate(mod['tasks']):
                task_id = f"t{idx+1}_{t_idx+1}"
                tasks_html += f"""          <li class="task-checkbox-container" data-task-id="{task_id}">
            <div class="custom-checkbox">
              <svg class="check-mark" viewBox="0 0 24 24"><path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z"/></svg>
            </div>
            <div class="task-content">
              <span class="task-label">{t['label']}</span>
              <span class="task-desc">{t['desc']}</span>
            </div>
          </li>\n"""
            tasks_html += '        </ul>\n'

        panels_html += f"""
      <!-- STEP PANEL {idx} -->
      <section class="content-panel {active_cls}" id="panel-{idx}">
        <h1>Step {idx + 1}: {mod['title']}</h1>
        <p class="subtitle">{mod['subtitle']}</p>
        {callout_html}
        <p>{mod.get('explanation', '')}</p>

        <!-- OS Tab Switcher -->
        <div class="os-tab-bar">
          <button class="os-tab-btn active" data-os="linux" onclick="switchOsTab('linux')">🐧 Linux / macOS</button>
          <button class="os-tab-btn" data-os="powershell" onclick="switchOsTab('powershell')">⚡ Windows (PowerShell)</button>
        </div>

        <!-- OS Command Content: Linux -->
        <div class="os-content active" data-os="linux">
          <div class="code-block-container">
            <div class="code-header">
              <span class="code-lang-badge">Linux / macOS ({code_lang})</span>
              <button class="copy-btn" onclick="copyCode(this)">Copy</button>
            </div>
            <pre class="code-content"><code>{mod.get('linux_cmd', '')}</code></pre>
          </div>
        </div>

        <!-- OS Command Content: PowerShell -->
        <div class="os-content" data-os="powershell">
          <div class="code-block-container">
            <div class="code-header">
              <span class="code-lang-badge">PowerShell ({code_lang})</span>
              <button class="copy-btn" onclick="copyCode(this)">Copy</button>
            </div>
            <pre class="code-content"><code>{mod.get('pwsh_cmd', '')}</code></pre>
          </div>
        </div>

        {tasks_html}
      </section>"""

    # Build Quiz Panel
    quiz_cards_html = ""
    for q_idx, q in enumerate(quiz_questions):
        opts_html = ""
        for opt in q['options']:
            corr_str = "true" if opt.get('correct') else "false"
            opts_html += f"""            <div class="quiz-option" data-correct="{corr_str}">{opt['text']}</div>\n"""
            
        quiz_cards_html += f"""
        <div class="quiz-card">
          <div class="quiz-question">{q_idx + 1}. {q['question']}</div>
          <div class="quiz-options">
{opts_html}          </div>
        </div>"""

    quiz_panel_html = f"""
      <!-- ASSESSMENT PANEL -->
      <section class="content-panel" id="panel-{quiz_idx}">
        <h1>Knowledge Assessment</h1>
        <p class="subtitle">Test your understanding of the concepts covered in this lab.</p>
        {quiz_cards_html}
      </section>"""

    # Build Cert Panel
    cert_panel_html = f"""
      <!-- CERTIFICATE PANEL -->
      <section class="content-panel" id="panel-{cert_idx}">
        <h1>Completion Certificate</h1>
        <p class="subtitle">Enter your name below to generate your official verification certificate.</p>
        <div class="cert-canvas-container">
          <input type="text" id="studentNameInput" class="cert-input" placeholder="Enter Your Full Name" oninput="generateCertificate()">
          <canvas id="certCanvas" width="800" height="500"></canvas>
          <button class="btn-nav" style="margin-top:15px; width:auto; padding: 10px 20px;" onclick="downloadCertificate()">📥 Download Certificate</button>
        </div>
      </section>"""

    html_content = f"""<!DOCTYPE html>
<html lang="en" data-theme="dark">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{lab_title}</title>
  <!-- Google Fonts: Inter & JetBrains Mono -->
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
  <style>
    :root {{
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
    }}

    [data-theme="light"] {{
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
    }}

    * {{
      box-sizing: border-box;
      margin: 0;
      padding: 0;
    }}

    body {{
      font-family: 'Inter', system-ui, -apple-system, sans-serif;
      background-color: var(--bg-primary);
      color: var(--text-primary);
      height: 100vh;
      display: flex;
      flex-direction: column;
      overflow: hidden;
      line-height: 1.6;
    }}

    /* Top Navbar */
    .navbar {{
      height: var(--header-height);
      background-color: var(--bg-secondary);
      border-bottom: 1px solid var(--border-color);
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 0 24px;
      z-index: 10;
    }}

    .brand {{
      display: flex;
      align-items: center;
      gap: 12px;
    }}

    .brand-logo {{
      width: 36px;
      height: 36px;
      background: linear-gradient(135deg, var(--accent-purple), var(--accent-blue));
      border-radius: 8px;
      display: flex;
      align-items: center;
      justify-content: center;
      font-weight: 700;
      color: #fff;
      font-size: 15px;
    }}

    .brand-title {{
      font-size: 18px;
      font-weight: 600;
      color: var(--text-primary);
    }}

    .nav-actions {{
      display: flex;
      align-items: center;
      gap: 16px;
    }}

    .progress-bar-container {{
      width: 180px;
      height: 8px;
      background-color: var(--bg-primary);
      border-radius: 4px;
      overflow: hidden;
      border: 1px solid var(--border-color);
    }}

    .progress-bar-fill {{
      height: 100%;
      width: 0%;
      background: linear-gradient(90deg, var(--accent-purple), var(--accent-blue));
      transition: width 0.3s ease;
    }}

    #progressPercent {{
      font-size: 14px;
      font-weight: 600;
      color: var(--accent-purple);
      min-width: 40px;
    }}

    .theme-toggle {{
      background-color: var(--bg-primary);
      border: 1px solid var(--border-color);
      color: var(--text-primary);
      padding: 8px 14px;
      border-radius: 6px;
      cursor: pointer;
      font-size: 14px;
      display: flex;
      align-items: center;
      gap: 6px;
      transition: all 0.2s;
    }}

    .theme-toggle:hover {{
      background-color: var(--bg-card-hover);
    }}

    /* Main Layout */
    .main-wrapper {{
      display: grid;
      grid-template-columns: var(--sidebar-width) 1fr;
      height: calc(100vh - var(--header-height));
      position: relative;
    }}

    /* Sidebar Navigation */
    .sidebar {{
      background-color: var(--bg-secondary);
      border-right: 1px solid var(--border-color);
      padding: 20px 0;
      overflow-y: auto;
      display: flex;
      flex-direction: column;
    }}

    .sidebar-heading {{
      font-size: 12px;
      text-transform: uppercase;
      letter-spacing: 1px;
      color: var(--text-muted);
      padding: 0 20px 12px 20px;
      font-weight: 600;
    }}

    .step-list {{
      list-style: none;
    }}

    .step-item {{
      display: flex;
      align-items: center;
      gap: 12px;
      padding: 12px 20px;
      cursor: pointer;
      transition: background 0.2s;
      border-left: 3px solid transparent;
    }}

    .step-item:hover {{
      background-color: var(--bg-card-hover);
    }}

    .step-item.active {{
      background-color: var(--bg-card-hover);
      border-left-color: var(--accent-purple);
    }}

    .step-item.completed .step-number {{
      background-color: var(--accent-green);
      color: #fff;
      border-color: var(--accent-green);
    }}

    .step-number {{
      width: 26px;
      height: 26px;
      border-radius: 50%;
      background-color: var(--bg-primary);
      border: 1px solid var(--border-color);
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 12px;
      font-weight: 600;
      color: var(--text-secondary);
      flex-shrink: 0;
    }}

    .step-title {{
      font-size: 14px;
      color: var(--text-secondary);
      font-weight: 500;
    }}

    .step-item.active .step-title {{
      color: var(--text-primary);
      font-weight: 600;
    }}

    /* Main Content Area */
    .content-area {{
      padding: 32px 40px 100px 40px;
      overflow-y: auto;
    }}

    .content-panel {{
      display: none;
      max-width: 900px;
      margin: 0 auto;
    }}

    .content-panel.active {{
      display: block;
    }}

    h1 {{
      font-size: 28px;
      font-weight: 700;
      margin-bottom: 8px;
      color: var(--text-primary);
    }}

    .subtitle {{
      font-size: 16px;
      color: var(--text-secondary);
      margin-bottom: 24px;
    }}

    h2 {{
      font-size: 20px;
      font-weight: 600;
      margin: 24px 0 12px 0;
      color: var(--text-primary);
    }}

    p {{
      margin-bottom: 16px;
      color: var(--text-secondary);
    }}

    /* Callout Cards */
    .callout {{
      padding: 16px 20px;
      border-radius: 8px;
      margin-bottom: 24px;
      border-left: 4px solid var(--accent-purple);
      background-color: var(--bg-secondary);
    }}

    .callout-purple {{ border-left-color: var(--accent-purple); }}
    .callout-blue {{ border-left-color: var(--accent-blue); }}
    .callout-amber {{ border-left-color: var(--accent-amber); }}
    .callout-green {{ border-left-color: var(--accent-green); }}
    .callout-red {{ border-left-color: var(--accent-red); }}

    .callout-title {{
      font-weight: 600;
      font-size: 15px;
      margin-bottom: 6px;
      color: var(--text-primary);
    }}

    .callout-content {{
      font-size: 14px;
      color: var(--text-secondary);
    }}

    /* OS Tab Switcher */
    .os-tab-bar {{
      display: flex;
      gap: 8px;
      margin-bottom: 12px;
      border-bottom: 1px solid var(--border-color);
      padding-bottom: 8px;
    }}

    .os-tab-btn {{
      background: none;
      border: none;
      color: var(--text-secondary);
      padding: 6px 14px;
      font-size: 14px;
      font-weight: 500;
      cursor: pointer;
      border-radius: 6px;
      transition: all 0.2s;
    }}

    .os-tab-btn:hover {{
      background-color: var(--bg-card-hover);
      color: var(--text-primary);
    }}

    .os-tab-btn.active {{
      background-color: var(--accent-purple);
      color: #fff;
    }}

    .os-content {{
      display: none;
    }}

    .os-content.active {{
      display: block;
    }}

    /* Code Block Containers */
    .code-block-container {{
      background-color: var(--code-bg);
      border: 1px solid var(--border-color);
      border-radius: 8px;
      overflow: hidden;
      margin-bottom: 24px;
    }}

    .code-header {{
      background-color: var(--bg-secondary);
      padding: 8px 16px;
      display: flex;
      justify-content: space-between;
      align-items: center;
      border-bottom: 1px solid var(--border-color);
    }}

    .code-lang-badge {{
      font-size: 12px;
      font-weight: 600;
      text-transform: uppercase;
      color: var(--text-muted);
    }}

    .copy-btn {{
      background-color: var(--bg-primary);
      border: 1px solid var(--border-color);
      color: var(--text-secondary);
      padding: 4px 10px;
      font-size: 12px;
      border-radius: 4px;
      cursor: pointer;
      transition: all 0.2s;
    }}

    .copy-btn:hover {{
      background-color: var(--bg-card-hover);
      color: var(--text-primary);
    }}

    pre.code-content {{
      padding: 16px;
      overflow-x: auto;
      font-family: 'JetBrains Mono', Consolas, monospace;
      font-size: 13px;
      color: #e2e8f0;
      line-height: 1.5;
    }}

    code {{
      font-family: 'JetBrains Mono', Consolas, monospace;
    }}

    /* Task Checklist */
    .task-checklist {{
      list-style: none;
      margin: 24px 0;
    }}

    .task-checkbox-container {{
      display: flex;
      align-items: flex-start;
      gap: 14px;
      background-color: var(--bg-secondary);
      border: 1px solid var(--border-color);
      border-radius: 8px;
      padding: 14px 18px;
      margin-bottom: 12px;
      cursor: pointer;
      transition: border-color 0.2s;
    }}

    .task-checkbox-container:hover {{
      border-color: var(--accent-purple);
    }}

    .task-checkbox-container.completed {{
      border-color: var(--accent-green);
      background-color: rgba(16, 185, 129, 0.05);
    }}

    .custom-checkbox {{
      width: 20px;
      height: 20px;
      border-radius: 4px;
      border: 2px solid var(--text-muted);
      display: flex;
      align-items: center;
      justify-content: center;
      margin-top: 2px;
      flex-shrink: 0;
      transition: all 0.2s;
    }}

    .task-checkbox-container.completed .custom-checkbox {{
      background-color: var(--accent-green);
      border-color: var(--accent-green);
    }}

    .check-mark {{
      width: 14px;
      height: 14px;
      fill: #fff;
      display: none;
    }}

    .task-checkbox-container.completed .check-mark {{
      display: block;
    }}

    .task-content {{
      display: flex;
      flex-direction: column;
    }}

    .task-label {{
      font-weight: 600;
      font-size: 15px;
      color: var(--text-primary);
    }}

    .task-desc {{
      font-size: 13px;
      color: var(--text-secondary);
    }}

    /* Quiz Cards */
    .quiz-card {{
      background-color: var(--bg-secondary);
      border: 1px solid var(--border-color);
      border-radius: 10px;
      padding: 20px;
      margin-bottom: 20px;
    }}

    .quiz-question {{
      font-size: 16px;
      font-weight: 600;
      margin-bottom: 14px;
      color: var(--text-primary);
    }}

    .quiz-options {{
      display: flex;
      flex-direction: column;
      gap: 10px;
    }}

    .quiz-option {{
      background-color: var(--bg-primary);
      border: 1px solid var(--border-color);
      padding: 12px 16px;
      border-radius: 6px;
      cursor: pointer;
      font-size: 14px;
      color: var(--text-secondary);
      transition: all 0.2s;
    }}

    .quiz-option:hover {{
      border-color: var(--accent-purple);
      color: var(--text-primary);
    }}

    .quiz-option.selected.correct {{
      background-color: rgba(16, 185, 129, 0.15);
      border-color: var(--accent-green);
      color: var(--accent-green);
      font-weight: 600;
    }}

    .quiz-option.selected.incorrect {{
      background-color: rgba(239, 68, 68, 0.15);
      border-color: var(--accent-red);
      color: var(--accent-red);
      font-weight: 600;
    }}

    /* Certificate Panel */
    .cert-canvas-container {{
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: 20px;
      background-color: var(--bg-secondary);
      border: 1px solid var(--border-color);
      border-radius: 12px;
      padding: 30px;
      margin-top: 20px;
    }}

    .cert-input {{
      width: 100%;
      max-width: 400px;
      padding: 12px 16px;
      font-size: 16px;
      border-radius: 6px;
      border: 1px solid var(--border-color);
      background-color: var(--bg-primary);
      color: var(--text-primary);
      outline: none;
    }}

    .cert-input:focus {{
      border-color: var(--accent-purple);
    }}

    #certCanvas {{
      border-radius: 8px;
      box-shadow: 0 10px 25px rgba(0, 0, 0, 0.3);
      max-width: 100%;
      height: auto;
    }}

    /* Sticky Bottom Footer Navigation */
    .nav-bar {{
      position: absolute;
      bottom: 0;
      right: 0;
      width: calc(100% - var(--sidebar-width));
      height: 64px;
      background-color: var(--bg-secondary);
      border-top: 1px solid var(--border-color);
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 0 40px;
      z-index: 5;
    }}

    .btn-nav {{
      background: linear-gradient(135deg, var(--accent-purple), var(--accent-blue));
      border: none;
      color: #fff;
      padding: 10px 20px;
      border-radius: 6px;
      font-size: 14px;
      font-weight: 600;
      cursor: pointer;
      transition: opacity 0.2s;
    }}

    .btn-nav:hover {{
      opacity: 0.9;
    }}

    .btn-nav:disabled {{
      opacity: 0.4;
      cursor: not-allowed;
    }}

    .btn-prev {{
      background: var(--bg-primary);
      border: 1px solid var(--border-color);
      color: var(--text-primary);
    }}
  </style>
</head>
<body>

  <!-- Top Navbar -->
  <header class="navbar">
    <div class="brand">
      <div class="brand-logo">{lab_badge}</div>
      <div class="brand-title">{lab_title}</div>
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
{sidebar_items_html}
      </ul>
    </aside>

    <!-- Main Content Area -->
    <main class="content-area">
{panels_html}
{quiz_panel_html}
{cert_panel_html}
    </main>

    <!-- Sticky Bottom Navigation Footer -->
    <footer class="nav-bar">
      <button class="btn-nav btn-prev" id="btnPrev" onclick="changeStep(-1)">← Previous</button>
      <button class="btn-nav btn-next" id="btnNext" onclick="changeStep(1)">Next Step →</button>
    </footer>

  </div>

  <!-- JavaScript Controller Logic -->
  <script>
    const LAB_TITLE_STRING = {json.dumps(lab_title)};
    const LAB_FILE_NAME = {json.dumps(lab_id)};
    const TOTAL_PANELS = {total_panels};
    let currentStep = 0;

    function goToStep(stepIndex) {{
      if (stepIndex < 0 || stepIndex >= TOTAL_PANELS) return;
      currentStep = stepIndex;

      const panels = document.querySelectorAll('.content-panel');
      panels.forEach((p, idx) => {{
        p.classList.toggle('active', idx === stepIndex);
      }});

      const stepItems = document.querySelectorAll('.step-item');
      stepItems.forEach((item, idx) => {{
        item.classList.toggle('active', idx === stepIndex);
      }});

      const btnPrev = document.getElementById('btnPrev');
      const btnNext = document.getElementById('btnNext');

      if (btnPrev) btnPrev.disabled = (stepIndex === 0);

      if (btnNext) {{
        if (stepIndex === TOTAL_PANELS - 1) {{
          btnNext.innerText = 'Completed 🎉';
          btnNext.disabled = true;
        }} else if (stepIndex === TOTAL_PANELS - 2) {{
          btnNext.innerText = 'View Certificate →';
          btnNext.disabled = false;
        }} else if (stepIndex === TOTAL_PANELS - 3) {{
          btnNext.innerText = 'Take Quiz →';
          btnNext.disabled = false;
        }} else {{
          btnNext.innerText = 'Next Step →';
          btnNext.disabled = false;
        }}
      }}

      const contentArea = document.querySelector('.content-area');
      if (contentArea) contentArea.scrollTop = 0;

      if (stepIndex === TOTAL_PANELS - 1) {{
        generateCertificate();
      }}
    }}

    function changeStep(delta) {{
      goToStep(currentStep + delta);
    }}

    function switchOsTab(os) {{
      const btns = document.querySelectorAll('.os-tab-btn');
      btns.forEach(b => {{
        b.classList.toggle('active', b.getAttribute('data-os') === os);
      }});
      const contents = document.querySelectorAll('.os-content');
      contents.forEach(c => {{
        c.classList.toggle('active', c.getAttribute('data-os') === os);
      }});
    }}

    function toggleTheme() {{
      const html = document.documentElement;
      const currentTheme = html.getAttribute('data-theme') || 'dark';
      const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
      html.setAttribute('data-theme', newTheme);
      const icon = document.getElementById('themeIcon');
      if (icon) icon.innerText = newTheme === 'dark' ? '🌙' : '☀️';

      if (currentStep === TOTAL_PANELS - 1) {{
        generateCertificate();
      }}
    }}

    function setupChecklists() {{
      const checklistItems = document.querySelectorAll('.task-checkbox-container');
      checklistItems.forEach(item => {{
        item.addEventListener('click', () => {{
          item.classList.toggle('completed');
          updateProgress();
        }});
      }});
      updateProgress();
    }}

    function updateProgress() {{
      const total = document.querySelectorAll('.task-checkbox-container').length;
      const completed = document.querySelectorAll('.task-checkbox-container.completed').length;
      const percent = total > 0 ? Math.round((completed / total) * 100) : 0;

      const bar = document.getElementById('progressBar');
      const badge = document.getElementById('progressPercent');
      if (bar) bar.style.width = percent + '%';
      if (badge) badge.innerText = percent + '%';

      const panels = document.querySelectorAll('.content-panel');
      panels.forEach((panel, idx) => {{
        const tasksInPanel = panel.querySelectorAll('.task-checkbox-container');
        if (tasksInPanel.length > 0) {{
          const doneInPanel = panel.querySelectorAll('.task-checkbox-container.completed');
          const stepItem = document.querySelectorAll('.step-item')[idx];
          if (stepItem) {{
            stepItem.classList.toggle('completed', tasksInPanel.length === doneInPanel.length);
          }}
        }}
      }});
    }}

    function setupQuizListeners() {{
      const quizCards = document.querySelectorAll('.quiz-card');
      quizCards.forEach(card => {{
        const options = card.querySelectorAll('.quiz-option');
        options.forEach(opt => {{
          opt.addEventListener('click', () => {{
            options.forEach(o => o.classList.remove('selected', 'correct', 'incorrect'));
            opt.classList.add('selected');
            const isCorrect = opt.getAttribute('data-correct') === 'true';
            if (isCorrect) {{
              opt.classList.add('correct');
            }} else {{
              opt.classList.add('incorrect');
              options.forEach(o => {{
                if (o.getAttribute('data-correct') === 'true') o.classList.add('correct');
              }});
            }}
          }});
        }});
      }});
    }}

    function copyCode(btn) {{
      const container = btn.closest('.code-block-container');
      const code = container.querySelector('pre.code-content').innerText;
      navigator.clipboard.writeText(code).then(() => {{
        const orig = btn.innerText;
        btn.innerText = 'Copied!';
        setTimeout(() => btn.innerText = orig, 2000);
      }});
    }}

    function generateCertificate() {{
      const canvas = document.getElementById('certCanvas');
      if (!canvas) return;
      const ctx = canvas.getContext('2d');
      const name = document.getElementById('studentNameInput').value.trim() || 'Learner Name';
      const isLight = document.documentElement.getAttribute('data-theme') === 'light';

      ctx.fillStyle = isLight ? '#ffffff' : '#0f172a';
      ctx.fillRect(0, 0, canvas.width, canvas.height);

      ctx.strokeStyle = '#8b5cf6';
      ctx.lineWidth = 8;
      ctx.strokeRect(15, 15, canvas.width - 30, canvas.height - 30);

      ctx.strokeStyle = '#f59e0b';
      ctx.lineWidth = 2;
      ctx.strokeRect(25, 25, canvas.width - 50, canvas.height - 50);

      ctx.fillStyle = isLight ? '#0f172a' : '#f8fafc';
      ctx.font = 'bold 28px Inter, sans-serif';
      ctx.textAlign = 'center';
      ctx.fillText('CERTIFICATE OF COMPLETION', canvas.width / 2, 90);

      ctx.fillStyle = '#8b5cf6';
      ctx.font = '600 16px Inter, sans-serif';
      ctx.fillText('THIS IS PROUDLY PRESENTED TO', canvas.width / 2, 130);

      ctx.fillStyle = '#f59e0b';
      ctx.font = 'bold 32px Inter, sans-serif';
      ctx.fillText(name, canvas.width / 2, 195);

      ctx.strokeStyle = isLight ? '#e2e8f0' : '#334155';
      ctx.lineWidth = 1;
      ctx.beginPath();
      ctx.moveTo(canvas.width / 2 - 150, 215);
      ctx.lineTo(canvas.width / 2 + 150, 215);
      ctx.stroke();

      ctx.fillStyle = isLight ? '#475569' : '#94a3b8';
      ctx.font = '15px Inter, sans-serif';
      ctx.fillText('For successfully completing the interactive hands-on training lab:', canvas.width / 2, 255);

      ctx.fillStyle = isLight ? '#0f172a' : '#f8fafc';
      ctx.font = 'bold 20px Inter, sans-serif';
      ctx.fillText(LAB_TITLE_STRING, canvas.width / 2, 295);

      const dateStr = new Date().toLocaleDateString('en-US', {{ year: 'numeric', month: 'long', day: 'numeric' }});
      ctx.fillStyle = isLight ? '#64748b' : '#64748b';
      ctx.font = '14px Inter, sans-serif';
      ctx.fillText('Issued on: ' + dateStr, canvas.width / 2, 345);

      ctx.beginPath();
      ctx.arc(canvas.width / 2, 410, 30, 0, Math.PI * 2);
      ctx.fillStyle = '#8b5cf6';
      ctx.fill();

      ctx.fillStyle = '#ffffff';
      ctx.font = 'bold 18px Inter, sans-serif';
      ctx.fillText('★', canvas.width / 2, 416);
    }}

    function downloadCertificate() {{
      const canvas = document.getElementById('certCanvas');
      if (!canvas) return;
      const link = document.createElement('a');
      link.download = LAB_FILE_NAME + '_Certificate.png';
      link.href = canvas.toDataURL('image/png');
      link.click();
    }}

    window.addEventListener('DOMContentLoaded', () => {{
      setupChecklists();
      setupQuizListeners();
      goToStep(0);
    }});
  </script>
</body>
</html>
"""
    return html_content
