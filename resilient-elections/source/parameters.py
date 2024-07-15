import pathlib
from dataclasses import dataclass

import numpy as np

## PARAMETERS ##
NUM_VOTERS = 1000
NUM_CANDIDATES = 100
COMMITTEE_SIZE = 10
NUM_ELECTIONS = 100  # Number of elections per radius
NUM_ITERATIONS = 100  # Number of augmented preferences to generate and compute distance of, for each instance
MAX_NUM_COMMITTEES = 100  # Number of tied committees considered in EXP2

percentage_power = 2
max_percentage = .1
percentage_changes = list(map(lambda x: round(x, 3),
                              np.power(np.linspace(0.0, max_percentage ** (1 / percentage_power), 15),
                                       percentage_power)))

this_directory = str(pathlib.Path(__file__).parent.resolve())
parent_directory = this_directory + "/.."
jsons_directory_path = parent_directory + "/jsons"
graphs_pdf_directory_path = parent_directory + "/graphs/pdfs/"
graphs_png_directory_path = parent_directory + "/graphs/pngs/"

PREF_IDS = ["1D", "2D", "Res"]
RULE_IDS = ["seqcc", "seqpav"]

MULTIPROCESSING = True  # Turn off for debugging purposes
WRITE_DATA = True  # Turn off for debugging purposes


@dataclass
class SamplingParameters:
    id: str
    dist_id: str
    euclid_resample: bool
    radius: float
    rho: float
    phi: float


# radius_list_1D = list(map(lambda x: round(x, 3), np.linspace(0.025, 0.08, 3)))
# radius_1D_to_2D = lambda radius: 1.08*np.sqrt(2*radius/np.pi)
# radius_list_2D = list(map(lambda x: round(radius_1D_to_2D(x), 3), radius_list_1D))

# Hardcode instead to give average approval numbers of 5%, 10%, and 15%, respectively
radius_list_1D = [0.025, 0.051, 0.078]
radius_list_2D = [0.134, 0.195, 0.244]

rho_list = list(map(lambda x: round(x, 3), np.linspace(0.05, 0.15, 3)))
phi_list = [0.75] * 3

parameter_list_1D = [SamplingParameters("1D", "1d_interval", False, radius, -1, -1) for radius in radius_list_1D]
parameter_list_2D = [SamplingParameters("2D", "2d_square", False, radius, -1, -1) for radius in radius_list_2D]
parameter_list_1D_res = [SamplingParameters("1D", "1d_interval", True, radius, -1, 0.1) for radius in radius_list_1D]
parameter_list_2D_res = [SamplingParameters("2D", "2d_square", True, radius, -1, 0.1) for radius in radius_list_2D]
parameter_list_Resampling = [SamplingParameters("Res", "", False, -1, rho, phi) for rho, phi in zip(rho_list, phi_list)]

parameter_list = parameter_list_1D + parameter_list_2D + parameter_list_1D_res + parameter_list_2D_res + parameter_list_Resampling
