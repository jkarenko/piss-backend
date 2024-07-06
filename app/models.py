from pydantic import BaseModel
from sqlalchemy import Column, Integer, String
from .database import Base


class Image(Base):
    __tablename__ = "images"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    url = Column(String)
    description = Column(String)


class ImageUpdate(BaseModel):
    title: str
    description: str
