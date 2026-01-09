# ------------------------------------------------------------------
# Required Libraries
# ------------------------------------------------------------------

import os
import shutil
import time
from multiprocessing import Process, Queue
from pscad_utils import Sim, run_simulation, collect_results, convert_results_to_csv

# ------------------------------------------------------------------
# Simulation Cases and parameters
# ------------------------------------------------------------------
TIME_PARAMS = (5, 5, 250)  # duration (s), time-step (µs), sample-step (µs)
SIMULATIONS = []

sim1 = Sim("D_1000")
SIMULATIONS.append(sim1)

sim2 = Sim('D_100')
sim2.D = 1/100
SIMULATIONS.append(sim2)

sim3 = Sim("D_10")
sim3.D = 1/10
SIMULATIONS.append(sim3)

sim4 = Sim("D_1")
sim4.D = 1/1
SIMULATIONS.append(sim4)
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
        print(f"[START] {simulation.test_name}")
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