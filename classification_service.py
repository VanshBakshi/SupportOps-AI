from app.services.ai_engine import classify
def get_classification_service():
    class S:
        def health(self): return {"status":"healthy","mode":"local-rule-engine"}
    return S()
