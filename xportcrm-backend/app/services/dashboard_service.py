import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.lead import Lead
from app.models.opportunity import Opportunity
from app.models.quotation import Quotation
from app.models.activity import Activity
from app.models.account import Account


def _period_to_dates(period: str) -> tuple[datetime, datetime]:
    """Converts a period string (XPO-58 section 4) into a date range."""
    now = datetime.now(timezone.utc)
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)

    if period == "today":
        return today_start, now
    elif period == "yesterday":
        return today_start - timedelta(days=1), today_start
    elif period == "last_7_days":
        return today_start - timedelta(days=7), now
    elif period == "last_30_days":
        return today_start - timedelta(days=30), now
    elif period == "this_month":
        return today_start.replace(day=1), now
    elif period == "last_month":
        first_of_this_month = today_start.replace(day=1)
        last_month_end = first_of_this_month - timedelta(seconds=1)
        last_month_start = last_month_end.replace(day=1)
        return last_month_start, last_month_end
    else:
        # default: last 30 days
        return today_start - timedelta(days=30), now


def _scope_filter(model, data_scope: str, current_user_id: uuid.UUID):
    """Returns a filter condition based on data_scope (XPO-41), same
    logic as list_leads/list_opportunities - 'Own' restricts to
    records assigned to/created by the current user."""
    if data_scope == "Own":
        return (model.assigned_to_id == current_user_id) | (model.created_by == current_user_id)
    return True  # All/Team/Branch - no restriction for now (see earlier note)


async def get_dashboard(
    db: AsyncSession, tenant_id: uuid.UUID, current_user_id: uuid.UUID, data_scope: str, period: str = "last_30_days"
) -> dict:
    period_start, period_end = _period_to_dates(period)
    prev_length = period_end - period_start
    prev_start, prev_end = period_start - prev_length, period_start

    # --- KPI: Leads ---
    current_leads = await db.execute(
        select(func.count()).select_from(Lead).where(
            Lead.tenant_id == tenant_id, Lead.is_deleted == False,
            Lead.created_at >= period_start, Lead.created_at <= period_end,
            _scope_filter(Lead, data_scope, current_user_id),
        )
    )
    current_leads_count = current_leads.scalar_one()

    prev_leads = await db.execute(
        select(func.count()).select_from(Lead).where(
            Lead.tenant_id == tenant_id, Lead.is_deleted == False,
            Lead.created_at >= prev_start, Lead.created_at < prev_end,
            _scope_filter(Lead, data_scope, current_user_id),
        )
    )
    prev_leads_count = prev_leads.scalar_one()
    leads_growth = ((current_leads_count - prev_leads_count) / prev_leads_count * 100) if prev_leads_count else None

    # --- KPI: Opportunities ---
    current_opps = await db.execute(
        select(func.count()).select_from(Opportunity).where(
            Opportunity.tenant_id == tenant_id, Opportunity.is_deleted == False,
            Opportunity.created_at >= period_start, Opportunity.created_at <= period_end,
            _scope_filter(Opportunity, data_scope, current_user_id),
        )
    )
    current_opps_count = current_opps.scalar_one()

    prev_opps = await db.execute(
        select(func.count()).select_from(Opportunity).where(
            Opportunity.tenant_id == tenant_id, Opportunity.is_deleted == False,
            Opportunity.created_at >= prev_start, Opportunity.created_at < prev_end,
            _scope_filter(Opportunity, data_scope, current_user_id),
        )
    )
    prev_opps_count = prev_opps.scalar_one()
    opps_growth = ((current_opps_count - prev_opps_count) / prev_opps_count * 100) if prev_opps_count else None

    # --- KPI: Quotations ---
    current_quotes = await db.execute(
        select(func.count()).select_from(Quotation).where(
            Quotation.tenant_id == tenant_id, Quotation.is_deleted == False,
            Quotation.created_at >= period_start, Quotation.created_at <= period_end,
        )
    )
    current_quotes_count = current_quotes.scalar_one()

    prev_quotes = await db.execute(
        select(func.count()).select_from(Quotation).where(
            Quotation.tenant_id == tenant_id, Quotation.is_deleted == False,
            Quotation.created_at >= prev_start, Quotation.created_at < prev_end,
        )
    )
    prev_quotes_count = prev_quotes.scalar_one()
    quotes_growth = ((current_quotes_count - prev_quotes_count) / prev_quotes_count * 100) if prev_quotes_count else None

    # --- KPI: Revenue (from Closed Won opportunities in period) ---
    current_revenue_result = await db.execute(
        select(func.coalesce(func.sum(Opportunity.estimated_amount), 0)).where(
            Opportunity.tenant_id == tenant_id, Opportunity.is_deleted == False,
            Opportunity.stage == "Closed Won",
            Opportunity.created_at >= period_start, Opportunity.created_at <= period_end,
        )
    )
    current_revenue = float(current_revenue_result.scalar_one())

    prev_revenue_result = await db.execute(
        select(func.coalesce(func.sum(Opportunity.estimated_amount), 0)).where(
            Opportunity.tenant_id == tenant_id, Opportunity.is_deleted == False,
            Opportunity.stage == "Closed Won",
            Opportunity.created_at >= prev_start, Opportunity.created_at < prev_end,
        )
    )
    prev_revenue = float(prev_revenue_result.scalar_one())
    revenue_growth = ((current_revenue - prev_revenue) / prev_revenue * 100) if prev_revenue else None

    # --- Sales Pipeline (grouped by stage) ---
    pipeline_result = await db.execute(
        select(Opportunity.stage, func.count(), func.coalesce(func.sum(Opportunity.estimated_amount), 0))
        .where(Opportunity.tenant_id == tenant_id, Opportunity.is_deleted == False)
        .group_by(Opportunity.stage)
    )
    pipeline = [
        {"stage": stage, "count": count, "value": float(value)}
        for stage, count, value in pipeline_result.all()
    ]

    # --- Revenue by Service (Closed Won grouped by opportunity_type) ---
    revenue_by_service_result = await db.execute(
        select(Opportunity.opportunity_type, func.coalesce(func.sum(Opportunity.estimated_amount), 0))
        .where(Opportunity.tenant_id == tenant_id, Opportunity.is_deleted == False, Opportunity.stage == "Closed Won")
        .group_by(Opportunity.opportunity_type)
    )
    service_rows = revenue_by_service_result.all()
    total_service_revenue = sum(float(rev) for _, rev in service_rows) or 1  # avoid div by zero
    revenue_by_service = [
        {"service_type": service, "revenue": float(rev), "percentage": round(float(rev) / total_service_revenue * 100, 1)}
        for service, rev in service_rows
    ]

    # --- Recent Activities (latest 10) ---
    recent_activities_result = await db.execute(
        select(Activity)
        .where(Activity.tenant_id == tenant_id, Activity.is_deleted == False)
        .order_by(Activity.created_at.desc())
        .limit(10)
    )
    recent_activities = [
        {
            "id": a.id, "subject": a.subject, "activity_type": a.activity_type,
            "status": a.status, "related_to": a.related_to, "updated_at": a.modified_at or a.created_at,
        }
        for a in recent_activities_result.scalars().all()
    ]

    # --- Upcoming Tasks (next 10 by due_date, not completed) ---
    upcoming_tasks_result = await db.execute(
        select(Activity)
        .where(
            Activity.tenant_id == tenant_id, Activity.is_deleted == False,
            Activity.status == "Pending", Activity.due_date.isnot(None),
        )
        .order_by(Activity.due_date.asc())
        .limit(10)
    )
    upcoming_tasks = [
        {"id": a.id, "subject": a.subject, "due_date": a.due_date, "priority": a.priority}
        for a in upcoming_tasks_result.scalars().all()
    ]

    # --- Top Accounts (by Closed Won revenue) ---
    top_accounts_result = await db.execute(
        select(Account.id, Account.name, func.coalesce(func.sum(Opportunity.estimated_amount), 0))
        .join(Opportunity, Opportunity.account_id == Account.id)
        .where(Account.tenant_id == tenant_id, Opportunity.stage == "Closed Won", Opportunity.is_deleted == False)
        .group_by(Account.id, Account.name)
        .order_by(func.sum(Opportunity.estimated_amount).desc())
        .limit(5)
    )
    top_accounts = [
        {"account_id": aid, "account_name": name, "revenue": float(rev)}
        for aid, name, rev in top_accounts_result.all()
    ]

    return {
        "total_leads": {"count": current_leads_count, "growth_pct": round(leads_growth, 1) if leads_growth is not None else None},
        "total_opportunities": {"count": current_opps_count, "growth_pct": round(opps_growth, 1) if opps_growth is not None else None},
        "total_quotations": {"count": current_quotes_count, "growth_pct": round(quotes_growth, 1) if quotes_growth is not None else None},
        "revenue": {"amount": current_revenue, "growth_pct": round(revenue_growth, 1) if revenue_growth is not None else None},
        "pipeline": pipeline,
        "revenue_by_service": revenue_by_service,
        "recent_activities": recent_activities,
        "upcoming_tasks": upcoming_tasks,
        "top_accounts": top_accounts,
    }