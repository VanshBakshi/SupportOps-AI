from fastapi import APIRouter
from app.core.config import settings
from app.database.connection import check_database_connection
router=APIRouter(prefix="/health",tags=["Health"])
@router.get("")
def health():
    try: db=check_database_connection(); db_status="healthy" if db else "unhealthy"
    except Exception as e: db=False; db_status=f"error: {e}"
    return {"status":"healthy" if db else "degraded","service":settings.app_name,"version":"1.0.0","database":db_status}
@router.get("/live")
def live(): return {"status":"alive"}
@router.get("/ready")
def ready():
    try: check_database_connection(); return {"status":"ready"}
    except Exception as e: return {"status":"not_ready","error":str(e)}
