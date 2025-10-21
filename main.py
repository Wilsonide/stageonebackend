from fastapi import FastAPI

import service
from config import config
from db import Base, engine

Base.metadata.create_all(bind=engine)

app = FastAPI(title=config.app_name)


# Register routes
app.include_router(service.router, prefix="/api")

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="localhost", port=8000)
