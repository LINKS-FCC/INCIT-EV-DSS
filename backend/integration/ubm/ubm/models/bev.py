from typing import Optional
import numpy as np
from pydantic import BaseModel
class EV_Model(BaseModel):
    """
    Characterization of the BEV ev model type.

    Attributes
    ----------
    battery_size: int
        Dimension of the Battery in kWh
    avg_consumption_kwh_km: float
        Average kWh/km consumption
    """
    battery_size: int
    avg_consumption_kwh_km: float



class BEV(BaseModel):
    """
    Formalization of the Battery Electric Vehicle (BEV) agent.

    Notes
    ====
    `parking_start_hour is extracted for each day in the simulation

    Attributes
    ----------
    battery_size: int
        Dimension of the Battery in kWh
    avg_consumption_kwh_km: float
        Average kWh/km consumption
    soc: float
        Current State of Charge (SoC) which ranges from 0 to 1.
    starting_soc: float
        State of Charge threshold for starting recharging [0,1]
    final_soc: float
        State of Charge until the car will charge [0,1]
    km_travelled_per_day: float
        Number of km travelled each day
    parking_hours: int
        Number of hour in which the car stays parked
    day_zone_idx: int = 0
        ID Day Zone (-1 if the car is outgoing)
    night_zone_idx: int = 0
        ID Night Zone (-1 if the car is incoming)
    charging_preference: int
        Charging preference (0 = night, 1 = day)
    charging_place_type: str
        Charging place preferred (home/work/other, public/semi-public/private)
    is_phev: bool
        Wheter the bev is actually a phev
    phev_autonomy: int
        the ......
    """
    battery_size: int # = 52  # Renault Zoe Data
    avg_consumption_kwh_km: float # = 0.177  # Renault Zoe Data
    soc: float
    starting_soc: float
    final_soc: float
    km_travelled_per_day: float
    parking_hours: int
    start_parking_time: int
    day_zone_idx: int = 0
    night_zone_idx: int = 0
    charging_preference: int
    charging_place_type: str
    is_phev: bool = False
    phev_actual_electrical_batt: Optional[int] = None

    def soc_discharge_prevision(self, km_travelled):
        """
        Given the current SoC and the kms the car is planning to travel, it returns the new expected SoC.

        Parameters
        ----------
        km_travelled: float
            Quantity of km that the car is going to travel.

        Returns
        -------
        expected_soc: float
            Expected new state of charge

        """
        return (km_travelled * self.avg_consumption_kwh_km) / self.battery_size * 100

    def travel(self, km_travelled=None):
        """
        Make the car travel for the specified kms or the default ones.

        Parameters
        ----------
        km_travelled: float (optional)
            Number of km to travel. If it is None, the number of km to travel will be equal to `km_travelled_per_day`

        Returns
        -------
        None

        """
        if km_travelled is None:
            km_travelled = self.km_travelled_per_day
        self.soc -= self.soc_discharge_prevision(km_travelled)
        self.soc = np.maximum(self.soc, 0)

    def charge(self, ratio_margin=1, soc_min=10):
        """
        Make the car recharge only if the planned travel for the next day do not make the car go under the
        `starting_soc` value.

        Parameters
        ----------
        ratio_margin: float (default 1)
            Ratio that adds a margin to the `starting_soc` value in the calculation.
        soc_min: float (default 10)
            Minimum state of charge as a threshold to make the car recharge.

        Returns
        -------
        kwh_charged: float
            kWh that the car needs from the grid to charge.

        """
        kwh_charged = 0
        prevision_soc = self.soc - self.soc_discharge_prevision(self.km_travelled_per_day)
        if self.soc < self.starting_soc * ratio_margin or prevision_soc <= soc_min:
            kwh_charged = np.maximum((self.final_soc - self.soc) / 100 * self.battery_size, 0)
        if kwh_charged > 0:
            self.soc = self.final_soc
        return kwh_charged


"""
Mapping of model name to model characteristics:
    1) battery_size: int (kW)
    2) avg_consumption_kwh_km: float (kWh/km)

    @TODO: this hardcoded values could be moved elsewhere
"""
name_model_characteristics_mapping: dict[str, EV_Model] = {
    "AB": EV_Model(avg_consumption_kwh_km=0.145, battery_size=43),
    "C": EV_Model(avg_consumption_kwh_km=0.165, battery_size=70),
    "DE": EV_Model(avg_consumption_kwh_km=0.153, battery_size=63),
    "phev": EV_Model(avg_consumption_kwh_km=0.171, battery_size=15),
}


"""
Mapping of model name to model percentage of use

@TODO: this hardcoded values could be moved elsewhere
"""
name_model_percentage_mapping: dict[str, float] = {
    "AB": 0.24,
    "C": 0.58,
    "DE": 0.18,
    #phev is dynamic
}
