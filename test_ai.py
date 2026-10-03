import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'backend'))
from app.services.ai_engine import classify,sentiment,priority
from app.database.models import Ticket

def ticket(s,d): return Ticket(subject=s,description=d)
def test_classification(): assert classify(ticket('API error','Our API timeout is blocking users'))['category']=='Technical Support'
def test_security_priority(): assert priority(ticket('Security breach','We were hacked and customer data may be exposed'))['priority']=='critical'
def test_negative_sentiment(): assert sentiment(ticket('Terrible','This is terrible and frustrating'))['label'] in {'negative','angry'}
