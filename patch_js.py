import re

path = r'c:\antigravity\mission-control\static\index.html'
try:
    with open(path, 'r', encoding='utf-8') as f:
        html = f.read()
    
    js_patch = """
// ─── SETTINGS ─────────────────────────────────────────────────────────────────
document.getElementById('btn-settings').addEventListener('click', async () => {
  const s = await api('/api/settings');
  document.getElementById('cfg-api-key').value = s.api_key || '';
  document.getElementById('cfg-model').value = s.model || 'nvidia/nemotron-3-ultra-550b-a55b';
  document.getElementById('cfg-gateway-url').value = s.gateway_url || 'http://localhost:20128/v1/chat/completions';
  document.getElementById('cfg-system-prompt').value = s.system_prompt || '';
  document.getElementById('cfg-workspace-rules').value = s.workspace_rules || '';
  document.getElementById('modal-settings').classList.add('open');
});
document.getElementById('settings-cancel').addEventListener('click', () => document.getElementById('modal-settings').classList.remove('open'));
document.getElementById('settings-save').addEventListener('click', async () => {
  const res = await api('/api/settings', 'POST', {
    api_key: document.getElementById('cfg-api-key').value,
    model: document.getElementById('cfg-model').value,
    gateway_url: document.getElementById('cfg-gateway-url').value,
    system_prompt: document.getElementById('cfg-system-prompt').value,
    workspace_rules: document.getElementById('cfg-workspace-rules').value
  });
  if (res.success) { toast('✅ Settings saved'); document.getElementById('modal-settings').classList.remove('open'); }
});
    """
    
    html = re.sub(r'// ─── SETTINGS ───.*?(?=\n// ─── EXPORT ───)', js_patch.strip(), html, flags=re.DOTALL)
    
    with open(path, 'w', encoding='utf-8') as f:
        f.write(html)
    print('JS patched.')
except Exception as e:
    print('Error:', e)
