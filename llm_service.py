# Optional LLM adapter. The application remains fully functional without an API key.
from app.core.config import settings
class LLMService:
    def health(self): return {"status":"configured" if settings.llm_provider != "none" else "fallback","provider":settings.llm_provider}
def get_llm_service(): return LLMService()
