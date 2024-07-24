import threading
from typing import List
from datetime import datetime
from dssdm.mongo.output.logs import LogNotYetInDB
from app.core.auth import authentication
from app.core.settings import settings
import requests

class Simulation_Log():
    def __init__(self, analysis_id: str, project_id: str):
        """
        Creates the log file that will be sent at the end of the simulation.
        """
        init_data=[f"LOGS INIT - {str(datetime.now())}", f"PROJECT: {project_id}, ANALYSIS: {analysis_id}"]
        self.log = LogNotYetInDB(
            analysis_id=analysis_id,
            project_id=project_id,
            date=str(datetime.now()),
            logs_data=init_data
        )
        print(init_data)

    def get_logs(self) -> LogNotYetInDB:
        """
        Returns the instance of the log.
        """
        return self.log

    def _send_logs(self) -> bool:
        """
        Post the current log data to the dss api.
        Returns:
            created: bool
        """
        token = authentication()
        header = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'Authorization': "Bearer " + token
        }
        body = self.log.dict() 
        response = requests.post(settings.dss_uri + "/logs", headers=header, json=body)
        print(response.json())
        return response.json()["created"]

    def post_logs(self) -> None:
        """
        Starts a new thread to send the logs
        Returns:
            created: bool
        """
        th = threading.Thread(target=self._send_logs, daemon=True)
        return th.start()

    def update_log(self, new_string: str) -> None:
        """
        Print the new string.
        Updates the logs_data of the log instance, by appeding new_string.
        @TODO: create a streamlike connection to put new logs directly in the database
        Returns:
            created: bool
        """
        print(new_string) # removes the necessity to use print() elsewhere
        return self.log.logs_data.append(new_string)
