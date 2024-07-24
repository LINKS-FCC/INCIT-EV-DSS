from pydantic import BaseModel

class CiDefaults(BaseModel):
    Expected_EV: float  # Ratio of EV (deprecated, leave at 1.0)
    ROIG: int  # ROI Goal [€] (general)
