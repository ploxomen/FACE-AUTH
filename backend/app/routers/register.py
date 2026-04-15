from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException
import requests
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import User
from ..services.face_service import get_face_embedding, FaceDetectionError # Importamos la excepción

router = APIRouter(prefix="/auth", tags=["Register"])

@router.post("/register")
async def register_user(
    name: str = Form(...),
    email: str = Form(None),
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    try:
        image_bytes = await file.read()
        embedding = get_face_embedding(image_bytes)

        if embedding is None:
            raise HTTPException(status_code=400, detail="Error al procesar el rostro.")

        user = User(
            name=name,
            email=email,
            embedding=embedding.tolist()
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        data = {
            "user_id": str(user.id),
            "correo": email,
            "nombre": name
        }
        files = {
            "data": (file.filename, image_bytes, file.content_type)
        }
        requests.post(
            "https://n8n-periferico.duckdns.org/webhook/upload-face",
            files=files,
            data=data
        )
        return {"message": "User registered", "user_id": user.id}

    except FaceDetectionError as e:
        # Aquí atrapamos el error de "no hay rostro" o "múltiples rostros"
        raise HTTPException(status_code=400, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")