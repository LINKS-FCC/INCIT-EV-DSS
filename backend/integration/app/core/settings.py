from pydantic import BaseSettings
import os

class Settings(BaseSettings):
    """It contains the parameters used by the simulator.
    They are then explicitly adopted by the single modules.

    Args:
        BaseSettings: `pydantic` class 
    """

    app_name: str = "INCIT-EV DSS"
    app_description: str = "INCIT-EV Simulation Endpoint"
    app_version: str = "1.0.0"
    public_key: str = ""
    dss_uri: str = "http://dss:80/api/v1"
    dss_user: str = "admin"
    dss_password: str = "Admin0!!"
    timeout_for_simulatgion: int = 420000 # =  7 minutes * 60 seconds * 1000 ms
    # timeout_for_simulatgion: int = 60000 # =  1 minutes * 60 seconds * 1000 ms

settings = Settings()

# If the environment variables are set, then the application settings will be properly modified.
# This step is necessary in a docker implementation like this one, in order to simplify the
# configuration phase.
if os.getenv("DSS_URI") != None:
    settings.dss_uri = "http://{}:80/api/v1".format(os.getenv("DSS_URI"))

if os.getenv("DSS_USER") != None:
    settings.dss_user = os.getenv("DSS_USER")

if os.getenv("DSS_PASSWORD") != None:
    settings.dss_password = os.getenv("DSS_PASSWORD")

if os.getenv("DSS_PUBLIC_KEY") != None:
    with open(os.getenv("DSS_PUBLIC_KEY")) as fp:
        settings.public_key = fp.read()
        fp.close()