from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from api.settings import settings, SERVICE_NAME, API_VERSION

origins = ["*"]


def create_app() -> FastAPI:
    app = FastAPI(
        debug=settings.DEBUG,
        title=SERVICE_NAME,
        version=API_VERSION,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    return app


app = create_app()
