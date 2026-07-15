import re

path = r'c:\antigravity\mission-control\static\index.html'
try:
    with open(path, 'r', encoding='utf-8') as f:
        html = f.read()
    
    settings_html = """
    <!-- ANTIGRAVITY ADVANCED SETTINGS -->
    <div class="modal-overlay" id="modal-settings">
      <div class="modal" style="width: 600px;">
        <div class="modal-title">Antigravity Engine Settings</div>
        <div class="modal-sub">Configure API Keys, LLM endpoints, and Global Agent Customizations</div>
        
        <div style="max-height: 50vh; overflow-y: auto; padding-right: 10px;">
            <div class="form-group">
            <label class="form-label">NVIDIA NIM API Key</label>
            <input type="password" class="form-input" id="cfg-api-key" placeholder="nvapi-...">
            </div>
            <div class="form-group">
            <label class="form-label">LLM Model Override</label>
            <input type="text" class="form-input" id="cfg-model" placeholder="nvidia/nemotron-3-ultra-550b-a55b">
            </div>
            <div class="form-group">
            <label class="form-label">OmniRoute / OpenClaw Gateway URL</label>
            <input type="text" class="form-input" id="cfg-gateway-url" placeholder="http://localhost:20128/v1/chat/completions">
            </div>
            <div class="form-group">
            <label class="form-label">Antigravity System Prompt (ReAct Loop)</label>
            <textarea class="form-input" id="cfg-system-prompt" style="height: 120px;" placeholder="You are an autonomous AI..."></textarea>
            </div>
            <div class="form-group">
            <label class="form-label">Workspace Rules (AGENTS.md Context)</label>
            <textarea class="form-input" id="cfg-workspace-rules" style="height: 120px;" placeholder="Enter custom rules and instructions..."></textarea>
            </div>
        </div>
        
        <div class="modal-actions">
          <button class="btn-secondary" id="settings-cancel">Cancel</button>
          <button class="btn-primary" id="settings-save">Save Settings</button>
        </div>
      </div>
    </div>
    """
    
    # Remove old modal-settings if it exists
    if 'id="modal-settings"' in html:
        html = re.sub(r'<div class="modal-overlay" id="modal-settings">.*?</div>\s*</div>\s*</div>', settings_html, html, flags=re.DOTALL)
    else:
        # insert before body tag ends
        html = html.replace('</body>', settings_html + '\n</body>')
        
    with open(path, 'w', encoding='utf-8') as f:
        f.write(html)
    print('Settings UI integrated successfully.')
except Exception as e:
    print('Error:', e)
