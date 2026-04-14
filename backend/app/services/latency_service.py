import time
from ..models import LoginLatencyDetail

class LatencyTracker:
    def __init__(self):
        self.times = {}
        self.total_start = time.perf_counter()

    def start(self, stage):
        self.times[stage] = time.perf_counter()

    def stop(self, stage):
        self.times[stage] = (time.perf_counter() - self.times[stage]) * 1000

    def total(self):
        return (time.perf_counter() - self.total_start) * 1000

def save_latency(db, user_id, success, times):
    latency = LoginLatencyDetail(
        user_id=user_id,
        success=success,
        upload_time_ms=times.get("upload"),
        preprocess_time_ms=times.get("preprocess"),
        detection_time_ms=times.get("detection"),
        embedding_time_ms=times.get("embedding"),
        db_query_time_ms=times.get("db_query"),
        decision_time_ms=times.get("decision"),
        total_latency_ms=times.get("total"),
    )
    db.add(latency)
    db.commit()
