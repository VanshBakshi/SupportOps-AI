import re, math
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from sqlalchemy.orm import Session
from app.core.config import settings
from app.database.models import AIPrediction, Ticket

TAXONOMY = {
    "Technical Support": ["Software Issue", "Installation", "Performance", "API / Integration", "Login / Access"],
    "Billing & Payments": ["Payment Failure", "Refund", "Invoice", "Subscription", "Unexpected Charge"],
    "Account Management": ["Profile Update", "Account Closure", "Password Reset", "Account Access"],
    "Security & Privacy": ["Suspicious Activity", "Data Privacy", "Security Incident"],
    "Orders & Delivery": ["Order Status", "Delivery Delay", "Wrong Item", "Damaged Item"],
    "Product Support": ["Product Information", "Compatibility", "Usage Help"],
    "Customer Service": ["General Inquiry", "Complaint", "Feedback"],
}
KEYWORDS = {
    "Technical Support": ["error", "bug", "crash", "api", "integration", "slow", "timeout", "login", "install", "not working"],
    "Billing & Payments": ["payment", "refund", "invoice", "subscription", "charged", "billing", "transaction"],
    "Account Management": ["password", "account", "profile", "delete account", "reset"],
    "Security & Privacy": ["hacked", "breach", "suspicious", "privacy", "phishing", "unauthorized", "security"],
    "Orders & Delivery": ["order", "delivery", "shipment", "delayed", "damaged", "wrong item", "tracking"],
    "Product Support": ["product", "compatible", "feature", "how to use", "specification"],
    "Customer Service": ["complaint", "feedback", "question", "suggestion", "help"],
}
POSITIVE = {"thanks", "thank you", "great", "excellent", "good", "helpful", "resolved", "happy"}
NEGATIVE = {"bad", "terrible", "angry", "frustrated", "unhappy", "worst", "disappointed", "useless", "broken"}
CRITICAL = ["data breach", "hacked", "ransomware", "security incident", "all users", "production down", "outage", "payment system down", "data loss"]
HIGH = ["urgent", "asap", "blocked", "cannot work", "business stopped", "multiple users", "production", "deadline"]


def text(ticket: Ticket) -> str:
    return f"{ticket.subject} {ticket.description}".lower().strip()


def classify(ticket: Ticket) -> dict:
    t = text(ticket)
    scores = {cat: sum(t.count(k) for k in keys) for cat, keys in KEYWORDS.items()}
    category = max(scores, key=scores.get) if max(scores.values(), default=0) else "Customer Service"
    confidence = min(0.98, 0.52 + (scores[category] * 0.08))
    sub = TAXONOMY[category][0]
    subrules = {
        "Technical Support": {"API / Integration": ["api", "webhook", "integration"], "Performance": ["slow", "latency", "timeout", "lag"], "Installation": ["install", "setup"], "Login / Access": ["login", "sign in", "access"]},
        "Billing & Payments": {"Payment Failure": ["failed", "declined", "payment"], "Refund": ["refund"], "Invoice": ["invoice", "receipt"], "Subscription": ["subscription", "renewal"], "Unexpected Charge": ["unexpected", "duplicate", "charged"]},
        "Account Management": {"Password Reset": ["password", "reset"], "Account Closure": ["delete account", "close account"], "Profile Update": ["profile", "email address"]},
        "Security & Privacy": {"Security Incident": ["breach", "hacked", "malware", "phishing"], "Suspicious Activity": ["suspicious", "unauthorized", "unknown login"], "Data Privacy": ["privacy", "personal data"]},
        "Orders & Delivery": {"Delivery Delay": ["delayed", "late", "not delivered"], "Damaged Item": ["damaged", "broken"], "Wrong Item": ["wrong item", "incorrect"], "Order Status": ["status", "tracking", "track"]},
        "Product Support": {"Compatibility": ["compatible", "works with"], "Usage Help": ["how to", "use", "instructions"]},
        "Customer Service": {"Complaint": ["complaint", "terrible", "unhappy"], "Feedback": ["feedback", "suggestion"]},
    }
    for candidate, words in subrules.get(category, {}).items():
        if any(w in t for w in words): sub = candidate; break
    return {"category": category, "subcategory": sub, "confidence": round(confidence, 3), "alternatives": sorted([{"category": k, "confidence": round(min(.9, .35 + v*.08), 3)} for k,v in scores.items() if k != category], key=lambda x:x["confidence"], reverse=True)[:3]}


def sentiment(ticket: Ticket) -> dict:
    t = text(ticket)
    pos = sum(t.count(x) for x in POSITIVE); neg = sum(t.count(x) for x in NEGATIVE)
    angry = sum(t.count(x) for x in ["angry", "furious", "ridiculous", "unacceptable", "worst"])
    score = max(-1.0, min(1.0, (pos-neg-angry*1.5) / max(5, len(t.split())/2)))
    if angry or score < -0.45: label = "angry"
    elif score < -0.12: label = "negative"
    elif score > 0.12: label = "positive"
    else: label = "neutral"
    return {"label": label, "score": round(score, 3), "confidence": round(min(.98, .55 + abs(score)*.4), 3), "signals": {"positive_terms": pos, "negative_terms": neg, "anger_terms": angry}}


def priority(ticket: Ticket) -> dict:
    t = text(ticket); score = 20; reasons=[]
    if any(k in t for k in CRITICAL): score += 60; reasons.append("critical business/security impact")
    if any(k in t for k in HIGH): score += 25; reasons.append("urgency or operational impact")
    if "customer" in t and any(x in t for x in ["cannot", "unable", "blocked"]): score += 15; reasons.append("customer blocked")
    if any(x in t for x in ["question", "information", "feature"]): score -= 5
    score = max(0, min(100, score))
    label = "critical" if score >= 75 else "high" if score >= 50 else "medium" if score >= 25 else "low"
    return {"priority": label, "score": score, "confidence": round(min(.97, .58 + len(reasons)*.1),3), "reasons": reasons}


def sla(ticket: Ticket, p: dict) -> dict:
    minutes = {"critical":60,"high":240,"medium":480,"low":1440}[p["priority"]]
    age = (datetime.now(timezone.utc) - ticket.created_at.replace(tzinfo=timezone.utc)).total_seconds()/60
    risk = min(.99, max(.02, age / minutes * .72 + (0.25 if p["priority"] in {"critical","high"} else 0)))
    risk = round(risk,3)
    level = "critical" if risk >= .9 else "high" if risk >= .7 else "medium" if risk >= .4 else "low"
    return {"risk": risk, "level": level, "target_minutes": minutes, "age_minutes": round(age,1), "breach_predicted": risk >= .7}


def routing(ticket: Ticket, category: str, db: Session) -> dict:
    agents = db.query(__import__('app.database.models', fromlist=['User']).User).filter_by(active=True).all()
    if not agents: return {"assigned_agent_id": None, "confidence": 0.0, "reason": "No active agent available", "candidates": []}
    required = set({"Technical Support": ["python","api","technical"], "Billing & Payments":["billing","payments"], "Security & Privacy":["security","privacy"], "Orders & Delivery":["orders","delivery"], "Product Support":["product"], "Account Management":["accounts"], "Customer Service":["customer service"]}.get(category,["general"]))
    candidates=[]
    for a in agents:
        skills={str(s).lower() for s in (a.skills or [])}; match=len(required & skills); load=db.query(Ticket).filter(Ticket.agent_id==a.id, Ticket.status.in_(["open","in_progress"])).count(); score=match*50 + max(0,30-load*5)
        candidates.append({"agent_id":a.id,"name":a.name,"skill_match":match,"active_tickets":load,"score":score})
    candidates.sort(key=lambda x:x["score"], reverse=True); best=candidates[0]
    return {"assigned_agent_id":best["agent_id"],"confidence":round(min(.99,.55+best["score"]/200),3),"reason":"skill and workload based routing","candidates":candidates[:5]}


def llm_fallback(ticket: Ticket, cls: dict, p: dict, s: dict) -> dict:
    summary=f"Customer reports {ticket.subject.lower()}. Classified as {cls['category']} / {cls['subcategory']} with {p['priority']} priority and {s['label']} sentiment."
    action="Review the ticket, verify the affected account/context, reproduce the issue where applicable, and respond with the next concrete resolution step."
    if p["priority"] in {"critical","high"}: action="Escalate to the appropriate support owner, acknowledge the customer quickly, and investigate the highest-impact failure path first."
    return {"summary":summary,"recommended_action":action,"provider":"local-fallback"}


def analyze_ticket(ticket: Ticket, db: Session) -> dict:
    cls=classify(ticket); s=sentiment(ticket); p=priority(ticket); sl=sla(ticket,p); r=routing(ticket,cls["category"],db); llm=llm_fallback(ticket,cls,p,s)
    ticket.category=cls["category"]; ticket.subcategory=cls["subcategory"]; ticket.ai_confidence=cls["confidence"]; ticket.sentiment=s["label"]; ticket.sentiment_score=s["score"]; ticket.priority=p["priority"]; ticket.sla_risk=sl["risk"]; ticket.ai_summary=llm["summary"]; ticket.recommended_action=llm["recommended_action"]
    if not ticket.agent_id and r.get("assigned_agent_id"): ticket.agent_id=r["assigned_agent_id"]
    for typ,val,conf,ex in [("category",f"{cls['category']} / {cls['subcategory']}",cls["confidence"],"Keyword-weighted text classification"),("priority",p["priority"],p["confidence"],"Business impact and urgency signals"),("sentiment",s["label"],s["confidence"],"Interpretable sentiment signals"),("sla_risk",sl["level"],sl["risk"],"Elapsed time and priority risk")]:
        db.add(AIPrediction(ticket_id=ticket.id,prediction_type=typ,predicted_value=val,confidence=conf,explanation=ex,features={}))
    db.add(__import__('app.database.models', fromlist=['TicketEvent']).TicketEvent(ticket_id=ticket.id,event_type="AI_ANALYZED",message="AI pipeline completed",actor="system",event_metadata={"category":cls["category"],"priority":p["priority"],"sla_risk":sl["risk"]}))
    return {"classification":cls,"priority":p,"sentiment":s,"sla":sl,"routing":r,"llm":llm}
