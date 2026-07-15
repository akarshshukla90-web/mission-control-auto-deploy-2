import re

path = r'c:\antigravity\mission-control\static\index.html'
try:
    with open(path, 'r', encoding='utf-8') as f:
        html = f.read()

    new_buttons = """
      <div style="display:flex; gap:8px; margin-top: 4px;">
        <button class="btn-primary" onclick="saveTaskEdit('${taskId}')">Save</button>
        <button class="btn-secondary" onclick="openTaskDrawer('${taskId}')">Cancel</button>
      </div>
    </div>
  `;
}

async function archiveTask(taskId) {
  if(!confirm("Archive this task? It will be moved to the archives.")) return;
  const res = await api('/api/tasks/archive', 'POST', { task_id: taskId });
  if (res.success) {
    toast('✅ Task archived.');
    closeDrawers();
    await refreshAll();
  } else {
    toast('❌ ' + res.error);
  }
}
"""

    if "async function archiveTask" not in html:
        html = html.replace("    </div>\n  `;\n}\n\nasync function saveTaskEdit", new_buttons.strip() + "\n\nasync function saveTaskEdit")
        
        # Inject the cancel and archive buttons directly into the drawer header content too, right above the description if they aren't editing.
        # Actually, let's put them in the task drawer body instead.
        action_bar = """
  const controlsBox = `
    <div style="display:flex; gap:10px; margin-bottom: 15px; padding: 10px; background: var(--bg2); border-radius: 8px; align-items: center; justify-content: space-between;">
      <button onclick="updateTask('${task.id}')" style="flex:1; padding: 6px; font-size: 12px; border-radius: 4px; border:none; background: var(--primary); color: white; cursor: pointer; transition: 0.2s;">
        <i class="fa-solid fa-sync"></i> Update
      </button>
      <button onclick="editTask('${task.id}')" style="flex:1; padding: 6px; font-size: 12px; border-radius: 4px; border:none; background: #64748b; color: white; cursor: pointer; transition: 0.2s;">
        <i class="fa-solid fa-pen"></i> Edit
      </button>
      <button onclick="cancelTask('${task.id}')" style="flex:1; padding: 6px; font-size: 12px; border-radius: 4px; border:none; background: var(--orange); color: white; cursor: pointer; transition: 0.2s;">
        <i class="fa-solid fa-ban"></i> Cancel
      </button>
      <button onclick="archiveTask('${task.id}')" style="flex:1; padding: 6px; font-size: 12px; border-radius: 4px; border:none; background: var(--red); color: white; cursor: pointer; transition: 0.2s;">
        <i class="fa-solid fa-box-archive"></i> Archive
      </button>
    </div>
  `;
"""
        html = re.sub(r'const controlsBox = `.*?`;', action_bar.strip(), html, flags=re.DOTALL)
        
        with open(path, 'w', encoding='utf-8') as f:
            f.write(html)
        print('Archive UI patched successfully.')
    else:
        print('Archive UI already exists.')
except Exception as e:
    print('Error:', e)
