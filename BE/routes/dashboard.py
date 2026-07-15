import calendar
from datetime import date, timedelta

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from dependencies.auth import require_gym_staff
from dependencies.db import get_db
from models.user import User
from repository import attendance_repo, contract_repo, user_repo
from schema.user import DashboardSummary
from service.gym_service import contract_status

router = APIRouter(prefix='/dashboard', tags=['dashboard'])


@router.get('/summary', response_model=DashboardSummary)
def summary(db: Session = Depends(get_db), staff: User = Depends(require_gym_staff)):
    today = date.today()
    members = user_repo.list_by_gym(db, staff.gym_id)
    contracts = contract_repo.latest_for_members(db, [m.id for m in members])
    all_contracts = contract_repo.list_for_gym(db, staff.gym_id)
    attendance = attendance_repo.list_for_gym(db, staff.gym_id, limit=2000)

    expiring_soon = sum(1 for m in members if contract_status(contracts.get(m.id), today) == 'expiring')
    today_attendance = sum(1 for a in attendance if a.date == today)
    new_members_this_month = sum(
        1 for m in members if m.date_joined.year == today.year and m.date_joined.month == today.month
    )
    monthly_revenue = sum(
        c.amount for c in all_contracts if c.date_start.year == today.year and c.date_start.month == today.month
    )
    birthday_count = sum(
        1 for m in members if m.birthdate and (m.birthdate.month, m.birthdate.day) == (today.month, today.day)
    )

    week_labels, week_data = [], []
    for i in range(6, -1, -1):
        day = today - timedelta(days=i)
        week_labels.append(day.strftime('%a'))
        week_data.append(sum(1 for a in attendance if a.date == day))

    month_labels, month_data = [], []
    for i in range(5, -1, -1):
        year, month = today.year, today.month - i
        while month <= 0:
            month += 12
            year -= 1
        month_labels.append(calendar.month_abbr[month])
        month_data.append(
            float(sum(c.amount for c in all_contracts if c.date_start.year == year and c.date_start.month == month))
        )

    recent_members = user_repo.recent_by_gym(db, staff.gym_id, limit=5)
    recent_attendance = sorted(attendance, key=lambda a: (a.date, a.time_in or ''), reverse=True)[:5]
    member_by_id = {m.id: m for m in members}

    return DashboardSummary(
        total_members=len(members),
        today_attendance=today_attendance,
        expiring_soon=expiring_soon,
        monthly_revenue=str(monthly_revenue),
        new_members_this_month=new_members_this_month,
        birthday_count=birthday_count,
        week_labels=week_labels,
        week_data=week_data,
        month_labels=month_labels,
        month_data=month_data,
        recent_members=recent_members,
        recent_attendance=[
            {
                'member_username': member_by_id[a.member_id].username if a.member_id in member_by_id else '?',
                'date': a.date.isoformat(),
                'time_in': a.time_in.isoformat() if a.time_in else None,
            }
            for a in recent_attendance
        ],
    )
