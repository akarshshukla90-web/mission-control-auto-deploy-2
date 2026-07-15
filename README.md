# Mission Control — OpenClaw Multi-Agent SaaS Dashboard

An executive control center and collaborative workspace for teams of autonomous OpenClaw agents. 

---

## 🚀 Product Concept & SaaS Potential

Mission Control compiles event streams, execution trajectories, and agent-to-agent dialogues into a unified **Kanban Board** and **Squad Chat**. Perfect for SaaS deployment where companies run autonomous marketing, coding, or support squads in background VPS containers.

### Core Value Proposition
1. **Hierarchical Visibility**: View what your Chief Orchestrator (`Jarvis`) is delegating to specialized workers (`Shuri`, `Friday`, `Wanda`, `Vision`).
2. **Interactive Human Steering (Human-in-the-Loop)**: Solve capture roadblocks, provide session cookie credentials, or whitelist targets directly from the UI to unblock worker agents instantly.
3. **Deliverables Persistence**: Task cards automatically link to their finished workspace files.

---

## 🛠️ Architecture

* **Frontend**: Responsive vanilla CSS + HTML5 SPA featuring a glassmorphic dashboard design, live agent diagnostic states, and custom dialogue bubbles.
* **Backend**: Lightweight, zero-dependency Python service (`server.py`) that binds directly to the local OpenClaw sessions SQLite database and `.jsonl` streams.
* **API Endpoints**:
  * `GET /api/board`: Extracts and aggregates tasks, statuses, comments, and deliverables.
  * `GET /api/chat`: Builds a chronological timeline of squad dialogues.
  * `POST /api/broadcast`: Sends strategic goals directly to the gateway execution queue.
  * `POST /api/unblock`: Inject overrides to resume blocked agent runs.

---

## ⚡ Setup & Run

1. Clone or copy this directory to your server or VPS.
2. Initialize and configure your local OpenClaw gateway using:
   ```bash
   openclaw gateway start
   ```
3. Run the dashboard server:
   ```bash
   python server.py
   ```
4. Access the premium dashboard at `http://localhost:8000`.
