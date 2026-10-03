class PriorityService:
    def health(self): return {"status":"healthy","mode":"business-impact-engine"}
def get_priority_service(): return PriorityService()
