from enum import Enum
from glob import glob
from fastapi import status
import time
import threading
import requests

from app.core.settings import settings
from app.core.auth import authentication

class Status(Enum):
    """The Status enum is a simple wrapper class that associates an HTTP response code
    to the current state of the simulator.

    States:
    - WAITING: HTTP 200 OK
    - RUNNING: HTTP 406 NOT ACCEPTABLE
    """

    WAITING = status.HTTP_200_OK
    RUNNING = status.HTTP_406_NOT_ACCEPTABLE

# The state is initialized to WAITING, since at the beginning, during the run up,
# there are no requests waiting to be executed by the simulator
state = Status.WAITING
sim_time = 0
last_sim_id = "" 

def set_waiting():
    """It sets the current state to `WAITING`.
    """
    global state
    global sim_time
    global last_sim_id 

    state = Status.WAITING
    sim_time = 0
    last_sim_id = ""

def set_running(new_sim_id: str):
    """It sets the current state to `RUNNING`.
    """
    global state
    global sim_time
    global last_sim_id

    state = Status.RUNNING
    sim_time = time.time()*1000
    last_sim_id = new_sim_id

def get_state():
    """It returns the current state.

    Returns:
        FastAPI status: current state
    """
    global state

    return state.value

def is_running():
    """It returns `true` if a simulation is currently running, `false` otherwise.
    Cleans state if last simulation failed abruptly.

    Returns:
        state (bool)
    """
    global state
    global sim_time

    print("STATE: ", state)
    print("SIM_TIME: ", sim_time)
    print("ANALAYSIS_ID ", last_sim_id)

    print("THREADSSSSS_isrunning")
    print("List of running threads:")
    for thread in threading.enumerate():
        print(thread.name)

    is_stucked = (time.time()*1000 - sim_time) > settings.timeout_for_simulatgion and sim_time != 0 #if passed more time than 7min considered stucked
    print("IS_STUCKED ", is_stucked)

    if is_stucked:
        print("running and stucked")
        th = threading.Thread(target=update_stucked_analysis, args=[last_sim_id], daemon=True)
        th.start()
        set_waiting()
        return False

    if state == Status.RUNNING and not is_stucked:
        print("running and not stucked")
        return True
    else:
        print("waiting")
        return False

def update_stucked_analysis(analysis_id: str):
        print("Unstucking...")
        token = authentication()
        header = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'Authorization': "Bearer " + token
        }
        response = requests.put(settings.dss_uri + f"/logs/unstuck/{analysis_id}", headers=header)
        # handle error?
        print("Put unstuck operation completed")
        print(response.json())
        return response.json()