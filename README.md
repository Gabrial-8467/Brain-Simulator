# Brain Simulator

Brain Simulator is a developmental cognitive agent prototype.
It is designed to accumulate experiences over time and update internal state through:

- neurochemical dynamics and receptor sensitivity
- autobiographical memory and Hopfield attractor replay
- identity/development updates
- attention-based thought selection (Global Workspace Theory)
- reflection and narrative updates
- striatal reinforcement learning and look-ahead strategic planning
- sleep/wake cycle homeostasis (SWS and REM)
- environmental attachment, goal pursuit, and curiosity drives

## What Is Implemented

- **Expanded Neurochemistry**: 9 neurochemicals (Dopamine, Cortisol, Oxytocin, Serotonin, Norepinephrine, Adrenaline, Acetylcholine, Melatonin, and Endorphins) with matrix interactions, homeostatic pulls, and receptor saturation dynamics.
- **Sleep/Wake Cycles**: Fatigue-driven sleep cycles modeling Slow Wave Sleep (offline striatal Q-value updates + synaptic pruning) and REM sleep (schema consolidation + dream thoughts), governed by Process S and Process C.
- **Salience Network (DMN vs TPN)**: Gated by Norepinephrine; Task Positive Network focuses attention outward, while Default Mode Network boosts mind-wandering and Hopfield attractor-based memory replay.
- **Hippocampal Replay & Hopfield CA3**: A 9x9 Hebbian attractor matrix that stores binarized chemical-identity states and recalls them during dreaming and mind-wandering.
- **Striatal Reinforcement Learning**: Maps 6 discrete mood states to action Q-values, updated via Reward Prediction Errors (RPE) triggering phasic dopamine bursts or dips.
- **Strategic Planner**: Depth=2 recursive look-ahead projecting state transitions onto lightweight state dictionaries, avoiding deep-copy bottlenecks.
- **Decoupled Background Drives**:
  - `AttachmentSystem`: Tracks source-specific trust to buffer cortisol stress responses and bias prosocial actions.
  - `CuriosityEngine`: Logs concept frequency to dynamically calculate curiosity values and boost workspace novelty.
  - `GoalSystem`: Tracks Active Goals (Safety, Mastery, Social Connection) to scale workspace thought relevance.
- **Speech Regulation**: Modulates sentence length, complexity, and empathy prefixing based on cortisol, oxytocin, and developmental stage.
- **Dynamic Identity**: Tracks competence, social_value, resilience, and intelligence based on evidence accumulation.
- **Developmental Stage Transitions**: Monotonic maturity progression (Baby -> Child -> Teen -> Adult) slowed down by chronic stress exposure.
- **Consciousness Score**: Focus stability streaks, narrative complexity, and development levels modulate risk tolerance.
- **Autobiographical Memory**: Episodic event logger with memory-thought proposals.
- **Belief Engine**: Computes statistical schemas (e.g., criticism, failure, support) over a sliding window of events to appraisal-modulate incoming perceptions.
- **Narrative Engine**: Generates continuous verbal self-narratives based on developmental milestones and chemical averages.
- **Perception Pipelines**:
  - `brain.perceive(event)` for structured life events.
  - `brain.observe_perception(modality, content, source)` for text modality input.
  - `brain.receive_visual_signal(signal)` for structured visual signals.
  - `brain.receive_hearing_signal(signal)` for structured hearing signals.

## Current CLI

`main.py` supports:

- `--mode simulate` (default)
- `--mode live`
- `--cycles <int>`
- `--deterministic`

Examples:

```bash
python main.py --mode simulate --cycles 100
python main.py --mode live
python main.py --mode simulate --cycles 500 --deterministic
```

## How Simulation Runs

In simulate mode:

1. `Simulator` generates one synthetic developmental event each cycle.
2. The event is sent to `brain.perceive(...)`.
3. Optional scenario events (from `simulation/scenarios.py`) are injected.
4. Brain runs `tick()`, selecting the winning thought via the Global Workspace.
5. The winning thought gates the `DecisionEngine` and the look-ahead `StrategicPlanner` to select an action, apply feedback, calculate regret/wisdom, and update RL Q-values.

## Aashu Assistant Integration

The repository includes a physical assistant interface named **Aashu** (located in the [aashu](file:///home/gabrialdeora/D-drive/Brain-Simulator/aashu) folder). Aashu acts as the physical "body" (handling audio/visual inputs and system action execution), while the Virtual Brain acts as the cognitive "mind".

### How Aashu and the Virtual Brain Connect

Aashu runs as a client and connects to the Virtual Brain server (running on `api_server.py`) using the REST APIs defined in [brain_client.py](file:///home/gabrialdeora/D-drive/Brain-Simulator/aashu/brain_client.py).

1. **Sensory Uplink:** 
   - **Hearing (`ears.py`):** Captures voice inputs, transcribes them, and sends them to the brain's hearing pipeline (`/perceive/hearing`).
   - **Vision (`eyes.py`):** Uses OpenCV camera streams to recognize objects/motion, posting them to the brain's visual pipeline (`/perceive/visual`).
   - **Somatic Alerts (`agent.py`):** Runs a background hardware monitor thread to ingest CPU and battery stress signals into the brain's raw perception feed.
2. **Heartbeat Ticking:** The background autonomous scheduler (`scheduler.py`) triggers a cognitive tick (`/tick`) in the brain every 10 seconds.
3. **Command Downlink (Actuators):** 
   - On startup, Aashu registers its local system tools (defined in [actuators.py](file:///home/gabrialdeora/D-drive/Brain-Simulator/aashu/actuators.py)) with the Virtual Brain.
   - When the brain ticks and makes a strategic decision to act, it returns a `tool_call` command block in the API response.
   - Aashu catches this command, announces it, and executes the physical tool locally (e.g., searching the web, adjusting system volume, playing music, taking screenshots, or modifying file contents).
   - Once executed, Aashu sends the command outcome back to the brain as an experience perception to complete the cognitive loop.
4. **Speech & Mood Alignment:** Aashu uses a local Ollama LLM to synthesize speech responses. The system prompt is dynamically updated with the brain's current focus, emotional mood, and neurochemical personality directives. The response is regulated through the brain's `/regulate_speech` endpoint before being spoken out loud.

## Brain-Owned App Generation & Debugging

The Virtual Brain also acts as a **deterministic application generator and debugger**. No external LLM is involved: output is produced from declarative templates and static analysis, so identical inputs always produce identical apps.

### Full-Stack Generator (`build_fullstack`)

Gated on the brain having learned Python. Supported kinds:

| Kind | Mode | Example |
| :--- | :--- | :--- |
| `food_delivery` | cart + checkout | ZomatoClone |
| `ecommerce` | cart + checkout | ShopNow |
| `booking` | cart + checkout (services) | BookIt |
| `task_tracker` | private collection | TodoPro |
| `chat` | collection + real-time SSE | Chatter |
| `blog` | public collection (read-only to guests) | DevBlog |
| `notes` | private collection | QuickNotes |
| `fitness` | private collection | FitLog |

Kind aliases normalize user phrasing (`zomato` -> `food_delivery`, `cms` -> `blog`, `todo` -> `task_tracker`, ...). Each project is written to `generated_apps/<slug>/` and contains:

- `backend/` — the REST API. Choose any of **four frameworks** via `backend=`:
  - `flask` (default) — `app.py`
  - `django` — `manage.py` + `config/` project with method-dispatch views, `JSON` 404 for unknown `/api/*`
  - `express` — `server.js`
  - `fastify` — `server.js`
  All share one API contract: pbkdf2-hashed session auth (`/api/auth/register|login|logout|me`), search + pagination (`?q=`, `?limit=`, `?offset=`), simulated payments, Server-Sent Events for chat, JSON 404s, and the SPA fallback route.
- `backend/schema.sql` — the SQL schema the app self-bootstraps (SQLite by default, Postgres-compatible with `SERIAL PRIMARY KEY`).
- `backend/requirements.txt` (Python) or `backend/package.json` (Node) + `backend/Dockerfile` — gunicorn or node multi-worker deployment.
- `docker-compose.yml` — web on `:8000` (Python) / `:3000` (Node) plus an optional **PostgreSQL 16 service**; the app auto-detects `DATABASE_URL` (Postgres) vs `DATABASE_PATH` (SQLite, zero-config dev fallback).
- `frontend/` — choose the frontend via `frontend=`:
  - `single` (default) — `index.html` single-page UI served by the backend
  - `react` — a full **React + Vite SPA** (`src/` + `package.json` + `vite.config.js`); the backend serves `dist/` after `npm run build`
- `README.md` — dev and production-ish run steps for that specific app.

```python
ok, msg = brain.build_fullstack("BookIt", kind="booking", backend="django", frontend="react")
```

### Deterministic Debugger (`debug_app`)

Scans a generated project (framework-aware: it locates `app.py`, `manage.py`, or `server.js`) and reports a structured bug list (severity + location + message):

- leftover template tokens (`{{...}}`, `%TOKEN%`)
- syntax errors (Python `py_compile`, Node `node --check`)
- backend-referenced tables missing from the schema (including collection/catalog table constants)
- seed inserts into unknown tables
- frontend `api()` / `EventSource()` calls with no matching backend route (method-aware, balanced-paren parsing)
- missing DB bootstrap (`_init_db`)

With `fix=True`, it repairs in place when the fix is unambiguous: rename a single unused table to the single missing table (e.g. `bookings` -> `orders`), insert a missing `_init_db()` call, or rebuild a brain-generated app from its template (restricted to non-Django backends).

```python
ok, msg = brain.build_fullstack("BookIt", kind="booking")
report = brain.debug_app("BookIt")          # list bugs
report = brain.debug_app("BookIt", fix=True)  # repair in place
```

Aashu reaches the same features through the planner and actuators: *"build a food delivery app like zomato"*, *"debug the BookIt app"*, *"fix the bugs in DevBlog"*.

### REST Endpoints

- `POST /brain/build_website`, `/brain/build_angularapp`, `/brain/build_vueapp`, `/brain/build_node_server`, `/brain/build_sql_schema`, `/brain/build_fullstack`, `/brain/build_cli`
- `POST /brain/debug_app` — body `{"name": "...", "fix": false}`
- `GET /brain/apps` — list projects the brain has generated

## Programmatic Perception APIs

You can feed external sensors without changing the core loop.

### Event-style input

```python
brain.perceive({
    "content": "You are praised for trying.",
    "category": "praise",
    "valence": 0.8,
    "intensity": 0.7,
    "source": "simulated",
    "timestamp": 0.0,
})
```

### Structured vision input

```python
brain.receive_visual_signal({
    "objects": ["person", "bottle"],
    "attributes": {"person": ["red"]},
    "relations": [{"from": "person", "rel": "near", "to": "bottle"}],
    "motion_level": 0.4,
    "confidence": 0.9,
    "source": "camera_pipeline",
    "timestamp": 0.0,
})
```

### Structured hearing input

```python
brain.receive_hearing_signal({
    "transcript": "Good job, keep trying",
    "speaker_type": "caregiver",
    "sentiment": 0.7,
    "prosody_intensity": 0.6,
    "keywords": ["praise", "support"],
    "source": "audio_pipeline",
    "timestamp": 0.0,
})
```

## Output State Includes

`brain.get_state()` returns:

- chemical values (9 neurochemicals)
- receptor sensitivities
- identity snapshot (`identity_*`)
- development snapshot (`development_*`)
- recent perceptions and learned concepts
- active beliefs and goals
- social attachments
- wisdom and self-narrative
- consciousness score and network mode

## Project Notes

- The decision engine is attached directly in `main.py` to enable active action selection, RL learning, and planning.
- This repository is a research/development prototype, not a production chatbot stack.

## Free Cloud Deployment (Render.com)

You can deploy the Virtual Brain server to **Render (render.com)** for free as a Web Service:

### Step 1: Create Web Service
1. Sign in to your [Render Dashboard](https://dashboard.render.com/).
2. Click **New** -> **Web Service**.
3. Connect your GitHub/GitLab repository.

### Step 2: Configure Settings
* **Name:** `virtual-brain-server`
* **Region:** (Select the closest one to you)
* **Branch:** `main`
* **Runtime:** `Docker` (Render will automatically detect the `Dockerfile` at the root)
* **Instance Type:** `Free`

### Step 3: Add Environment Variables
Click **Advanced** -> **Add Environment Variable**:
* `PORT` = `10000` (or leave empty; Render will configure this automatically)
* `BRAIN_DATA_DIR` = `/tmp` (Free tier has ephemeral storage; using `/tmp` avoids file permission issues)
* `BRAIN_API_KEY` = `your-secure-custom-key` (Any custom password to secure your endpoints; if configured, requests must supply the `X-API-Key` header)

### Step 4: Deploy and Connect Client
1. Click **Create Web Service**.
2. Once deployed, copy your public URL (e.g. `https://virtual-brain-server.onrender.com`).
3. Set your public URL and API key in the client's `config.py` (either in the local package or `Aashu-Client` outside the repo):
   ```python
   BRAIN_API_URL = "https://virtual-brain-server.onrender.com"
   BRAIN_API_KEY = "your-secure-custom-key"
   ```
4. Start your client: `python run_client.py`.

