# JobPilot - AI Job Assistant

An AI-powered application to orchestrate your job functions: track projects, manage teams, delegate tasks, and let AI analyze your progress.

## Features

- **Project & Goal Tracking** - Full CRUD for projects, goals, milestones, and tasks with status tracking
- **Team Management** - Add team members, assign tasks, track workload and availability
- **AI-Powered Planning** - Claude AI analyzes your projects and suggests next steps, identifies risks, and recommends task delegation
- **Email Integration** - Sync unread emails and automatically extract action items using AI
- **WhatsApp Integration** - Webhook-based integration to receive messages and extract action items
- **Inbox** - Central place to review all AI-extracted action items from emails, WhatsApp, and manual input
- **Web Dashboard** - Clean HTMX-powered UI with real-time AI insights

## Quick Start

```bash
# 1. Navigate to the app directory
cd jobpilot

# 2. Create a virtual environment
python -m venv .venv
source .venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY

# 5. Run the application
uvicorn app.main:app --reload

# 6. Open http://localhost:8000 in your browser
```

## API Endpoints

### Projects
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/projects` | List all projects |
| POST | `/api/projects` | Create a project |
| GET | `/api/projects/{id}` | Get project details |
| PUT | `/api/projects/{id}` | Update a project |
| DELETE | `/api/projects/{id}` | Delete a project |

### Tasks
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/tasks` | List tasks (filter by project, status, assignee) |
| POST | `/api/tasks` | Create a task |
| PUT | `/api/tasks/{id}` | Update a task |
| POST | `/api/tasks/{id}/assign` | Assign task to team member |

### Team
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/team` | List team members |
| POST | `/api/team` | Add a team member |
| GET | `/api/team/{id}/workload` | View member workload |

### AI
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/ai/plan/{project_id}` | AI project analysis |
| POST | `/api/ai/delegate/{project_id}` | AI delegation suggestions |
| POST | `/api/ai/extract-actions` | Extract actions from text |
| GET | `/api/ai/dashboard-summary` | AI dashboard summary |

### Integrations
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/email/sync` | Sync emails and extract actions |
| GET | `/api/email/action-items` | List extracted action items |
| POST | `/api/whatsapp/webhook` | WhatsApp incoming webhook |

## Running Tests

```bash
cd jobpilot
pip install -r requirements.txt
pytest tests/ -v
```

## Tech Stack

- **Backend**: FastAPI + SQLAlchemy + SQLite
- **AI**: Claude (Anthropic SDK)
- **Frontend**: Jinja2 + HTMX + Pico CSS
- **Email**: IMAP (imaplib)
- **WhatsApp**: Meta Business API (webhook-based)

## Configuration

All settings are managed via environment variables (`.env` file):

| Variable | Required | Description |
|----------|----------|-------------|
| `ANTHROPIC_API_KEY` | Yes (for AI) | Your Anthropic API key |
| `DATABASE_URL` | No | Database URL (default: SQLite) |
| `IMAP_SERVER` | No | IMAP server for email sync |
| `EMAIL_ADDRESS` | No | Email address for sync |
| `EMAIL_PASSWORD` | No | Email password |
| `WHATSAPP_API_TOKEN` | No | WhatsApp Business API token |
