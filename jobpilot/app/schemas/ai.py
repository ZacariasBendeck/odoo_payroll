from pydantic import BaseModel


class AIAnalysisResponse(BaseModel):
    project_id: int
    summary: str
    next_steps: list[str]
    risks: list[str]
    priority_suggestions: list[str]


class AIDelegationResponse(BaseModel):
    project_id: int
    recommendations: list["DelegationRecommendation"]


class DelegationRecommendation(BaseModel):
    task_id: int
    task_title: str
    recommended_member_id: int
    recommended_member_name: str
    reason: str


class AIExtractActionsRequest(BaseModel):
    text: str
    source: str = "manual"  # email | whatsapp | manual


class AIExtractActionsResponse(BaseModel):
    actions: list["ExtractedAction"]


class ExtractedAction(BaseModel):
    action: str
    suggested_project: str | None = None
    priority: str = "medium"


class AIDashboardSummary(BaseModel):
    summary: str
    top_priorities: list[str]
    blockers: list[str]
