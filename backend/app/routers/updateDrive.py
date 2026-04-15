from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException
from ..database import get_db
from ..models import User
from sqlalchemy.orm import Session

router = APIRouter(prefix="/auth", tags=["Register"])

@router.post("/update-drive")
async def update_drive(user_id: int,drive_file_id: str,db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=404,
            detail="Usuario no encontrado"
        )
    # Actualizar campo
    user.id_drive = drive_file_id

    db.commit()
    db.refresh(user)

    return {
        "message": "Usuario actualizado correctamente",
        "user_id": user.id,
        "drive_file_id": user.id_drive
    }
