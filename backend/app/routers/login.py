from fastapi import APIRouter, UploadFile, File, Depends
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import User
from ..services.face_service import get_face_embedding
from ..services.latency_service import LatencyTracker, save_latency
import os

router = APIRouter(prefix="/auth", tags=["Facial Login"])

THRESHOLD = float(os.getenv("THRESHOLD", 0.6))

@router.post("/login")
async def facial_login(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    tracker = LatencyTracker()

    tracker.start("upload")
    image_bytes = await file.read()
    tracker.stop("upload")

    tracker.start("embedding")
    embedding = get_face_embedding(image_bytes)
    tracker.stop("embedding")

    if embedding is None:
        times = tracker.times
        times["total"] = tracker.total()
        save_latency(db, None, False, times)
        return {"status": "No face detected", "latency": times}

    tracker.start("db_query")
    result = (
        db.query(User)
        .order_by(User.embedding.l2_distance(embedding))
        .first()
    )
    tracker.stop("db_query")

    tracker.start("decision")
    success = result is not None and \
              result.embedding.l2_distance(embedding) < THRESHOLD
    tracker.stop("decision")

    times = tracker.times
    times["total"] = tracker.total()

    save_latency(db, result.id if success else None, success, times)

    if success:
        return {
            "status": "Authenticated",
            "user_id": result.id,
            "name": result.name,
            "latency_ms": times
        }
    else:
        return {
            "status": "Authentication failed",
            "latency_ms": times
        }
