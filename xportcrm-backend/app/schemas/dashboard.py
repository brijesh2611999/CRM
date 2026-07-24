import uuid
from datetime import datetime
from pydantic import BaseModel


class KPICard(BaseModel):
    count: int
    growth_pct: float | None = None


class RevenueKPI(BaseModel):
    amount: float
    growth_pct: float | None = None


class PipelineStage(BaseModel):
    stage: str
    count: int
    value: float


class RevenueByService(BaseModel):
    service_type: str
    revenue: float
    percentage: float


class RecentActivity(BaseModel):
    id: uuid.UUID
    subject: str
    activity_type: str
    status: str
    related_to: str | None = None
    updated_at: datetime | None = None


class UpcomingTask(BaseModel):
    id: uuid.UUID
    subject: str
    due_date: datetime | None = None
    priority: str


class TopAccount(BaseModel):
    account_id: uuid.UUID
    account_name: str
    revenue: float


class DashboardResponse(BaseModel):
    total_leads: KPICard
    total_opportunities: KPICard
    total_quotations: KPICard
    revenue: RevenueKPI
    pipeline: list[PipelineStage]
    revenue_by_service: list[RevenueByService]
    recent_activities: list[RecentActivity]
    upcoming_tasks: list[UpcomingTask]
    top_accounts: list[TopAccount]