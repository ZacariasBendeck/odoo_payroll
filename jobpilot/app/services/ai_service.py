import json
import logging

import anthropic

from app.config import settings

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are JobPilot AI, an intelligent assistant that helps manage projects,
tasks, and teams. You provide actionable, specific advice based on the project data provided.
Always respond with valid JSON matching the requested format."""


def _get_client() -> anthropic.Anthropic:
    return anthropic.Anthropic(api_key=settings.anthropic_api_key)


def analyze_project(project_data: dict) -> dict:
    """Analyze a project and suggest next steps, risks, and priorities."""
    client = _get_client()

    prompt = f"""Analyze this project and provide strategic guidance.

PROJECT DATA:
{json.dumps(project_data, indent=2, default=str)}

Respond with this exact JSON structure:
{{
    "summary": "Brief assessment of project health and progress",
    "next_steps": ["Step 1", "Step 2", "Step 3"],
    "risks": ["Risk 1", "Risk 2"],
    "priority_suggestions": ["Suggestion 1", "Suggestion 2"]
}}"""

    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1024,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": prompt}],
    )

    try:
        return json.loads(message.content[0].text)
    except (json.JSONDecodeError, IndexError):
        return {
            "summary": message.content[0].text if message.content else "Analysis unavailable",
            "next_steps": [],
            "risks": [],
            "priority_suggestions": [],
        }


def recommend_delegation(tasks: list[dict], team: list[dict]) -> list[dict]:
    """Recommend task assignments based on team skills and workload."""
    client = _get_client()

    prompt = f"""Match unassigned tasks to the best team members based on their skills,
role, and current workload.

UNASSIGNED TASKS:
{json.dumps(tasks, indent=2, default=str)}

TEAM MEMBERS:
{json.dumps(team, indent=2, default=str)}

Respond with this exact JSON structure:
{{
    "recommendations": [
        {{
            "task_id": 1,
            "task_title": "Task name",
            "recommended_member_id": 1,
            "recommended_member_name": "Member name",
            "reason": "Why this member is the best fit"
        }}
    ]
}}"""

    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1024,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": prompt}],
    )

    try:
        result = json.loads(message.content[0].text)
        return result.get("recommendations", [])
    except (json.JSONDecodeError, IndexError):
        return []


def extract_action_items(text: str, projects: list[dict]) -> list[dict]:
    """Extract actionable items from text (email, message, etc.)."""
    client = _get_client()

    prompt = f"""Extract action items from this text and match them to existing projects if possible.

TEXT:
{text}

EXISTING PROJECTS:
{json.dumps(projects, indent=2, default=str)}

Respond with this exact JSON structure:
{{
    "actions": [
        {{
            "action": "Description of the action item",
            "suggested_project": "Project name if it matches, or null",
            "priority": "low|medium|high|critical"
        }}
    ]
}}"""

    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1024,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": prompt}],
    )

    try:
        result = json.loads(message.content[0].text)
        return result.get("actions", [])
    except (json.JSONDecodeError, IndexError):
        return []


def generate_dashboard_summary(projects: list[dict]) -> dict:
    """Generate an overall summary of all active projects."""
    client = _get_client()

    prompt = f"""Provide a concise executive summary of the current state of all projects.

ACTIVE PROJECTS:
{json.dumps(projects, indent=2, default=str)}

Respond with this exact JSON structure:
{{
    "summary": "Overall status paragraph",
    "top_priorities": ["Priority 1", "Priority 2", "Priority 3"],
    "blockers": ["Blocker 1 if any"]
}}"""

    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1024,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": prompt}],
    )

    try:
        return json.loads(message.content[0].text)
    except (json.JSONDecodeError, IndexError):
        return {
            "summary": "Unable to generate summary.",
            "top_priorities": [],
            "blockers": [],
        }
