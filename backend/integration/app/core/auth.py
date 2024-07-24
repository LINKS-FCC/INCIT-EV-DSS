from app.core.settings import settings
import requests

def authentication():
    """It is in charge of obtaining the access token from the DSS API in order to send the results.
    The credentials are stored inside the settings class, which in turn has parsed them
    from the environment variables.

    Returns:
        token (str): access token
    """

    header = {
        'Accept': 'application/json',
        'Content-Type': 'application/x-www-form-urlencoded'
    }

    token = requests.post(
        settings.dss_uri + "/auth/token", 
        headers=header, 
        data="grant_type=&username={}&password={}&scope=&client_id=&client_secret=".format(settings.dss_user, settings.dss_password))
    
    return token.json()["access_token"]