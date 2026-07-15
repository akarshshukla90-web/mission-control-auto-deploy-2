import re

def patch_index():
    path = r'c:\antigravity\mission-control\static\index.html'
    with open(path, 'r', encoding='utf-8') as f:
        html = f.read()

    # 1. Premium CSS Injection right before </style>
    premium_css = """
    /* Premium Project Selector */
    .premium-project-selector { position: relative; display: flex; align-items: center; gap: 8px; padding: 6px 14px; background: var(--surface2); border: 1px solid var(--border); border-radius: 20px; font-size: 13px; font-weight: 600; color: var(--text); cursor: pointer; transition: all 0.2s ease; user-select: none; }
    .premium-project-selector:hover { background: var(--surface); border-color: var(--border2); box-shadow: 0 4px 12px rgba(0,0,0,0.1); }
    .project-dropdown-menu { position: absolute; top: calc(100% + 8px); left: 0; width: 220px; background: rgba(25, 27, 31, 0.95); backdrop-filter: blur(16px); -webkit-backdrop-filter: blur(16px); border: 1px solid var(--border); border-radius: 12px; box-shadow: 0 10px 30px rgba(0,0,0,0.5); padding: 8px; display: none; flex-direction: column; gap: 4px; z-index: 1000; animation: dropdown-fade 0.2s ease; }
    .project-dropdown-menu.show { display: flex; }
    @keyframes dropdown-fade { from { opacity: 0; transform: translateY(-5px); } to { opacity: 1; transform: translateY(0); } }
    .dropdown-item { display: flex; align-items: center; gap: 10px; padding: 10px 12px; border-radius: 8px; font-size: 13px; font-weight: 500; color: var(--text2); cursor: pointer; transition: all 0.15s ease; }
    .dropdown-item i { width: 14px; text-align: center; font-size: 14px; }
    .dropdown-item:hover { background: var(--surface2); color: var(--text); }
    .dropdown-item.active { background: var(--accent-soft); color: var(--accent); font-weight: 600; }
    .dropdown-divider { height: 1px; background: var(--border); margin: 4px 0; }
    
    /* Projects View */
    .project-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 20px; padding: 20px; }
    .project-card { background: var(--surface); border: 1px solid var(--border); border-radius: 12px; padding: 20px; transition: all 0.2s ease; cursor: pointer; }
    .project-card:hover { border-color: var(--accent); transform: translateY(-2px); box-shadow: 0 10px 20px rgba(0,0,0,0.2); }
"""
    if ".premium-project-selector" not in html:
        html = html.replace("</style>", premium_css + "\n</style>")

    # 2. Inject Sidebar Views (Regex search case-insensitive for Squad Directory)
    views_html = """
  <!-- Antigravity Views -->
  <div class="sidebar-section-label">Views</div>
  <div class="sidebar-agents" style="flex: 0 0 auto; margin-bottom: 20px;">
    <div class="agent-item selected" onclick="switchView('board')">
      <div class="agent-avatar" style="background:var(--surface2)">📊</div>
      <div class="agent-info"><div class="agent-name">Command Board</div></div>
    </div>
    <div class="agent-item" onclick="switchView('chat')">
      <div class="agent-avatar" style="background:var(--purple-soft)">💬</div>
      <div class="agent-info"><div class="agent-name" style="color:var(--purple)">Conversations</div></div>
    </div>
    <div class="agent-item" onclick="switchView('projects')">
      <div class="agent-avatar" style="background:var(--surface2)">📂</div>
      <div class="agent-info"><div class="agent-name">Projects</div></div>
    </div>
  </div>
"""
    # Look for `<div class="sidebar-section-label">Squad Directory</div>` case-insensitively
    if "<!-- Antigravity Views -->" not in html:
        html = re.sub(r'(<div class="sidebar-section-label">Squad Directory</div>)', views_html + r'\1', html, flags=re.IGNORECASE)

    # 3. Inject Antigravity Chat Container and Projects Container
    ui_containers = """
    <!-- ANTIGRAVITY CHAT VIEW -->
    <div id="chat-view" style="display: none; flex: 1; flex-direction: row; height: 100%;">
      <div style="width: 260px; border-right: 1px solid var(--border); background: var(--surface2); display: flex; flex-direction: column;">
        <div style="padding: 20px; border-bottom: 1px solid var(--border);">
          <button class="btn-primary" style="width: 100%; justify-content: center; border-radius: 20px;" onclick="newChat()">
            <i class="fa-solid fa-plus"></i> New Conversation
          </button>
        </div>
        <div id="chat-history-list" style="flex: 1; overflow-y: auto; padding: 15px;">
          <div style="padding: 10px; border-radius: 8px; background: var(--surface); color: var(--text); font-size: 13px; font-weight: 500; cursor: pointer; border: 1px solid var(--border2);">
            <i class="fa-regular fa-message"></i> General Assistance
          </div>
        </div>
      </div>
      <div style="flex: 1; display: flex; flex-direction: column; background: var(--bg);">
        <div id="active-chat-messages" style="flex: 1; overflow-y: auto; padding: 30px; display: flex; flex-direction: column; gap: 24px;">
          <div style="display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100%; color: var(--text3);">
            <div style="width: 64px; height: 64px; border-radius: 50%; background: var(--surface2); display: flex; align-items: center; justify-content: center; font-size: 28px; margin-bottom: 16px;">🌌</div>
            <h2 style="color: var(--text); font-weight: 600; margin-bottom: 8px;">Antigravity Mode</h2>
            <p>I am your personal intelligence layer. How can I assist you today?</p>
          </div>
        </div>
        <div style="padding: 24px; background: transparent;">
          <div style="display: flex; gap: 12px; max-width: 800px; margin: 0 auto; background: var(--surface2); padding: 8px; border-radius: 24px; border: 1px solid var(--border); box-shadow: 0 4px 20px rgba(0,0,0,0.1);">
            <input type="text" id="main-chat-input" placeholder="Message Antigravity..." style="flex: 1; padding: 12px 16px; border-radius: 16px; border: none; background: transparent; color: var(--text); outline: none; font-size: 14px;">
            <button class="btn-primary" onclick="sendMainChat()" style="padding: 0 24px; border-radius: 16px; font-weight: 600;"><i class="fa-solid fa-arrow-up"></i></button>
          </div>
        </div>
      </div>
    </div>

    <!-- PROJECTS VIEW -->
    <div id="projects-view" style="display: none; flex: 1; flex-direction: column; overflow-y: auto; background: var(--bg);">
      <div style="padding: 40px; max-width: 1200px; margin: 0 auto; width: 100%;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 30px;">
          <h1 style="font-size: 24px; font-weight: 700; color: var(--text);">Project Manager</h1>
          <button class="btn-primary" onclick="openNewProjectModal()"><i class="fa-solid fa-plus"></i> Create Project</button>
        </div>
        <div class="project-grid" id="project-grid">
          <!-- populated dynamically -->
        </div>
      </div>
    </div>
    
    <!-- MODAL: NEW PROJECT -->
    <div class="modal-overlay" id="modal-new-project">
      <div class="modal">
        <div class="modal-header">
          <div class="modal-title">Create Project</div>
          <button class="icon-btn" onclick="document.getElementById('modal-new-project').classList.remove('show')"><i class="fa-solid fa-xmark"></i></button>
        </div>
        <div class="modal-body">
          <label class="form-label">Project Name</label>
          <input type="text" class="form-input" id="new-project-name" placeholder="e.g. Acme Corp Rebranding" />
          
          <label class="form-label">Project Context & Rules</label>
          <textarea class="form-input" id="new-project-context" rows="5" placeholder="Provide background info, rules, target audience, and specific guidelines for this project..."></textarea>
          
          <button class="btn-primary" style="width: 100%; margin-top: 15px; justify-content: center;" onclick="submitNewProject()">Create Project</button>
        </div>
      </div>
    </div>
"""
    if "<!-- PROJECTS VIEW -->" not in html:
        # Inject right before <div id="board-wrap">
        html = html.replace('<div id="board-wrap">', ui_containers + '\n  <div id="board-wrap">')

    # 4. Project Logic and Refresh Integration
    js_logic = """
let serverProjects = [];

async function loadProjects() {
    try {
        const res = await api('/api/projects');
        serverProjects = res.projects || [];
        renderProjectDropdown();
        renderProjectGrid();
    } catch(e) {}
}

function renderProjectDropdown() {
    const menu = document.getElementById('project-dropdown-menu');
    if(!menu) return;
    let html = '';
    serverProjects.forEach(p => {
        const isActive = (p.id === activeProjectId) ? 'active' : '';
        const icon = p.id === 'personal' ? 'fa-user' : 'fa-folder';
        html += `<div class="dropdown-item ${isActive}" onclick="selectProject('${p.id}', '${p.name}', event)">
            <i class="fa-solid ${icon}"></i> ${p.name}
        </div>`;
    });
    html += `<div class="dropdown-divider"></div>
             <div class="dropdown-item" onclick="event.stopPropagation(); document.getElementById('project-dropdown-menu').classList.remove('show'); openNewProjectModal();">
                <i class="fa-solid fa-plus"></i> Create Project
             </div>`;
    menu.innerHTML = html;
    
    const activeP = serverProjects.find(p => p.id === activeProjectId);
    if(activeP) {
        document.getElementById('active-project-label').textContent = activeP.name;
    }
}

function renderProjectGrid() {
    const grid = document.getElementById('project-grid');
    if(!grid) return;
    grid.innerHTML = serverProjects.map(p => `
        <div class="project-card" onclick="selectProject('${p.id}', '${p.name}', {stopPropagation:()=>{}})">
            <div style="font-size: 16px; font-weight: 700; margin-bottom: 8px; color: var(--text);"><i class="fa-solid ${p.id==='personal'?'fa-user':'fa-folder'}"></i> ${p.name}</div>
            <div style="font-size: 12px; color: var(--text2); line-height: 1.5; overflow: hidden; display: -webkit-box; -webkit-line-clamp: 3; -webkit-box-orient: vertical;">${p.context}</div>
            ${p.id === activeProjectId ? '<div style="margin-top: 15px; display: inline-block; padding: 4px 10px; background: var(--accent-soft); color: var(--accent); border-radius: 12px; font-size: 11px; font-weight: 700;">ACTIVE</div>' : ''}
        </div>
    `).join('');
}

function openNewProjectModal() {
    document.getElementById('new-project-name').value = '';
    document.getElementById('new-project-context').value = '';
    document.getElementById('modal-new-project').classList.add('show');
}

async function submitNewProject() {
    const name = document.getElementById('new-project-name').value.trim();
    const context = document.getElementById('new-project-context').value.trim();
    if(!name) return toast('Name is required');
    
    document.getElementById('modal-new-project').classList.remove('show');
    try {
        const res = await api('/api/projects/new', 'POST', { name, context });
        if(res.success) {
            activeProjectId = res.id;
            toast('Project created');
            await loadProjects();
        }
    } catch(e) {
        toast('Failed to create project');
    }
}

// Override switchView to handle projects view
function switchView(view) {
  document.getElementById('board-wrap').style.display = view === 'board' ? 'block' : 'none';
  document.getElementById('filters-bar').style.display = view === 'board' ? 'flex' : 'none';
  const chatView = document.getElementById('chat-view');
  if(chatView) chatView.style.display = view === 'chat' ? 'flex' : 'none';
  const projView = document.getElementById('projects-view');
  if(projView) projView.style.display = view === 'projects' ? 'flex' : 'none';
  
  // Highlight sidebar
  const items = document.querySelectorAll('.sidebar-agents:first-of-type .agent-item');
  if(items.length >= 3) {
      items.forEach(el => el.classList.remove('selected'));
      if(view === 'board') items[0].classList.add('selected');
      if(view === 'chat') items[1].classList.add('selected');
      if(view === 'projects') items[2].classList.add('selected');
  }
}
"""
    # Insert logic right after existing switchView if present, or replace the old logic
    # Wait, my previous patch probably inserted `switchView` in `index.html`.
    # Let's remove the old one and add the new one.
    code = re.sub(r'function switchView.*?\}', '', html, flags=re.DOTALL)
    if "loadProjects()" not in html:
        # hook loadProjects into app init
        html = html.replace("refreshAll();", "loadProjects();\n  refreshAll();")
        html = html.replace('// ─── APP INIT', js_logic + '\n// ─── APP INIT')

    with open(path, 'w', encoding='utf-8') as f:
        f.write(html)
    print("index.html fully patched with Project Manager and robust injection.")

patch_index()
