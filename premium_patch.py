import re
import os

def patch_index():
    path = r'c:\antigravity\mission-control\static\index.html'
    with open(path, 'r', encoding='utf-8') as f:
        html = f.read()

    # 1. Restore topbar-sub and add premium custom dropdown
    old_dropdown = r'<div class="topbar-sub" style="display:flex; align-items:center; gap:8px;">.*?</div>'
    premium_dropdown = """
      <div id="topbar-sub" style="display:none;"></div>
      <div class="premium-project-selector" onclick="toggleProjectDropdown(event)">
        <i class="fa-solid fa-layer-group"></i>
        <span id="active-project-label">Personal Profile</span>
        <i class="fa-solid fa-chevron-down" style="font-size: 10px; opacity: 0.5;"></i>
        
        <div class="project-dropdown-menu" id="project-dropdown-menu">
          <div class="dropdown-item active" onclick="selectProject('personal', 'Personal Profile', event)">
            <i class="fa-solid fa-user"></i> Personal Profile
          </div>
          <div class="dropdown-item" onclick="selectProject('demo_project', 'Demo SaaS Project', event)">
            <i class="fa-solid fa-rocket"></i> Demo SaaS Project
          </div>
          <div class="dropdown-divider"></div>
          <div class="dropdown-item" onclick="event.stopPropagation(); toast('New project UI coming soon')">
            <i class="fa-solid fa-plus"></i> Create Project
          </div>
        </div>
      </div>
"""
    # Replace the old ugly dropdown (if it exists) with the new premium one
    html = re.sub(old_dropdown, premium_dropdown.strip(), html, flags=re.DOTALL)

    # 2. Add premium CSS
    premium_css = """
    /* Premium Project Selector */
    .premium-project-selector {
      position: relative;
      display: flex;
      align-items: center;
      gap: 8px;
      padding: 6px 14px;
      background: var(--surface2);
      border: 1px solid var(--border);
      border-radius: 20px;
      font-size: 13px;
      font-weight: 600;
      color: var(--text);
      cursor: pointer;
      transition: all 0.2s ease;
      user-select: none;
    }
    .premium-project-selector:hover {
      background: var(--surface);
      border-color: var(--border2);
      box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }
    .project-dropdown-menu {
      position: absolute;
      top: calc(100% + 8px);
      left: 0;
      width: 220px;
      background: rgba(25, 27, 31, 0.85);
      backdrop-filter: blur(16px);
      -webkit-backdrop-filter: blur(16px);
      border: 1px solid var(--border);
      border-radius: 12px;
      box-shadow: 0 10px 30px rgba(0,0,0,0.3);
      padding: 8px;
      display: none;
      flex-direction: column;
      gap: 4px;
      z-index: 1000;
      animation: dropdown-fade 0.2s ease;
    }
    .project-dropdown-menu.show { display: flex; }
    @keyframes dropdown-fade { from { opacity: 0; transform: translateY(-5px); } to { opacity: 1; transform: translateY(0); } }
    .dropdown-item {
      display: flex;
      align-items: center;
      gap: 10px;
      padding: 10px 12px;
      border-radius: 8px;
      font-size: 13px;
      font-weight: 500;
      color: var(--text2);
      cursor: pointer;
      transition: all 0.15s ease;
    }
    .dropdown-item i { width: 14px; text-align: center; font-size: 14px; }
    .dropdown-item:hover { background: var(--surface2); color: var(--text); }
    .dropdown-item.active { background: var(--accent-soft); color: var(--accent); font-weight: 600; }
    .dropdown-divider { height: 1px; background: var(--border); margin: 4px 0; }
"""
    if "/* Premium Project Selector */" not in html:
        html = html.replace('/* Topbar */', premium_css + '\n    /* Topbar */')

    # 3. Add JS for dropdown
    premium_js = """
let activeProjectId = 'personal';

function toggleProjectDropdown(e) {
  e.stopPropagation();
  document.getElementById('project-dropdown-menu').classList.toggle('show');
}

function selectProject(id, name, e) {
  e.stopPropagation();
  activeProjectId = id;
  document.getElementById('active-project-label').textContent = name;
  document.querySelectorAll('.dropdown-item').forEach(el => el.classList.remove('active'));
  e.currentTarget.classList.add('active');
  document.getElementById('project-dropdown-menu').classList.remove('show');
  toast('Switched to ' + name);
}

document.addEventListener('click', () => {
  const menu = document.getElementById('project-dropdown-menu');
  if(menu) menu.classList.remove('show');
});
"""
    # Replace the old changeProject function
    html = re.sub(r"let activeProjectId = 'personal';.*?toast\('Switched active project context'\);\s*\}", premium_js.strip(), html, flags=re.DOTALL)

    # 4. Inject Views in Sidebar
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
    if "<!-- Antigravity Views -->" not in html:
        html = html.replace('<div class="sidebar-section-label">SQUAD DIRECTORY</div>', views_html + '\n    <div class="sidebar-section-label">SQUAD DIRECTORY</div>')

    # 5. Inject Antigravity Chat Mode Container
    chat_container_html = """
    <!-- ANTIGRAVITY CHAT VIEW -->
    <div id="chat-view" style="display: none; flex: 1; flex-direction: row; height: 100%;">
      <div style="width: 260px; border-right: 1px solid var(--border); background: var(--surface2); display: flex; flex-direction: column;">
        <div style="padding: 20px; border-bottom: 1px solid var(--border);">
          <button class="btn-primary" style="width: 100%; justify-content: center; border-radius: 20px;" onclick="newChat()">
            <i class="fa-solid fa-plus"></i> New Conversation
          </button>
        </div>
        <div id="chat-history-list" style="flex: 1; overflow-y: auto; padding: 15px;">
          <!-- Chat history items -->
          <div style="padding: 10px; border-radius: 8px; background: var(--surface); color: var(--text); font-size: 13px; font-weight: 500; cursor: pointer; border: 1px solid var(--border2);">
            <i class="fa-regular fa-message"></i> General Assistance
          </div>
        </div>
      </div>
      <div style="flex: 1; display: flex; flex-direction: column; background: var(--bg);">
        <div id="active-chat-messages" style="flex: 1; overflow-y: auto; padding: 30px; display: flex; flex-direction: column; gap: 24px;">
          <div style="display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100%; color: var(--text3);">
            <div style="width: 64px; height: 64px; border-radius: 50%; background: var(--surface2); display: flex; align-items: center; justify-content: center; font-size: 28px; margin-bottom: 16px;">
              🌌
            </div>
            <h2 style="color: var(--text); font-weight: 600; margin-bottom: 8px;">Antigravity Mode</h2>
            <p>I am your personal intelligence layer. How can I assist you today?</p>
          </div>
        </div>
        <div style="padding: 24px; background: transparent;">
          <div style="display: flex; gap: 12px; max-width: 800px; margin: 0 auto; background: var(--surface2); padding: 8px; border-radius: 24px; border: 1px solid var(--border); box-shadow: 0 4px 20px rgba(0,0,0,0.1);">
            <input type="text" id="main-chat-input" placeholder="Message Antigravity..." style="flex: 1; padding: 12px 16px; border-radius: 16px; border: none; background: transparent; color: var(--text); outline: none; font-size: 14px;">
            <button class="btn-primary" onclick="sendMainChat()" style="padding: 0 24px; border-radius: 16px; font-weight: 600;">
              <i class="fa-solid fa-arrow-up"></i>
            </button>
          </div>
          <div style="text-align: center; font-size: 11px; color: var(--text3); margin-top: 12px;">Antigravity can make mistakes. Verify important information.</div>
        </div>
      </div>
    </div>
"""
    if "ANTIGRAVITY CHAT VIEW" not in html:
        html = html.replace('<div id="board-container"', chat_container_html + '\n      <div id="board-container"')

    # 6. Ensure Task Drawer Chat is properly appended
    task_chat_html = """
    <div class="drawer-chat-input" style="padding: 20px; border-top: 1px solid var(--border); background: var(--surface); display: flex; gap: 10px;">
      <input type="text" id="task-chat-input" placeholder="Message the assigned agent to steer this task..." style="flex: 1; padding: 12px 16px; border-radius: 12px; border: 1px solid var(--border); background: var(--surface2); color: var(--text); outline: none;">
      <button onclick="sendTaskChat()" class="btn-primary" style="padding: 0 20px; border-radius: 12px;">Send</button>
    </div>
"""
    if "drawer-chat-input" not in html:
        # We need to insert this right before the drawer closes.
        # The drawer HTML ends with:
        #       </div> <!-- /comment-thread -->
        #     </div>
        #   </div>
        # </div>
        html = html.replace('      </div>\n    </div>\n  </div>\n</div>\n\n  <!-- MODAL: NEW TASK -->', '      </div>\n    </div>\n' + task_chat_html + '\n  </div>\n</div>\n\n  <!-- MODAL: NEW TASK -->')


    # 7. Add switchView JS if missing
    view_js = """
// ─── ANTIGRAVITY VIEWS ─────────────────────────────────────────────────────────
function switchView(view) {
  document.getElementById('board-container').style.display = view === 'board' ? 'flex' : 'none';
  document.getElementById('filters-bar').style.display = view === 'board' ? 'flex' : 'none';
  document.getElementById('chat-view').style.display = view === 'chat' ? 'flex' : 'none';
  
  // Highlight sidebar
  const items = document.querySelectorAll('.sidebar-agents:first-of-type .agent-item');
  if(items.length >= 3) {
      items.forEach(el => el.classList.remove('selected'));
      if(view === 'board') items[0].classList.add('selected');
      if(view === 'chat') items[1].classList.add('selected');
      if(view === 'projects') items[2].classList.add('selected');
  }
}

let activeTaskId = null;
const origOpenDrawer = openTaskDrawer;
openTaskDrawer = function(id) {
  activeTaskId = id;
  origOpenDrawer(id);
};

async function sendTaskChat() {
  const inp = document.getElementById('task-chat-input');
  if(!inp) return;
  const text = inp.value.trim();
  if(!text || !activeTaskId) return;
  inp.value = '';
  await api(`/api/tasks/${activeTaskId}/chat`, 'POST', { text });
  openTaskDrawer(activeTaskId);
  refreshAll();
}

async function sendMainChat() {
  const inp = document.getElementById('main-chat-input');
  const text = inp.value.trim();
  if(!text) return;
  inp.value = '';
  
  const msgContainer = document.getElementById('active-chat-messages');
  if (msgContainer.innerHTML.includes('How can I assist')) {
      msgContainer.innerHTML = '';
  }

  const div = document.createElement('div');
  div.style.alignSelf = 'flex-end';
  div.style.background = 'var(--surface2)';
  div.style.padding = '12px 18px';
  div.style.borderRadius = '18px 18px 4px 18px';
  div.style.maxWidth = '70%';
  div.style.color = 'var(--text)';
  div.innerHTML = text;
  msgContainer.appendChild(div);
  msgContainer.scrollTop = msgContainer.scrollHeight;
  
  const res = await api('/api/chat/message', 'POST', { text });
  
  const reply = document.createElement('div');
  reply.style.alignSelf = 'flex-start';
  reply.style.display = 'flex';
  reply.style.gap = '12px';
  reply.style.maxWidth = '80%';
  reply.innerHTML = `
    <div style="width: 32px; height: 32px; border-radius: 50%; background: var(--purple-soft); color: var(--purple); display: flex; align-items: center; justify-content: center; font-size: 16px; flex-shrink: 0;">🌌</div>
    <div style="color: var(--text); padding-top: 6px; line-height: 1.6;">${res.reply}</div>
  `;
  msgContainer.appendChild(reply);
  msgContainer.scrollTop = msgContainer.scrollHeight;
}
"""
    if "switchView(view)" not in html:
        html = html.replace('// ─── APP INIT ──────────────────────────────────────────────────────────────', view_js + '\n// ─── APP INIT ──────────────────────────────────────────────────────────────')

    with open(path, 'w', encoding='utf-8') as f:
        f.write(html)
    print("index.html patched with premium UI features and crash fix.")

patch_index()
