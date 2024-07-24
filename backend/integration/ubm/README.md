# INCIT-EV UB&M Module

Branch used to implement this module inside a Docker container.

`ubm` is a Python library implemented in the context of WP6 Task 3 of INCIT-EV H2020 European project.

It allows the user to calculate Mobility and User Charging Behaviour by using very simple user inputs and a set of
dataset publicly available.

## Development

This part of the guide will guide you to the set up of the environment to work and use the library.

### Poetry (preferred)

#### Requirements

- Python ^3.9
- [Poetry](https://python-poetry.org/)
- [GDAL](https://gdal.org/) ([Installation Guide on Ubuntu](https://mothergeo-py.readthedocs.io/en/latest/development/how-to/gdal-ubuntu-pkg.html#))

The default procedure to create the Python environment to use this library is represented
by [Poetry](https://python-poetry.org/), a Python packaging and dependency manager.

Please follow the [documentation](https://python-poetry.org/docs/) to install this tool.

After that, you will need just to clone the repository, enter in the root folder of the repository and
type `poetry install` in your terminal.

### Others

> e.g., pip, pipenv, virtualenv

#### Requirements

- Python ^3.9
- [GDAL](https://gdal.org/) ([Installation Guide on Ubuntu](https://mothergeo-py.readthedocs.io/en/latest/development/how-to/gdal-ubuntu-pkg.html#))

The [Poetry](#poetry-preferred) is preferred, but the repository contains also the `requirements.txt` file to install
the dependencies in your favourite Python packaging and dependency manager with the evergreen:

```shell
pip install -r requirements.txt
```

## Usage

An example of usage is provided in the `main.py` folder, listed here for simplicity.

```python
import numpy as np

from ubm.car_parking import calculate_car_parked
from ubm.charging import charging_behaviour_sim
from ubm.enact_pop import add_enact_pop_stat_to_gdf
from ubm.surveys import calculate_bevs_phevs_percentage
from ubm.utils.stuff import load_yaml
from ubm.zoning import shapefile_path_to_geodataframe


def get_trips_info(input_data):
    return np.asarray(input_data['total_urban_trips']), np.asarray(input_data['total_incoming_trips']), np.array(
        np.asarray(input_data['total_outgoing_trips'])), np.asarray(input_data['average_number_trips'])


def generate_csv(impact, parking, folder="./output_sample/"):
    impact_m = impact.mean
    parking_m = parking.mean
    np.savetxt(f"{folder}impact_kw_mean_7_days.csv", impact_m, delimiter=',', fmt="%.2f")
    np.savetxt(f"{folder}parking_all_mean_7_days.csv", parking_m.sum(axis=0), delimiter=',', fmt="%.2f")

    for h_i, hour in enumerate(parking_m):
        np.savetxt(f"{folder}parking_{h_i}h_mean_7_days.csv", hour, delimiter=',', fmt="%.2f")


def main():
    # Load Input Data and Behaviour
    input_data = load_yaml('input/turin.yaml')
    behaviour = load_yaml('config/test_wp2.yaml')

    # Loading Zoning and augmenting it with JRC's ENACT-POP data
    filename = input_data['zoning_shp_path']
    gdf = shapefile_path_to_geodataframe(filename)
    gdf = add_enact_pop_stat_to_gdf(gdf)

    # Get Information about Trips and Vehicles
    urban_trips, in_trips, out_trips, avg_n_trips = get_trips_info(input_data)
    gdf = calculate_bevs_phevs_percentage(gdf, input_data)
    gdf = calculate_car_parked(gdf, urban_trips, in_trips, out_trips, avg_n_trips)

    # Simulate Charging Behaviour
    impact, parking = charging_behaviour_sim(gdf, behaviour, max_epoch=10000, simulation_days=7)
    generate_csv(impact, parking, folder="./output_sample/turin/start_parking/output/")
    pass

```


## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## License

[MIT](https://choosealicense.com/licenses/mit/)

# Appendix A: Windows GDAL error fix

1. Run the first time `poetry install` will return an error. Despite that, open a terminal with the poetry virtualenv activated.
2. Download and put in the UBM folder this three wheels:
    - [GDAL](https://www.lfd.uci.edu/~gohlke/pythonlibs/#gdal) - Suggestion: **GDAL‑3.3.1‑cp39‑cp39‑win_amd64.whl**
    - [Fiona](https://www.lfd.uci.edu/~gohlke/pythonlibs/#fiona) - Suggestion: **Fiona‑1.8.20‑cp39‑cp39‑win_amd64.whl**
    - [rasterio](https://www.lfd.uci.edu/~gohlke/pythonlibs/#rasterio) - Suggestion: **rasterio‑1.2.6‑cp39‑cp39‑win_amd64.whl**
3. Install the package using `pip install .\GDAL-3.3.1-cp39-cp39-win_amd64.whl .\Fiona-1.8.20-cp39-cp39-win_amd64.whl .\rasterio-1.2.6-cp39-cp39-win_amd64.whl`
4. Run `poetry update -vv`
5. The code will run as expected!

# Appendix B: use_2to3 is invalid.
```bash
/home/macaluso/dev/incit-ev/ubm/.venv/lib/python3.9/site-packages/setuptools/_distutils/dist.py:275: UserWarning: Unknown distribution option: 'use_2to3_fixers'
 warnings.warn(msg)
/home/macaluso/dev/incit-ev/ubm/.venv/lib/python3.9/site-packages/setuptools/_distutils/dist.py:275: UserWarning: Unknown distribution option: 'use_2to3_exclude_fixers'
 warnings.warn(msg)
error in GDAL setup command: use_2to3 is invalid.
[end of output]
```

1. `poetry shell`
2. `pip install setuptools==57.5.0`
3. `poetry install`
