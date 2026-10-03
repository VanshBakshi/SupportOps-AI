from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.database.models import User
from pydantic import BaseModel, EmailStr
router=APIRouter(prefix="/auth",tags=["Auth"])
class Register(BaseModel): email:EmailStr; name:str="Support Agent"; role:str="agent"; skills:list[str]=[]
@router.post("/register")
def register(p:Register,db:Session=Depends(get_db)):
    if db.query(User).filter_by(email=p.email).first(): raise HTTPException(409,"User already exists")
    u=User(email=p.email,name=p.name,role=p.role,skills=p.skills); db.add(u); db.commit(); db.refresh(u); return u
@router.get("/users")
def users(db:Session=Depends(get_db)): return db.query(User).all()
