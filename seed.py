import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; sys.path.insert(0,str(ROOT/'backend'))
from app.database.connection import init_db, db_session
from app.database.models import User, Ticket
from app.services.ai_engine import analyze_ticket

AGENTS=[
("alex@supportops.local","Alex Johnson",["python","api","technical"]),
("priya@supportops.local","Priya Sharma",["billing","payments","accounts"]),
("rahul@supportops.local","Rahul Verma",["security","privacy","technical"]),
("neha@supportops.local","Neha Kapoor",["orders","delivery","product"]),
]
TICKETS=[
("Payment failed twice","My payment was declined twice and I need the subscription today."),
("Production API timeout","Our production API is timing out for multiple users and business is blocked."),
("Suspicious login","I received an unknown login alert and think someone accessed my account."),
("Where is my order","My order has not arrived and tracking has not changed for three days."),
("How can I update my profile","I want to change my email address in my profile."),
("Refund request","The service was not useful for me and I would like a refund."),
("Application crashes","The desktop application crashes every time I open the reports page."),
("Great support","Thanks, the previous agent solved my issue quickly. Great support."),
]

def main():
    init_db()
    with db_session() as db:
        agent_info=[]
        for email,name,skills in AGENTS:
            a=db.query(User).filter_by(email=email).first()
            if not a:
                a=User(email=email,name=name,role="agent",skills=skills); db.add(a); db.flush()
            agent_info.append((a.name,a.email,a.skills))
        if db.query(Ticket).count()==0:
            for i,(subject,description) in enumerate(TICKETS):
                t=Ticket(customer_name=f"Customer {i+1}",customer_email=f"customer{i+1}@example.com",subject=subject,description=description,source="seed")
                db.add(t); db.flush(); analyze_ticket(t,db)
    print("Seed complete. Demo users:")
    for name,email,skills in agent_info: print(f"- {name}: {email} skills={skills}")
if __name__=="__main__": main()
