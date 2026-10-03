class SLAService:
    def health(self): return {"status":"healthy","mode":"risk-engine"}
def get_sla_service(): return SLAService()
