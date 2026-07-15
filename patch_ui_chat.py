import re

with open('static/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace renderChat
old_render_chat = """  function renderChat(msgs) {
    const feed = document.getElementById('chat-feed');
    const atBottom = feed.scrollHeight - feed.scrollTop <= feed.clientHeight + 40;
    const prev = feed.children.length;
    feed.innerHTML = '';
    msgs.slice(-30).forEach(m => {
      const div = document.createElement('div');
      div.className = 'chat-msg';
      div.innerHTML = `
        <span class="chat-sender">${m.sender}:</span>
        <span class="chat-text">${m.text}</span>
      `;
      feed.appendChild(div);
    });
    if (atBottom || msgs.length !== prev) feed.scrollTop = feed.scrollHeight;
  }"""

new_render_chat = """  let lastChatCount = 0;
  function renderChat(msgs) {
    const feed = document.getElementById('chat-feed');
    if (!feed) return;
    const atBottom = feed.scrollHeight - feed.scrollTop <= feed.clientHeight + 40;
    
    if (msgs.length > lastChatCount) {
        if (lastChatCount === 0) feed.innerHTML = '';
        const newMsgs = msgs.slice(lastChatCount);
        newMsgs.forEach(m => {
          const div = document.createElement('div');
          div.className = 'chat-msg';
          div.innerHTML = `
            <span class="chat-sender">${m.sender}:</span>
            <span class="chat-text">${m.text}</span>
          `;
          feed.appendChild(div);
        });
        lastChatCount = msgs.length;
        if (atBottom) feed.scrollTop = feed.scrollHeight;
    }
  }
  
  async function sendChat() {
    const textInput = document.getElementById('chat-text');
    const targetSelect = document.getElementById('chat-target');
    const text = textInput.value.trim();
    if(!text) return;
    textInput.value = '';
    
    await fetch('/api/send_chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text, target: targetSelect.value })
    });
    await refreshAll();
  }"""

content = content.replace(old_render_chat, new_render_chat)

with open('static/index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("UI patched successfully.")
