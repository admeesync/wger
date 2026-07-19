from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from dependencies.auth import require_gym_staff
from dependencies.db import get_db
from models.admin_note import AdminNote
from models.member import Member
from models.user import User
from repository import admin_note_repo, member_repo
from schema.admin_note import AdminNoteCreate, AdminNoteOut

router = APIRouter(prefix='/members/{member_id}/notes', tags=['admin-notes'])


def _member_in_gym(db: Session, member_id: int, gym_id: int) -> Member:
    member = member_repo.get_by_id(db, member_id)
    if member is None or member.gym_id != gym_id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, 'Member not found')
    return member


def _to_out(note: AdminNote) -> AdminNoteOut:
    return AdminNoteOut(
        id=note.id, member_id=note.member_id, author_id=note.author_id,
        author_name=note.author.get_full_name() if note.author else None,
        note=note.note, created_at=note.created_at,
    )


@router.get('', response_model=list[AdminNoteOut])
def list_notes(member_id: int, db: Session = Depends(get_db), staff: User = Depends(require_gym_staff)):
    _member_in_gym(db, member_id, staff.gym_id)
    return [_to_out(n) for n in admin_note_repo.list_for_member(db, member_id)]


@router.post('', response_model=AdminNoteOut, status_code=status.HTTP_201_CREATED)
def add_note(
    member_id: int, data: AdminNoteCreate, db: Session = Depends(get_db), staff: User = Depends(require_gym_staff),
):
    _member_in_gym(db, member_id, staff.gym_id)
    note = AdminNote(member_id=member_id, author_id=staff.id, note=data.note, created_at=datetime.utcnow())
    return _to_out(admin_note_repo.create(db, note))


@router.delete('/{note_id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_note(
    member_id: int, note_id: int, db: Session = Depends(get_db), staff: User = Depends(require_gym_staff),
):
    _member_in_gym(db, member_id, staff.gym_id)
    note = admin_note_repo.get_by_id(db, note_id)
    if note is None or note.member_id != member_id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, 'Note not found')
    admin_note_repo.delete(db, note)
