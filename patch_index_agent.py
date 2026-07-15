import re

path = r'c:\antigravity\mission-control\static\index.html'
with open(path, 'r', encoding='utf-8') as f:
    html = f.read()

engine_options = """
  <option value="OmniRoute (Unified Gateway)">OmniRoute (Unified Gateway)</option>
  <option value="NVIDIA NIM (GPU Accelerated)">NVIDIA NIM (GPU Accelerated)</option>
  <option value="Claude (Fallback)">Claude (Fallback)</option>
  <option value="OpenAI">OpenAI</option>
"""

# 1. Update `#modal-spawn` to add Engine dropdown
spawn_form_old = """<input type="text" class="form-input" id="spawn-skills" placeholder="e.g. Google-Ads, PPC, Analytics" />
      <textarea class="form-input" id="spawn-about" placeholder="Describe this agent's expertise and methodologies..."></textarea>"""

spawn_form_new = f"""<input type="text" class="form-input" id="spawn-skills" placeholder="e.g. Google-Ads, PPC, Analytics" />
      <select class="form-input" id="spawn-engine">
        {engine_options}
      </select>
      <textarea class="form-input" id="spawn-about" placeholder="Describe this agent's expertise and methodologies..."></textarea>"""
html = html.replace(spawn_form_old, spawn_form_new)

# 2. Add Edit Modal
edit_modal = f"""
  <!-- Edit Agent Modal -->
  <div class="modal-overlay" id="modal-edit-agent">
    <div class="modal">
      <div class="modal-header">
        <h3 class="modal-title"><i class="fa-solid fa-pen"></i> Edit Agent Persona</h3>
      </div>
      <input type="hidden" id="edit-key" />
      <input type="text" class="form-input" id="edit-name" placeholder="Name" />
      <input type="text" class="form-input" id="edit-title" placeholder="Title" />
      <select class="form-input" id="edit-role">
        <option value="SPC">Specialist (SPC)</option>
        <option value="TL">Team Lead (TL)</option>
        <option value="QA">Quality Analyst (QA)</option>
      </select>
      <input type="text" class="form-input" id="edit-skills" placeholder="Skills (comma separated)" />
      <select class="form-input" id="edit-engine">
        {engine_options}
      </select>
      <textarea class="form-input" id="edit-about" placeholder="Persona / About"></textarea>
      <div style="display:flex; justify-content:flex-end; gap:10px; margin-top:20px;">
        <button class="btn-secondary" id="edit-cancel">Cancel</button>
        <button class="btn-primary" id="edit-submit"><i class="fa-solid fa-floppy-disk"></i> Save Changes</button>
      </div>
    </div>
  </div>
"""
html = html.replace('<div class="modal-overlay" id="modal-spawn">', edit_modal + '\n  <div class="modal-overlay" id="modal-spawn">')

# 3. Add Edit Button in Agent Drawer
drawer_old = """
    ${!isCore ? `<div style="margin-top:20px"><button class="btn-secondary" onclick="retireAgent('${key}')"><i class="fa-solid fa-user-minus"></i> Retire Agent</button></div>` : ''}
  `;
"""
drawer_new = """
    <div style="margin-top:20px; display:flex; gap:10px;">
      <button class="btn-secondary" onclick="openEditAgent('${key}')"><i class="fa-solid fa-pen"></i> Edit Persona</button>
      ${!isCore ? `<button class="btn-secondary" onclick="retireAgent('${key}')" style="color:var(--red)"><i class="fa-solid fa-user-minus"></i> Retire</button>` : ''}
    </div>
  `;
"""
html = html.replace(drawer_old, drawer_new)

# 4. Add Engine badge in Agent Drawer
about_old = """      <div style="font-size:12px;color:var(--text2);margin-top:10px;line-height:1.5">${agent.about || 'No details provided.'}</div>"""
about_new = """      <div style="font-size:11px;color:var(--text3);margin-top:10px;text-transform:uppercase;">ENGINE: <span style="font-weight:600;color:var(--accent);">${agent.engine || 'OmniRoute (Unified Gateway)'}</span></div>
      <div style="font-size:12px;color:var(--text2);margin-top:5px;line-height:1.5">${agent.about || 'No details provided.'}</div>"""
html = html.replace(about_old, about_new)

# 5. JS updates
js_updates = """
// ─── EDIT AGENT ──────────────────────────────────────────────────────────────
function openEditAgent(key) {
  const agent = activeAgents[key];
  if (!agent) return;
  document.getElementById('edit-key').value = key;
  document.getElementById('edit-name').value = agent.name;
  document.getElementById('edit-title').value = agent.title || '';
  document.getElementById('edit-role').value = agent.role || 'SPC';
  document.getElementById('edit-skills').value = (agent.skills || []).join(', ');
  document.getElementById('edit-engine').value = agent.engine || 'OmniRoute (Unified Gateway)';
  document.getElementById('edit-about').value = agent.about || '';
  document.getElementById('modal-edit-agent').classList.add('open');
}

document.getElementById('edit-cancel').addEventListener('click', () => {
  document.getElementById('modal-edit-agent').classList.remove('open');
});

document.getElementById('edit-submit').addEventListener('click', async () => {
  const key = document.getElementById('edit-key').value;
  const name = document.getElementById('edit-name').value.trim();
  const title = document.getElementById('edit-title').value.trim();
  const role = document.getElementById('edit-role').value;
  const skills = document.getElementById('edit-skills').value.split(',').map(s => s.trim()).filter(Boolean);
  const engine = document.getElementById('edit-engine').value;
  const about = document.getElementById('edit-about').value.trim();
  
  if (!name) { toast('⚠️ Name is required'); return; }
  
  const res = await api('/api/agents/update', 'POST', { key, name, title, role, skills, engine, about });
  if (res.success) {
    toast(`✅ ${name} updated!`);
    document.getElementById('modal-edit-agent').classList.remove('open');
    await refreshAll();
    openAgentDrawer(key); // refresh drawer
  } else {
    toast('❌ ' + res.error);
  }
});
"""
# inject right before // ─── SETTINGS
html = html.replace('// ─── SETTINGS', js_updates + '\n// ─── SETTINGS')

# 6. Update spawn endpoint JS
spawn_js_old = """const about = document.getElementById('spawn-about').value.trim();
  if (!key || !name) { toast('⚠️ Key and name are required'); return; }
  const res = await api('/api/agents/spawn', 'POST', { key, name, title, role, skills, about });"""
spawn_js_new = """const engine = document.getElementById('spawn-engine').value;
  const about = document.getElementById('spawn-about').value.trim();
  if (!key || !name) { toast('⚠️ Key and name are required'); return; }
  const res = await api('/api/agents/spawn', 'POST', { key, name, title, role, skills, engine, about });"""
html = html.replace(spawn_js_old, spawn_js_new)

with open(path, 'w', encoding='utf-8') as f:
    f.write(html)
print("index.html patched with Agent editing!")
