from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import or_, func
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.database.models import Ticket, TicketMessage, TicketEvent, User
from app.database.schemas import TicketCreate, TicketUpdate, MessageCreate, TicketOut
from app.services.ai_engine import analyze_ticket
from datetime import datetime, timezone

router=APIRouter(prefix="/tickets", tags=["Tickets"])

def get_ticket(ticket_id, db):
    t=db.get(Ticket,ticket_id)
    if not t: raise HTTPException(404,"Ticket not found")
    return t

@router.post("", response_model=TicketOut)
def create_ticket(payload:TicketCreate, db:Session=Depends(get_db)):
    t=Ticket(customer_name=payload.customer_name,customer_email=payload.customer_email,subject=payload.subject,description=payload.description,source=payload.source,priority=payload.priority or "medium")
    db.add(t); db.flush(); db.add(TicketEvent(ticket_id=t.id,event_type="CREATED",message="Ticket created",actor="system"))
    if payload.auto_analyze: analyze_ticket(t,db)
    db.commit(); db.refresh(t); return t

@router.get("", response_model=list[TicketOut])
def list_tickets(status:str|None=None,priority:str|None=None,category:str|None=None,search:str|None=None,limit:int=Query(50,le=200),offset:int=0,db:Session=Depends(get_db)):
    q=db.query(Ticket)
    if status:q=q.filter(Ticket.status==status)
    if priority:q=q.filter(Ticket.priority==priority)
    if category:q=q.filter(Ticket.category==category)
    if search:q=q.filter(or_(Ticket.subject.ilike(f"%{search}%"),Ticket.description.ilike(f"%{search}%"),Ticket.customer_name.ilike(f"%{search}%")))
    return q.order_by(Ticket.created_at.desc()).offset(offset).limit(limit).all()

@router.get("/stats/summary")
def stats(db:Session=Depends(get_db)):
    total=db.query(func.count(Ticket.id)).scalar() or 0
    def count(field,val): return db.query(func.count(Ticket.id)).filter(field==val).scalar() or 0
    return {"total":total,"open":count(Ticket.status,"open"),"in_progress":count(Ticket.status,"in_progress"),"resolved":count(Ticket.status,"resolved"),"critical":count(Ticket.priority,"critical"),"high":count(Ticket.priority,"high"),"sla_at_risk":db.query(func.count(Ticket.id)).filter(Ticket.sla_risk>=.7).scalar() or 0}

@router.get("/{ticket_id}", response_model=TicketOut)
def get_one(ticket_id:str,db:Session=Depends(get_db)): return get_ticket(ticket_id,db)

@router.patch("/{ticket_id}", response_model=TicketOut)
def update(ticket_id:str,payload:TicketUpdate,db:Session=Depends(get_db)):
    t=get_ticket(ticket_id,db)
    for k,v in payload.model_dump(exclude_unset=True).items(): setattr(t,k,v)
    t.updated_at=datetime.now(timezone.utc); db.add(TicketEvent(ticket_id=t.id,event_type="UPDATED",message="Ticket updated",actor="user")); db.commit(); db.refresh(t); return t

@router.post("/{ticket_id}/analyze", response_model=TicketOut)
def analyze(ticket_id:str,db:Session=Depends(get_db)):
    t=get_ticket(ticket_id,db); analyze_ticket(t,db); db.commit(); db.refresh(t); return t

@router.post("/{ticket_id}/messages", response_model=TicketOut)
def add_message(ticket_id:str,payload:MessageCreate,db:Session=Depends(get_db)):
    t=get_ticket(ticket_id,db); db.add(TicketMessage(ticket_id=t.id,sender_type=payload.sender_type,sender_name=payload.sender_name,body=payload.body)); t.description += "\n" + payload.body; analyze_ticket(t,db); db.commit(); db.refresh(t); return t

@router.get("/{ticket_id}/timeline")
def timeline(ticket_id:str,db:Session=Depends(get_db)):
    t=get_ticket(ticket_id,db)
    events=db.query(TicketEvent).filter_by(ticket_id=t.id).order_by(TicketEvent.created_at.desc()).all()
    return [{"id":e.id,"type":e.event_type,"message":e.message,"actor":e.actor,"created_at":e.created_at} for e in events]

@router.post("/{ticket_id}/assign/{agent_id}", response_model=TicketOut)
def assign(ticket_id:str,agent_id:str,db:Session=Depends(get_db)):
    t=get_ticket(ticket_id,db); a=db.get(User,agent_id)
    if not a or not a.active: raise HTTPException(400,"Active agent not found")
    t.agent_id=a.id; t.status="in_progress"; db.add(TicketEvent(ticket_id=t.id,event_type="ASSIGNED",message=f"Assigned to {a.name}",actor="user")); db.commit(); db.refresh(t); return t
