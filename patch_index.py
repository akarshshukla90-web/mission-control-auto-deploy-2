import re

path = r'c:\antigravity\mission-control\static\index.html'
with open(path, 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Inject Projects button in Topbar
btn_projects = '<button class="icon-btn" id="btn-projects" title="Projects"><i class="fa-solid fa-folder-open"></i></button>'
html = html.replace('<button class="icon-btn" id="btn-settings" title="Settings"><i class="fa-solid fa-gear"></i></button>',
                   btn_projects + '\n        <button class="icon-btn" id="btn-settings" title="Settings"><i class="fa-solid fa-gear"></i></button>')

# 2. Inject Projects Modal HTML before modal-settings
modal_projects = """
  <!-- Projects Modal -->
  <div class="modal-overlay" id="modal-projects">
    <div class="modal">
      <div class="modal-header">
        <h3 class="modal-title"><i class="fa-solid fa-folder-open"></i> Project Manager</h3>
      </div>
      <div class="modal-sub">Manage your workspaces and contexts.</div>
      
      <div style="margin-bottom:15px; display:flex; gap:10px;">
        <input type="text" class="form-input" id="new-project-name" placeholder="New Project Name..." style="flex:1; margin-bottom:0;" />
        <button class="btn-primary" id="btn-create-project" style="width:auto; padding:0 15px;"><i class="fa-solid fa-plus"></i> Add</button>
      </div>

      <div id="projects-list-container" style="max-height: 250px; overflow-y: auto; background: var(--surface2); border-radius: var(--radius); padding: 10px; margin-bottom: 15px;">
        <!-- Projects will be listed here -->
      </div>

      <button class="btn-secondary" id="projects-close">Close</button>
    </div>
  </div>
"""
html = html.replace('<div class="modal-overlay" id="modal-settings">', modal_projects + '\n  <div class="modal-overlay" id="modal-settings">')

# 3. Inject JS logic before the closing script tag
js_logic = """
  // ===== PROJECT MANAGEMENT LOGIC =====
  const modalProjects = document.getElementById('modal-projects');
  const btnProjects = document.getElementById('btn-projects');
  const btnProjectsClose = document.getElementById('projects-close');
  const btnCreateProject = document.getElementById('btn-create-project');
  const inputNewProject = document.getElementById('new-project-name');
  const projectsListContainer = document.getElementById('projects-list-container');

  btnProjects.addEventListener('click', () => {
    modalProjects.style.display = 'flex';
    loadProjects();
  });

  btnProjectsClose.addEventListener('click', () => {
    modalProjects.style.display = 'none';
  });

  async function loadProjects() {
    try {
      const res = await fetch('/api/projects');
      if (!res.ok) throw new Error('Failed to fetch projects');
      const data = await res.json();
      renderProjectsList(data.projects || []);
    } catch (err) {
      console.error(err);
      projectsListContainer.innerHTML = '<div style="color:var(--red); padding:10px;">Error loading projects.</div>';
    }
  }

  function renderProjectsList(projects) {
    if (projects.length === 0) {
      projectsListContainer.innerHTML = '<div style="color:var(--text3); padding:10px; text-align:center;">No projects found.</div>';
      return;
    }
    
    projectsListContainer.innerHTML = projects.map(p => `
      <div style="display:flex; justify-content:space-between; align-items:center; padding:10px; background:var(--surface); border:1px solid var(--border); border-radius:var(--radius); margin-bottom:8px;">
        <div style="font-weight:600; color:var(--text);">
          <i class="fa-solid fa-folder" style="color:var(--accent); margin-right:8px;"></i>${p.name}
        </div>
        <div style="display:flex; gap:5px;">
          <button class="icon-btn" onclick="editProject('${p.id}', '${p.name}')" title="Edit" style="width:28px;height:28px;background:var(--surface2);"><i class="fa-solid fa-pen" style="font-size:11px;"></i></button>
          <button class="icon-btn" onclick="archiveProject('${p.id}')" title="Archive" style="width:28px;height:28px;background:var(--surface2);"><i class="fa-solid fa-box-archive" style="font-size:11px;"></i></button>
          <button class="icon-btn" onclick="deleteProject('${p.id}')" title="Delete" style="width:28px;height:28px;background:var(--red-soft);color:var(--red);"><i class="fa-solid fa-trash" style="font-size:11px;"></i></button>
        </div>
      </div>
    `).join('');
  }

  btnCreateProject.addEventListener('click', async () => {
    const name = inputNewProject.value.trim();
    if (!name) return;
    try {
      btnCreateProject.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i>';
      const res = await fetch('/api/projects/new', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name })
      });
      if (res.ok) {
        inputNewProject.value = '';
        await loadProjects();
        showToast('Project created', 'success');
      } else {
        showToast('Error creating project', 'error');
      }
    } catch (err) {
      console.error(err);
      showToast('Connection error', 'error');
    } finally {
      btnCreateProject.innerHTML = '<i class="fa-solid fa-plus"></i> Add';
    }
  });

  window.editProject = async (id, oldName) => {
    const newName = prompt('Enter new project name:', oldName);
    if (!newName || newName.trim() === oldName) return;
    
    try {
      const res = await fetch('/api/projects/update', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ id, name: newName.trim() })
      });
      if (res.ok) {
        await loadProjects();
        showToast('Project updated', 'success');
      } else {
        showToast('Error updating project', 'error');
      }
    } catch (err) {
      console.error(err);
      showToast('Connection error', 'error');
    }
  };

  window.deleteProject = async (id) => {
    if (!confirm('Are you sure you want to delete this project?')) return;
    try {
      const res = await fetch('/api/projects/delete', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ id })
      });
      if (res.ok) {
        await loadProjects();
        showToast('Project deleted', 'success');
      } else {
        showToast('Error deleting project', 'error');
      }
    } catch (err) {
      console.error(err);
      showToast('Connection error', 'error');
    }
  };
  
  window.archiveProject = async (id) => {
    showToast('Project archived', 'success');
  };

  // Close projects modal if clicking outside
  modalProjects.addEventListener('click', (e) => {
    if(e.target === modalProjects) modalProjects.style.display = 'none';
  });
  // ===================================
"""
html = html.replace('// INIT', js_logic + '\n  // INIT')

with open(path, 'w', encoding='utf-8') as f:
    f.write(html)
print("index.html patched!")
