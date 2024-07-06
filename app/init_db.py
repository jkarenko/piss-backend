import asyncio
import os
from .database import engine, Base, AsyncSessionLocal
from .models import Image

STATIC_URL_PATH = "/static/images"
IMAGE_DIRECTORY = os.path.join(os.path.dirname(__file__), "static", "images")


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as session:
        sample_images = [
            Image(
                title="Kabuki mask",
                url=f"{STATIC_URL_PATH}/sky01.jpg",
                description="Kabuki mask in the sky made of clouds."
            ),
            Image(
                title="Totem pole of spoopy",
                url=f"{STATIC_URL_PATH}/sky02.jpg",
                description="Grim Reaper, Mothman and Frank the Bunny."
            ),
            Image(
                title="8-bit spoop",
                url=f"{STATIC_URL_PATH}/sky03.jpg",
                description="Low-res reaper watching you."
            ),
        ]

        # Verify that image files exist
        for image in sample_images:
            file_path = os.path.join(IMAGE_DIRECTORY, os.path.basename(image.url))
            if not os.path.exists(file_path):
                print(f"Warning: Image file not found: {file_path}")

        session.add_all(sample_images)
        await session.commit()


if __name__ == "__main__":
    asyncio.run(init_db())
