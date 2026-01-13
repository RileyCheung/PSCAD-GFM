# ------------------------------------------------------------------
# Required Libraries & Constants
# ------------------------------------------------------------------

import os
import shutil
import time
from multiprocessing import Process, Queue
from pscad_utils import Sim, run_simulation, collect_results, convert_results_to_csv

# ------------------------------------------------------------------
# Simulation Cases and parameters
# ------------------------------------------------------------------

TIME_PARAMS = (5, 10, 100)  # duration (s), time-step (µs), sample-step (µs)
SIMULATIONS = []

# sim1 = Sim("H2")
# sim1.set_LOAD_JUMP()
# sim1.load_p = 4
# sim1.load_pf = 1
# SIMULATIONS.append(sim1)

# sim2 =  Sim("H1_5")
# sim2.set_LOAD_JUMP()
# sim2.load_p = 4
# sim2.load_pf = 1
# sim2.H = 1.5
# SIMULATIONS.append(sim2)

# sim3 = Sim("H2_5")
# sim3.set_LOAD_JUMP()
# sim3.load_p = 4
# sim3.load_pf = 1
# sim3.H = 2.5
# SIMULATIONS.append(sim3)

for h in [1, 2, 3]:
    for d in [250, 100]:
        # Do something with h and d
        sim = Sim(f"H_{h}_D_{d}")
        sim.H = h
        sim.D = 1/d
        sim.set_LOAD_JUMP()
        sim.load_p = 4
        sim.load_pf = 1
        SIMULATIONS.append(sim)

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