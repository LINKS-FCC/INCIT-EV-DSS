from fastapi import FastAPI

from app.api.v1 import analyses, users, auth, projects, results, defaults, logs, dcm
from app.core.config import settings

app = FastAPI(
    title=settings.app_name,
    description=settings.app_description,
    version=settings.version
)

app.include_router(auth.router,
                   prefix="/auth",
                   tags=["Auth"],
                   responses={404: {"description": "Not found"}},
                   )
app.include_router(users.router,
                   prefix="/users",
                   tags=["Users"],
                   responses={404: {"description": "Not found"}},
                   )
app.include_router(projects.router,
                   prefix="/projects",
                   tags=["Projects"],
                   responses={404: {"description": "Not found"}},
                   )
app.include_router(analyses.router,
                    prefix="/analyses",
                    tags=["Analyses"],
                    responses={404: {"description": "Not found"}}
                    )
app.include_router(results.router,
                    prefix="/results",
                    tags=["Results"],
                    responses={404: {"description": "Not found"}}
                    )
app.include_router(defaults.router,
                    prefix="/defaults",
                    tags=["Defaults"],
                    responses={404: {"description": "Not found"}}
                    )
app.include_router(logs.router,
                    prefix="/logs",
                    tags=["Logs"],
                    responses={404: {"description": "Not found"}}
                    )
app.include_router(dcm.router,
                    prefix="/dcm",
                    tags=["DCM"],
                    responses={404: {"description": "Not found"}}
                    )

app.mount("/api/v1", app)