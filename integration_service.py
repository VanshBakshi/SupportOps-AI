class IntegrationService:
    async def health(self): return {"status":"optional","message":"External providers are optional in local mode."}
def get_integration_service(): return IntegrationService()
