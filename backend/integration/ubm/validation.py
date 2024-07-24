# %%

import numpy as np
import yaml
from geopandas import GeoDataFrame

from ubm.enact_pop import add_enact_pop_stat_to_gdf
from ubm.mobility import download_datasets
from ubm.utils.stuff import load_yaml
from ubm.zoning import shapefile_path_to_geodataframe

# TODO: Limit solutions

def objective_f(gdf: GeoDataFrame):
    error = abs(gdf['istat_pop_'] - gdf['enact_pop_night_ratio']) / gdf['enact_pop_night_ratio']
    return error.sum()


def random_population(n_chromosomes: int, lenght: int = 22):
    population = np.random.rand(n_chromosomes, lenght)
    matrix = np.zeros((n_chromosomes, 49), dtype=np.float32)
    matrix[:, 1:lenght + 1] = population
    return matrix_to_dict_list(matrix)


def mutated_population(best_solution, n_chromosomes: int, lenght: int = 22, n_mutation: int = 2):
    indexes = np.random.randint(1, lenght + 1, (n_chromosomes, n_mutation))
    array_dict = []
    mutation = np.random.rand(n_chromosomes, n_mutation)
    for i in range(n_chromosomes):
        new_solution = best_solution.copy()
        for j in range(n_mutation):
            new_solution[indexes[i][j]] = float(mutation[i][j])
        array_dict.append(new_solution)
    array_dict.append(best_solution.copy())
    return array_dict


def matrix_to_dict_list(matrix):
    array_dict = []
    ranges = list(range(0, 49))
    for line in matrix:
        array_dict.append(dict(zip(ranges, line)))
    return array_dict


# %%
input = "./input/turin.yaml"
config = "./config/test_wp2.yaml"
# %%
download_datasets()
# Load Input Data and Behaviour
input_data = load_yaml(input)
behaviour = load_yaml(config)
# %%
# Loading Zoning and augmenting it with JRC's ENACT-POP data
filename = input_data['zoning_shp_path']
gdf = shapefile_path_to_geodataframe(filename)
best_score = np.Inf
corine_dict_night = load_yaml('./config/corine_night.yaml')
gdf = add_enact_pop_stat_to_gdf(gdf, corine_dict_night=corine_dict_night)
print(f"Baseline Objective: {objective_f(gdf)}")
n_ch = 10
n_mutation = 5
n_epoch = 100
# %%
# pop = mutated_population(corine_dict_night, n_ch, n_mutation=n_mutation)
pop = random_population(n_ch)
for epoch in range(n_epoch):
    scores = {}
    for i, sol in enumerate(pop):
        print(f"{i}")
        gdf = add_enact_pop_stat_to_gdf(gdf, corine_dict_night=sol)
        scores[i] = objective_f(gdf)
    # TODO: Take best X solutions
    # TODO: Crossovers
    ordered = sorted(scores.items(), key=lambda item: item[1])
    best_sol_idx = ordered[0][0]
    best_sol = pop[best_sol_idx]
    if ordered[0][1] < best_score:
        print(f"New Best! Error Score: {ordered[0][1]:.5f}")
        best_score = ordered[0][1]
        with open('best_sol.yml', 'w') as outfile:
            out_best_sol = {}
            for key in best_sol.keys():
                out_best_sol[key] = float(best_sol[key])
            yaml.dump(out_best_sol, outfile)
    pop = mutated_population(best_sol, n_ch, n_mutation=n_mutation)