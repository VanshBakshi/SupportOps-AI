class RoutingService:
    def health(self): return {"status":"healthy","mode":"skill-workload-routing"}
def get_routing_service(): return RoutingService()
