import re

path = r'c:\antigravity\mission-control\static\index.html'
try:
    with open(path, 'r', encoding='utf-8') as f:
        html = f.read()

    # 1. Add View Toggles to Sidebar
    views_html = """
    <!-- Antigravity Views -->
    <div class="sidebar-section-label">Views</div>
    <div class="sidebar-agents" style="flex: 0 0 auto;">
      <div class="agent-item selected" onclick="switchView('board')">
        <div class="agent-avatar" style="background:var(--surface2)">📊</div>
        <div class="agent-info"><div class="agent-name">Command Board</div></div>
      </div>
      <div class="agent-item" onclick="switchView('chat')">
        <div class="agent-avatar" style="background:var(--surface2)">💬</div>
        <div class="agent-info"><div class="agent-name">Conversations</div></div>
      </div>
      <div class="agent-item" onclick="switchView('projects')">
        <div class="agent-avatar" style="background:var(--surface2)">📂</div>
        <div class="agent-info"><div class="agent-name">Projects</div></div>
      </div>
    </div>
"""
    if "<!-- Antigravity Views -->" not in html:
        html = html.replace('<div class="sidebar-section-label">Squad</div>', views_html + '\n    <div class="sidebar-section-label">Squad</div>')

    # 2. Add Chat Input to Task Drawer
    drawer_chat_html = """
    </div>
    <div class="drawer-chat-input" style="padding: 15px; border-top: 1px solid var(--border); background: var(--surface); display: flex; gap: 8px;">
      <input type="text" id="task-chat-input" placeholder="Message the assigned agent to steer the task..." style="flex: 1; padding: 10px; border-radius: var(--radius); border: 1px solid var(--border); background: var(--surface2); color: var(--text);">
      <button onclick="sendTaskChat()" class="btn-primary" style="padding: 0 15px;">Send</button>
    </div>
  </div>
</div>
"""
    html = re.sub(r'</div>\s*</div>\s*</div>\s*<!-- MODAL: NEW TASK -->', drawer_chat_html + '\n  <!-- MODAL: NEW TASK -->', html)


    # 3. Add Antigravity Chat Container
    chat_container_html = """
    <!-- ANTIGRAVITY CHAT VIEW -->
    <div id="chat-view" style="display: none; flex: 1; flex-direction: row; height: 100%;">
      <div style="width: 250px; border-right: 1px solid var(--border); background: var(--surface2); display: flex; flex-direction: column;">
        <div style="padding: 15px; border-bottom: 1px solid var(--border);">
          <button class="btn-primary" style="width: 100%; justify-content: center;" onclick="newChat()">+ New Conversation</button>
        </div>
        <div id="chat-history-list" style="flex: 1; overflow-y: auto; padding: 10px;">
          <!-- Chat history items -->
        </div>
      </div>
      <div style="flex: 1; display: flex; flex-direction: column; background: var(--bg);">
        <div id="active-chat-messages" style="flex: 1; overflow-y: auto; padding: 20px; display: flex; flex-direction: column; gap: 15px;">
          <div style="text-align: center; color: var(--text3); margin-top: 50px;">Antigravity mode activated. How can I assist you?</div>
        </div>
        <div style="padding: 20px; border-top: 1px solid var(--border); background: var(--surface);">
          <div style="display: flex; gap: 10px; max-width: 800px; margin: 0 auto;">
            <input type="text" id="main-chat-input" placeholder="Message Antigravity..." style="flex: 1; padding: 12px 16px; border-radius: var(--radius-lg); border: 1px solid var(--border); background: var(--surface2); color: var(--text);">
            <button class="btn-primary" onclick="sendMainChat()" style="padding: 0 20px;">Send</button>
          </div>
        </div>
      </div>
    </div>
"""
    if "ANTIGRAVITY CHAT VIEW" not in html:
        html = html.replace('<div id="board-container">', chat_container_html + '\n      <div id="board-container">')

    # 4. Add CSS and JS for View Switch
    js_patch = """
// ─── ANTIGRAVITY VIEWS ─────────────────────────────────────────────────────────
function switchView(view) {
  document.getElementById('board-container').style.display = view === 'board' ? 'flex' : 'none';
  document.getElementById('filters-bar').style.display = view === 'board' ? 'flex' : 'none';
  document.getElementById('chat-view').style.display = view === 'chat' ? 'flex' : 'none';
  
  // Highlight sidebar
  const items = document.querySelectorAll('.sidebar-agents:first-of-type .agent-item');
  items.forEach(el => el.classList.remove('selected'));
  if(view === 'board') items[0].classList.add('selected');
  if(view === 'chat') items[1].classList.add('selected');
  if(view === 'projects') items[2].classList.add('selected');
}

let activeTaskId = null;
const origOpenDrawer = openTaskDrawer;
openTaskDrawer = function(id) {
  activeTaskId = id;
  origOpenDrawer(id);
};

async function sendTaskChat() {
  const inp = document.getElementById('task-chat-input');
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
  const div = document.createElement('div');
  div.innerHTML = `<strong>You:</strong> ${text}`;
  document.getElementById('active-chat-messages').appendChild(div);
  
  const res = await api('/api/chat/message', 'POST', { text });
  const reply = document.createElement('div');
  reply.innerHTML = `<strong>Antigravity:</strong> ${res.reply}`;
  document.getElementById('active-chat-messages').appendChild(reply);
}

// ─────────────────────────────────────────────────────────────────────────────
"""
    if "switchView(view)" not in html:
        html = html.replace('// ─── APP INIT ──────────────────────────────────────────────────────────────', js_patch + '\n// ─── APP INIT ──────────────────────────────────────────────────────────────')

    with open(path, 'w', encoding='utf-8') as f:
        f.write(html)
    print("index.html patched with new UI features.")
except Exception as e:
    print("Error:", e)
