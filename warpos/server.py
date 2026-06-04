"""FastAPI server with auto-generated chat UI and WebSocket streaming."""

from __future__ import annotations

import json
import asyncio
from typing import TYPE_CHECKING

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

if TYPE_CHECKING:
    from warpos.agent import Agent


def create_app(agent: Agent) -> FastAPI:
    """Create a FastAPI app that serves the agent with a chat UI."""

    app = FastAPI(title=f"WarpOS — {agent.config.name}")

    @app.get("/", response_class=HTMLResponse)
    async def index():
        return _chat_ui_html(agent)

    @app.get("/api/info")
    async def info():
        return {
            "name": agent.config.name,
            "model": agent.config.model,
            "provider": agent.config.provider,
            "tools": list(agent._tool_defs.keys()),
            "memory": agent.config.memory,
        }

    @app.websocket("/ws")
    async def websocket_endpoint(ws: WebSocket):
        await ws.accept()
        session_id = "default"

        try:
            while True:
                data = await ws.receive_text()
                payload = json.loads(data)

                if payload.get("type") == "chat":
                    user_message = payload.get("message", "")
                    session_id = payload.get("session_id", session_id)

                    # Stream thinking indicator
                    await ws.send_text(json.dumps({"type": "thinking"}))

                    # Run agent (blocking — run in thread)
                    loop = asyncio.get_event_loop()
                    response = await loop.run_in_executor(
                        None, agent.run, user_message, session_id
                    )

                    # Send response
                    await ws.send_text(json.dumps({
                        "type": "response",
                        "content": response,
                    }))

                elif payload.get("type") == "reset":
                    agent.reset()
                    await ws.send_text(json.dumps({"type": "reset_ok"}))

        except WebSocketDisconnect:
            pass

    return app


def _chat_ui_html(agent: Agent) -> str:
    """Generate the chat UI HTML."""
    tool_names = ", ".join(agent._tool_defs.keys()) if agent._tool_defs else "none"

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{agent.config.name} — WarpOS</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600;700&family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
<style>
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  :root {{
    --bg: #0a0a0a; --bg-card: #111; --border: #1a1a1a; --text: #e0e0e0;
    --dim: #666; --muted: #444; --accent: #f5a623; --green: #00ff88;
  }}
  body {{
    background: var(--bg); color: var(--text);
    font-family: 'Inter', -apple-system, sans-serif;
    height: 100vh; display: flex; flex-direction: column;
  }}

  /* Header */
  .header {{
    padding: 12px 20px; border-bottom: 1px solid var(--border);
    display: flex; align-items: center; justify-content: space-between;
    background: rgba(10,10,10,0.9); backdrop-filter: blur(12px);
    flex-shrink: 0;
  }}
  .header-left {{ display: flex; align-items: center; gap: 12px; }}
  .header h1 {{
    font-family: 'JetBrains Mono', monospace; font-size: 0.85rem;
    font-weight: 700; letter-spacing: -0.5px;
  }}
  .header .badge {{
    font-family: 'JetBrains Mono', monospace; font-size: 0.6rem;
    padding: 3px 8px; border: 1px solid var(--border); color: var(--dim);
    letter-spacing: 1px; text-transform: uppercase;
  }}
  .header .info {{
    font-family: 'JetBrains Mono', monospace; font-size: 0.6rem;
    color: var(--muted); letter-spacing: 1px;
  }}
  .header button {{
    background: transparent; border: 1px solid var(--border); color: var(--dim);
    font-family: 'JetBrains Mono', monospace; font-size: 0.6rem;
    padding: 4px 10px; cursor: pointer; letter-spacing: 1px; text-transform: uppercase;
    transition: all 0.2s;
  }}
  .header button:hover {{ border-color: var(--text); color: var(--text); }}

  /* Messages */
  .messages {{
    flex: 1; overflow-y: auto; padding: 20px; display: flex;
    flex-direction: column; gap: 16px;
  }}
  .messages::-webkit-scrollbar {{ width: 4px; }}
  .messages::-webkit-scrollbar-thumb {{ background: #333; border-radius: 2px; }}

  .msg {{ max-width: 720px; width: 100%; margin: 0 auto; }}
  .msg-user {{ text-align: right; }}
  .msg-user .bubble {{
    display: inline-block; background: var(--accent); color: #000;
    padding: 10px 16px; border-radius: 4px 4px 0 4px;
    font-size: 0.9rem; line-height: 1.5; text-align: left;
    max-width: 85%; word-wrap: break-word;
  }}
  .msg-assistant .bubble {{
    background: var(--bg-card); border: 1px solid var(--border);
    padding: 12px 16px; border-radius: 4px 4px 4px 0;
    font-size: 0.9rem; line-height: 1.6; color: var(--text);
    max-width: 85%; word-wrap: break-word; white-space: pre-wrap;
  }}
  .msg-thinking .bubble {{
    color: var(--dim); font-style: italic; font-size: 0.85rem;
    padding: 8px 0; border: none; background: none;
  }}
  .msg-thinking .bubble::after {{
    content: ''; display: inline-block; width: 6px; height: 12px;
    background: var(--accent); margin-left: 4px; vertical-align: text-bottom;
    animation: blink 1s step-end infinite;
  }}
  @keyframes blink {{ 50% {{ opacity: 0; }} }}

  .msg-label {{
    font-family: 'JetBrains Mono', monospace; font-size: 0.55rem;
    color: var(--muted); letter-spacing: 2px; text-transform: uppercase;
    margin-bottom: 4px;
  }}
  .msg-user .msg-label {{ text-align: right; }}

  /* Welcome */
  .welcome {{
    text-align: center; padding: 40px 20px; max-width: 500px; margin: auto;
  }}
  .welcome h2 {{
    font-family: 'JetBrains Mono', monospace; font-size: 1.2rem;
    font-weight: 700; letter-spacing: -0.5px; margin-bottom: 8px;
  }}
  .welcome p {{ color: var(--dim); font-size: 0.85rem; line-height: 1.6; }}
  .welcome .tools {{
    margin-top: 16px; font-family: 'JetBrains Mono', monospace;
    font-size: 0.65rem; color: var(--muted); letter-spacing: 1px;
  }}

  /* Input */
  .input-area {{
    padding: 12px 20px; border-top: 1px solid var(--border);
    background: var(--bg-card); flex-shrink: 0;
  }}
  .input-row {{ display: flex; gap: 8px; max-width: 720px; margin: 0 auto; }}
  .input-row textarea {{
    flex: 1; background: var(--bg); border: 1px solid var(--border);
    color: var(--text); padding: 10px 14px; font-family: 'Inter', sans-serif;
    font-size: 0.9rem; resize: none; outline: none; border-radius: 4px;
    min-height: 42px; max-height: 120px; line-height: 1.5;
    transition: border-color 0.2s;
  }}
  .input-row textarea:focus {{ border-color: var(--accent); }}
  .input-row textarea::placeholder {{ color: var(--muted); }}
  .input-row button {{
    background: var(--accent); color: #000; border: none; padding: 10px 20px;
    font-family: 'JetBrains Mono', monospace; font-size: 0.7rem;
    font-weight: 600; letter-spacing: 1px; text-transform: uppercase;
    cursor: pointer; border-radius: 4px; transition: opacity 0.2s;
    align-self: flex-end;
  }}
  .input-row button:hover {{ opacity: 0.85; }}
  .input-row button:disabled {{ opacity: 0.4; cursor: not-allowed; }}
</style>
</head>
<body>

<div class="header">
  <div class="header-left">
    <h1>{agent.config.name}</h1>
    <span class="badge">{agent.config.model}</span>
  </div>
  <div>
    <span class="info">tools: {tool_names}</span>
    <button onclick="resetChat()">Reset</button>
  </div>
</div>

<div class="messages" id="messages">
  <div class="welcome">
    <h2>{agent.config.name}</h2>
    <p>{agent.config.instructions[:200]}</p>
    <div class="tools">TOOLS: {tool_names}</div>
  </div>
</div>

<div class="input-area">
  <div class="input-row">
    <textarea id="input" placeholder="Type a message..." rows="1"
      onkeydown="handleKey(event)"></textarea>
    <button id="sendBtn" onclick="send()">Send</button>
  </div>
</div>

<script>
  const ws = new WebSocket(`ws://${{location.host}}/ws`);
  const messages = document.getElementById('messages');
  const input = document.getElementById('input');
  const sendBtn = document.getElementById('sendBtn');
  let thinking = null;

  ws.onmessage = (e) => {{
    const data = JSON.parse(e.data);
    if (data.type === 'thinking') {{
      thinking = addMsg('assistant', '', true);
    }} else if (data.type === 'response') {{
      if (thinking) {{ thinking.remove(); thinking = null; }}
      addMsg('assistant', data.content);
      sendBtn.disabled = false;
      input.focus();
    }} else if (data.type === 'reset_ok') {{
      messages.innerHTML = '';
      addWelcome();
    }}
  }};

  ws.onclose = () => {{
    addMsg('assistant', '[Connection lost. Refresh to reconnect.]');
  }};

  function send() {{
    const text = input.value.trim();
    if (!text) return;
    addMsg('user', text);
    ws.send(JSON.stringify({{ type: 'chat', message: text }}));
    input.value = '';
    sendBtn.disabled = true;
    autoResize();
  }}

  function resetChat() {{
    ws.send(JSON.stringify({{ type: 'reset' }}));
  }}

  function handleKey(e) {{
    if (e.key === 'Enter' && !e.shiftKey) {{
      e.preventDefault();
      send();
    }}
  }}

  function addMsg(role, content, isThinking = false) {{
    // Remove welcome if present
    const welcome = messages.querySelector('.welcome');
    if (welcome) welcome.remove();

    const div = document.createElement('div');
    div.className = `msg msg-${{role}}`;
    const label = role === 'user' ? 'You' : '{agent.config.name}';
    div.innerHTML = `
      <div class="msg-label">${{label}}</div>
      <div class="bubble">${{isThinking ? 'Thinking' : escapeHtml(content)}}</div>
    `;
    messages.appendChild(div);
    messages.scrollTop = messages.scrollHeight;
    return div;
  }}

  function addWelcome() {{
    messages.innerHTML = `
      <div class="welcome">
        <h2>{agent.config.name}</h2>
        <p>{agent.config.instructions[:200]}</p>
        <div class="tools">TOOLS: {tool_names}</div>
      </div>
    `;
  }}

  function escapeHtml(str) {{
    return str.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
  }}

  // Auto-resize textarea
  input.addEventListener('input', autoResize);
  function autoResize() {{
    input.style.height = 'auto';
    input.style.height = Math.min(input.scrollHeight, 120) + 'px';
  }}

  input.focus();
</script>
</body>
</html>"""
