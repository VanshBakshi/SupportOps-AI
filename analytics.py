from collections import Counter
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.database.models import Ticket
router=APIRouter(prefix="/analytics",tags=["Analytics"])
@router.get("/overview")
def overview(db:Session=Depends(get_db)):
    rows=db.query(Ticket).all(); n=len(rows)
    return {"total":n,"open":sum(t.status=="open" for t in rows),"in_progress":sum(t.status=="in_progress" for t in rows),"resolved":sum(t.status=="resolved" for t in rows),"avg_sla_risk":round(sum(t.sla_risk for t in rows)/n,3) if n else 0,"avg_ai_confidence":round(sum(t.ai_confidence for t in rows)/n,3) if n else 0,"categories":dict(Counter(t.category for t in rows)),"priorities":dict(Counter(t.priority for t in rows)),"sentiments":dict(Counter(t.sentiment for t in rows))}
@router.get("/agents")
def agents(db:Session=Depends(get_db)):
    rows=db.query(Ticket).all(); c=Counter(t.agent_id or "unassigned" for t in rows); return [{"agent_id":k,"tickets":v} for k,v in c.items()]
