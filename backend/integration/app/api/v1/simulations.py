from fastapi import APIRouter, Body
from app.services.simulations import schedule_simulation

from dssdm.mongo.input.analysis import AnalysesSimulation

router = APIRouter()

@router.post("/")
async def post_simulations(
    analysis: AnalysesSimulation,
    shape_file: str = Body(),
    analysis_hash: str = Body(),
    shape_file_hash: str = Body()):
    """This API accepts in input, from the DSS API, the parameters of the simulation that it
    has to run. 

    NOTE: for the moment, inside the input there are also the hash strings signed with the 
    private key of the DSS API.
    In the future, it is possible that this verification step will be modified.

    Args:
        analysis (AnalysesSimulation): simulation parameters
        shape_file (str): the shapefile associated to a single project
        analysis_hash (str): hash of the simulation parameters
        shape_file_hash (str): hash of the shapefile

    Returns:
        status (dict): returns if the simulator can accept the request or not
    """
    
    return schedule_simulation(
        analysis, 
        shape_file,
        analysis_hash,
        shape_file_hash)