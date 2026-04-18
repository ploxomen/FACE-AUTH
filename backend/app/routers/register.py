from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException, BackgroundTasks
import requests
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import User
from ..services.face_service import get_face_embedding, FaceDetectionError # Importamos la excepción

router = APIRouter(prefix="/auth", tags=["Register"])

def send_perfil_plex(name):
    url = "https://clients.plex.tv/api/v2/home/users/restricted"
    headers = {
        "X-Plex-Token": "zeyrHqj4WaF1xCVszLa8",
        "X-Plex-Client-Identifier": "miapp123",
    }
    params = {
        "sharingSettings[allowTuners]": "0",
        "sharingSettings[allowSync]": "1",
        "friendlyName": name,
    }
    try:
        requests.post(
            url,
            headers=headers, 
            params=params 
        )
    except Exception as e:
        print(f"Error al enviar al PLEX: {e}")

def send_webhook_task(image_bytes, filename, content_type, data):
    files = {"data": (filename, image_bytes, content_type)}
    try:
        requests.post(
            "https://n8n-periferico.duckdns.org/webhook/upload-face",
            files=files,
            data=data,
            timeout=10 
        )
    except Exception as e:
        print(f"Error enviando webhook: {e}")

@router.post("/register")
async def register_user(
    background_tasks: BackgroundTasks,
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
        background_tasks.add_task(
            send_webhook_task, 
            image_bytes, 
            file.filename, 
            file.content_type, 
            data
        )
        background_tasks.add_task(
            send_perfil_plex,
            name
        )
        return {"message": "User registered", "user_id": user.id}

    except FaceDetectionError as e:
        # Aquí atrapamos el error de "no hay rostro" o "múltiples rostros"
        raise HTTPException(status_code=400, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")