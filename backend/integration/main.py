from fastapi import FastAPI

from app.api.v1 import simulations, health
from app.core.settings import settings

app = FastAPI(
    title=settings.app_name,
    description=settings.app_description,
    version=settings.app_version
)

# The requests that are used to create/start new simulations 
# are handled by the simulations router.
app.include_router(simulations.router,
                   prefix="/simulations",
                   tags=["Simulations"],
                   responses={404: {"description": "Not found"}},
                   )

# The requests that are used to know if the simulator is occupied or not 
# are handled by the health router.
app.include_router(health.router,
                   prefix="/health",
                   tags=["Health"],
                   responses={404: {"description": "Not found"}},
                   )

app.mount("/api/v1", app)