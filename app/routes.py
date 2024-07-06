from fastapi import APIRouter, Depends, HTTPException, File, UploadFile, Form
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import delete, update
from . import models
from .database import get_db
import shutil
import os
from uuid import uuid4

from .models import ImageUpdate

router = APIRouter()


@router.get("/images")
async def get_images(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(models.Image))
    images = result.scalars().all()
    return images


@router.get("/images/{image_id}")
async def get_image(image_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(models.Image).filter(models.Image.id == image_id))
    image = result.scalars().first()
    if image is None:
        raise HTTPException(status_code=404, detail="Image not found")
    return image


@router.delete("/images/{image_id}")
async def delete_image(image_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(models.Image).filter(models.Image.id == image_id))
    image = result.scalars().first()
    if image is None:
        raise HTTPException(status_code=404, detail="Image not found")

    await db.execute(delete(models.Image).where(models.Image.id == image_id))
    await db.commit()
    return {"message": "Image deleted successfully"}


@router.post("/images")
async def create_image(
        file: UploadFile = File(...),
        title: str = Form(...),
        description: str = Form(...),
        db: AsyncSession = Depends(get_db)
):
    # Generate a unique filename
    file_extension = os.path.splitext(file.filename)[1]
    unique_filename = f"{uuid4()}{file_extension}"

    # Define the path where the image will be saved
    static_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static")
    file_location = os.path.join(static_dir, "images", unique_filename)

    # Ensure the directory exists
    os.makedirs(os.path.dirname(file_location), exist_ok=True)

    # Save the file
    with open(file_location, "wb+") as file_object:
        shutil.copyfileobj(file.file, file_object)

    # Create a new Image record in the database
    new_image = models.Image(
        title=title,
        url=f"/static/images/{unique_filename}",
        description=description
    )
    db.add(new_image)
    await db.commit()
    await db.refresh(new_image)

    return {
        "id": new_image.id,
        "title": new_image.title,
        "url": new_image.url,
        "description": new_image.description
    }


@router.put("/images/{image_id}")
async def update_image(
        image_id: int,
        image_update: ImageUpdate,
        db: AsyncSession = Depends(get_db)
):
    # Check if the image exists
    result = await db.execute(select(models.Image).filter(models.Image.id == image_id))
    image = result.scalars().first()
    if image is None:
        raise HTTPException(status_code=404, detail="Image not found")

    # Update the image details
    update_stmt = update(models.Image).where(models.Image.id == image_id).values(
        title=image_update.title,
        description=image_update.description
    )
    await db.execute(update_stmt)
    await db.commit()

    # Fetch the updated image
    result = await db.execute(select(models.Image).filter(models.Image.id == image_id))
    updated_image = result.scalars().first()

    return {
        "id": updated_image.id,
        "title": updated_image.title,
        "url": updated_image.url,
        "description": updated_image.description
    }
