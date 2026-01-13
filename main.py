# ------------------------------------------------------------------
# Required Libraries & Constants
# ------------------------------------------------------------------

import os
import shutil
import time
from multiprocessing import Process, Queue
from pscad_utils import Sim, run_simulation, collect_results, convert_results_to_csv

SETTINGS = {"fortran_version": "GFortran 4.6.2"}
FORTRAN_EXT = ".gf46"
PROJECT_NAME = "GFMBESS"
# ------------------------------------------------------------------
# Simulation Cases and parameters
# ------------------------------------------------------------------

TIME_PARAMS = (5, 10, 100)  # duration (s), time-step (µs), sample-step (µs)
SIMULATIONS = []

for h in [2]:
    for d in [10000, 1000, 100]:
        # Do something with h and d
        sim = Sim(f"H_{h}_D_{d}")
        sim.H = h
        sim.D = 1/d
        sim.set_LOAD_JUMP()
        sim.load_p = 3
        sim.load_pf = 1
        SIMULATIONS.append(sim)

# ------------------------------------------------------------------
# Main entry-point
# ------------------------------------------------------------------
if __name__ == "__main__":
    print("************ Parallel Simulation START ************")

    # --- Configuration ----------------------------------------------------------
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