from typing import List
from fastapi import HTTPException, status
from datetime import datetime

from app.core.db import DB
# from app.models.user import UserInDB
from dssdm.mongo.input.analysis import AnalysesInDB
from dssdm.mongo.output.logs import Log, LogNotYetInDB
from dssdm.mongo.mongodb_utils import OID

def get_logs_of_analysis(analysis_id: str, db: DB):
    """
    Get logs of an analysis

    Parameters
    ----------
    db: DB
        database with all informations
    analysis_id: str
        target analysis to get logs from

        
    Returns
    -------
    n_logs: int 
        number of logs for the current analysis
    logs: arr[Logs] 
        array with all logs found in the db for the current analysis

    """
    l = db.instance["logs"]
    logs = list(map(lambda kv: Log.from_mongo(kv), list(l.find({"analysis_id": analysis_id}))))
    if logs is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Error in finding logs for current analysis.")
    return {
        "n_logs": len(logs),
        "logs": logs,
    }

def create_log_of_analysis(log: LogNotYetInDB, db: DB):
    """
    Create log for the current analysis

    Parameters
    ----------
    log: LogNotYetInDB
        log dict containing the logs_data
    db: DB
        database with all informations
        
    Returns
    -------
    created: boolean
        true if created correctly, false in case of error

    """
    l = db.instance["logs"] 
    res = l.insert_one(log.mongo())
    if res is None:
        return {"created": False}
    return {"created": True}

def unstuck_analysis(analysis_id: OID, db: DB):
    """
    Modify the "status" field of a stucked analysis

    Parameters
    ----------
    analyses_id: OID
        analysis id
    db: DB
        database with all informations

    Returns
    -------
    null => everything right

    """
    print("called unstuck service")
    a = db.instance["analyses"]
    l = db.instance["logs"]

    # update analysis
    analysis = AnalysesInDB.from_mongo(a.find_one({"_id": analysis_id}))
    print("analysis: ", analysis)
    if analysis is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="There are no analyses with the specified ID.")
    res_a = a.update_one({"_id": analysis_id}, {"$set": {"status": "failed"}})
    print("res a: ", res_a)

    # update log
    log_data=[f"LOGS INIT - {str(datetime.now())}", f"PROJECT: {analysis.project_id}, ANALYSIS: {analysis_id}", "Simulation failed and remained stucked.", "Failed to save backtrace"]
    log = LogNotYetInDB(
       date = str(datetime.now()),
       project_id = str(analysis.project_id),
       analysis_id = str(analysis_id),
       logs_data = log_data
    )
    print("new log: ", log)
    res_l = l.insert_one(log.mongo())
    print("res l: ", res_l)

    # send response
    response = {
        "updated_analysis": res_a is not None,
        "created_log": res_l is not None,
    }
    print("response: ", response)
    return response