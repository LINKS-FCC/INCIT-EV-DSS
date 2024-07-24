from app.services.dss import run_simulation
from app.core.status import is_running
from app.core.settings import settings
import os

from typing import Tuple
from Crypto.Hash import SHA256
from Crypto.Signature import PKCS1_v1_5
from Crypto.PublicKey import RSA
from base64 import b64decode
import json
import threading

from app.core.logs import Simulation_Log

def check_sender(
    analysis,
    shape_file,
    analysis_hash,
    shape_file_hash) -> Tuple[bool, bool]:
    """This method verifies if the body of the request has been effectively sent by the DSS API.

    Args:
        analysis (AnalysesSimulation): simulation parameters
        shape_file (str): the shapefile associated to a single project
        analysis_hash (str): hash of the simulation parameters
        shape_file_hash (str): hash of the shapefile

    Returns:
    bool: if sender is verified
    """
    public_key = RSA.importKey(settings.public_key)
    verifier = PKCS1_v1_5.new(public_key)

    digest = SHA256.new()
    digest_analysis = b64decode(analysis_hash)
    digest.update(json.dumps(analysis.dict()).encode())
    verified_analysis = verifier.verify(digest, digest_analysis)

    digest = SHA256.new()
    digest_shapefile = b64decode(shape_file_hash)
    digest.update(shape_file.encode())
    verified_shapefile = verifier.verify(digest, digest_shapefile)
    return verified_analysis, verified_shapefile

def schedule_simulation(
    analysis,
    shape_file,
    analysis_hash,
    shape_file_hash):
    """If sender is verified and if it is not running another simulation, a new daemon thread is created
    and associated to the received analysis.

    Args:
        analysis (AnalysesSimulation): simulation parameters
        shape_file (str): the shapefile associated to a single project
        analysis_hash (str): hash of the simulation parameters
        shape_file_hash (str): hash of the shapefile

    Returns:
        response (dict): dictionary containing some usefull information about the status
        of the request and the simulator that took over the request

    """
    # Init logs object
    sim_log = Simulation_Log(
        analysis_id=analysis.id,
        project_id=analysis.project_id,
    )

    sim_log.update_log("Checking signature for authentication")

    verified_analysis, verified_shapefile = check_sender(analysis=analysis, analysis_hash= analysis_hash, shape_file=shape_file, shape_file_hash=shape_file_hash)

    sim_log.update_log(f"Shapefile is verified: {verified_shapefile}")
    sim_log.update_log(f"Analysis is verified: {verified_shapefile}")

    hostname = os.getenv("HOSTNAME")

    print("THREADS_initial")
    print("List of running threads:")
    for thread in threading.enumerate():
        print(thread.name)

    if not verified_analysis or not verified_shapefile:
        sim_log.update_log("STATUS: unauthorized, simulation not started")
        sim_log.post_logs()
        return {
            "analysis_id": analysis.id,
            "dss": hostname,
            "result": "unauthorized"
        }

    if is_running():
        sim_log.update_log("STATUS: occupied, simulation not started")
        sim_log.post_logs()
        return {
            "analysis_id": analysis.id,
            "dss": hostname,
            "result": "failed" #TODO add queued here
        }

    try:
        th = threading.Thread(target=run_simulation, args=(sim_log, analysis, shape_file), daemon=True)
        th.start()
        sim_log.update_log("STATUS: running, simulation has started in a new thread")

        print("THREADS_started")
        print("List of running threads:")
        for thread in threading.enumerate():
            print(thread.name)

        return {
            "analysis_id": analysis.id,
            "dss": hostname,
            "result": "running"
        }
    except:
        sim_log.update_log("STATUS: failed, error in the creation of a new thread")
        sim_log.post_logs()
        return {
            "analysis_id": analysis.id,
            "dss": hostname,
            "result": "failed"
        }