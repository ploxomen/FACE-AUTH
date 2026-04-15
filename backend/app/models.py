from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from pgvector.sqlalchemy import Vector
from .database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(150), unique=True)
    embedding = Column(Vector(128), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    id_drive = Column(String(500), nullable=True)
    latencies = relationship("LoginLatencyDetail", back_populates="user")


class LoginLatencyDetail(Base):
    __tablename__ = "login_latency_details"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    success = Column(Boolean, nullable=False)

    upload_time_ms = Column(Float)
    embedding_time_ms = Column(Float)
    db_query_time_ms = Column(Float)
    decision_time_ms = Column(Float)
    total_latency_ms = Column(Float, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="latencies")
