# ------------------------------------------------------------------
# Required Libraries & Constants
# ------------------------------------------------------------------

import os
import shutil
import time
from multiprocessing import Process, Queue
from pscad_utils import Sim, run_simulation, collect_results, convert_results_to_csv

# TEST CASES
ROCOF_TEST = 0
IBR_FAULT = 1
LOAD_FAULT = 2
LOAD_JUMP = 3

# FAULT CASES
NO_FAULT = 0
P2G_A = 1
P2G_B = 2
P2G_C = 3
P2G_AB = 4
P2G_AC = 5
P2G_BC = 6
P2G_ABC = 7
P2P_AB = 8
P2P_AC = 9
P2P_BC = 10
P2P_ABC = 11

# ------------------------------------------------------------------
# Simulation Cases and parameters
# ------------------------------------------------------------------

TIME_PARAMS = (6, 5, 250)  # duration (s), time-step (µs), sample-step (µs)
SIMULATIONS = []

sim1 = Sim("Base")
SIMULATIONS.append(sim1)

sim2 = Sim("LoadJump")
sim2.set_LOAD_JUMP()
sim2.load_p = 4
sim2.load_pf = 1
SIMULATIONS.append(sim2)

# ------------------------------------------------------------------
# Main entry-point
# ------------------------------------------------------------------
if __name__ == "__main__":
    print("************ Parallel Simulation START ************")

    # --- Configuration ----------------------------------------------------------
    SETTINGS = {"fortran_version": "GFortran 4.6.2"}
    FORTRAN_EXT = ".gf46"
    PROJECT_NAME = "GFMBESS20251112"

    WORKING_DIR = os.getcwd() + os.sep
    SIMULATIONS_DIR = os.path.join(WORKING_DIR, "all_simulations")

    # Clean/create output folder
    if os.path.exists(SIMULATIONS_DIR):
        shutil.rmtree(SIMULATIONS_DIR)
    os.makedirs(SIMULATIONS_DIR)

    # --- Launch workers ---------------------------------------------------------
    results_queue = Queue()
    processes = []

    for simulation in SIMULATIONS:
        p = Process(
            target=run_simulation,
            args=(
                simulation,
                results_queue,
                WORKING_DIR,
                PROJECT_NAME,
                SETTINGS,
                FORTRAN_EXT,
                SIMULATIONS_DIR,
                TIME_PARAMS,
            ),
        )
        processes.append(p)
        print(f"[START] {simulation.sim_name}")
        p.start()
        time.sleep(5)  # stagger launches to avoid PSCAD conflicts

    # --- Wait for completion ----------------------------------------------------
    for p in processes:
        p.join()

    # --- Collect results --------------------------------------------------------
    test_results = collect_results(results_queue)

    # --- Convert .psout → .csv --------------------------------------------------
    convert_results_to_csv(test_results, SIMULATIONS_DIR, WORKING_DIR)

    print("************ Parallel Simulation END ************")