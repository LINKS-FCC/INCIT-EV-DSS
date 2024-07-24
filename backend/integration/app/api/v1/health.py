from fastapi import APIRouter, Response
from app.core.status import get_state

router = APIRouter()

@router.get("/")
async def get_health(response: Response):
    """This API returns the current status of the simulator.
    The results is always an empty dictionary, because what is matter is the
    response status code.

    Returns:
        dict: empty dictionary
    """
    response.status_code = get_state()
    return {}