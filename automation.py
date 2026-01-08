# ------------------------------------------------------------------
# Required Libraries
# ------------------------------------------------------------------

import os
import shutil
import time
from multiprocessing import Process, Queue
import mhi.pscad
from mhi.pscad.utilities.file import File, OutFile


# ------------------------------------------------------------------
# Helper functions to update component parameters
# ------------------------------------------------------------------
def set_PrefA(value: float, project) -> None:
    """Update the PrefA slider value."""
    slider = project.component(830232143)
    slider.parameters(Value=value)
    print(f"[INFO] PrefA set to {value}")


def set_SCL(value: float, project) -> None:
    """Update the SCL slider value."""
    slider = project.component(1715080837)
    slider.parameters(Value=value)
    print(f"[INFO] SCL set to {value}")


# ------------------------------------------------------------------
# Single simulation worker
# ------------------------------------------------------------------
def run_simulation(
    test_name: str,
    queue: Queue,
    prefA: float,
    scl: float,
    working_dir: str,
    project_name: str,
    settings: dict,
    fortran_ext: str,
    sim_folder: str,
    time_params: tuple,
) -> None:
    """
    Worker process that:
      1. Creates a unique case folder.
      2. Copies the master .pscx file into it.
      3. Launches PSCAD, loads the project, sets parameters, and runs.
      4. Returns the path to the .psout file via the provided queue.
    """
    try:
        # --- 1. Prepare case folder -------------------------------------------------
        master = os.path.join(working_dir, f"{project_name}.pscx")
        case = os.path.join(sim_folder, test_name)
        if os.path.exists(case):
            shutil.rmtree(case)
        os.makedirs(case)
        shutil.copy(master, case)

        # --- 2. Launch PSCAD and load project ---------------------------------------
        pscad = mhi.pscad.launch(version="5.0.2", settings=settings)
        if not pscad:
            raise RuntimeError("Failed to launch PSCAD")

        pscad.load([os.path.join(case, f"{project_name}.pscx")])
        project = pscad.project(project_name)
        project.parameters(
            output_filename=test_name,
            time_duration=time_params[0],
            time_step=time_params[1],
            sample_step=time_params[2],
        )
        main = project.canvas("Main")

        # --- 3. Set parameters and run ---------------------------------------------
        set_PrefA(prefA, main)
        set_SCL(scl, main)

        print(f"[RUN] {test_name}")
        project.run()

        psout_path = os.path.join(case, f"{project_name}{fortran_ext}", test_name)

        # --- 4. Signal success -------------------------------------------------------
        queue.put({
            "psout_path": psout_path, 
            "test_name": test_name, 
            "success": True})
        print(f"[OK ] {test_name} completed successfully")

        pscad.quit()

    except Exception as e:
        print(f"[ERR] {test_name} failed: {e}\n")
        queue.put({"success": False, "error": str(e)})


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

    # Simulation matrix
    TIME_PARAMS = (12, 20, 250)          # duration (s), time-step (µs), sample-step (µs)
    PREFA_VALUES = [0, 0, 0]
    SCL_VALUES = [20, 10, 2]
    TEST_NAMES = ["SCL20", "SCL10", "SCL2"]

    # --- Launch workers ---------------------------------------------------------
    results_queue = Queue()
    processes = []

    for prefA, scl, name in zip(PREFA_VALUES, SCL_VALUES, TEST_NAMES):
        p = Process(
            target=run_simulation,
            args=(
                name,
                results_queue,
                prefA,
                scl,
                WORKING_DIR,
                PROJECT_NAME,
                SETTINGS,
                FORTRAN_EXT,
                SIMULATIONS_DIR,
                TIME_PARAMS,
            ),
        )
        processes.append(p)
        print(f"[START] {name}")
        p.start()
        time.sleep(5)  # stagger launches to avoid PSCAD conflicts

    # --- Wait for completion ----------------------------------------------------
    for p in processes:
        p.join()

    # --- Collect results --------------------------------------------------------
    print("[INFO] Collecting results...")
    test_results = []
    while not results_queue.empty():
        res = results_queue.get()
        if res.get("success"):
            test_results.append(res)

    # --- Convert .psout → .csv --------------------------------------------------
    for case in test_results:
        psout = case["psout_path"]
        name = case["test_name"]
        csv_name = f"{name}.csv"

        os.chdir(os.path.join(SIMULATIONS_DIR, name))
        OutFile(psout).toCSV(csv_name)
        os.chdir(WORKING_DIR)
        print(f"[SAVE] {csv_name}")

    print("************ Parallel Simulation END ************")