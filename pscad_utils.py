# ------------------------------------------------------------------
# PSCAD Automation Utilities Library & Constants
# ------------------------------------------------------------------

import os
import shutil
from multiprocessing import Queue
import mhi.pscad
from mhi.pscad.utilities.file import OutFile

# ------------------------------------------------------------------
# Simulation Base Case
# ------------------------------------------------------------------

class Sim:
    def __init__(
            self, 
            sim_name, 
            prefA = 0, 
            scl = 5, 
            xr = 5, 
            H = 2, 
            D = 0.001, 
            fdroop = 0.01, 
            inverter_size = 1.1, 
            no_inverters = 1, 
            POD_en = 0, 
            line_length = 1, 
            test_case = 0, # default ROCOF test
            fault_type = 1,
            fault_time = 4,
            fault_duration = 0.05,
            rocof_mag = 1 
            ):
        self.sim_name = sim_name
        self.prefA = prefA # plant acitve power setpoint (pu)
        self.scl = scl # grid short circuit level
        self.xr = xr # grid x/r ratio
        self.H = H # inertia
        self.D = D # damping
        self.fdroop = fdroop
        self.inverter_size = inverter_size # capacity of single inverter module (MVA)
        self.no_inverters = no_inverters # parallel inverters in plant
        self.POD_en = POD_en # Power oscillation damper
        self.line_length = line_length # Transmission line length between IBR and grid (m)
        self.rocof_mag = rocof_mag # grid rocof value for rocof test
        
        self.test_case = test_case # rocof, fault, etc
        self.fault_type = fault_type # used for both ibr and load faults
        self.fault_time = fault_time
        self.fault_duration = fault_duration
        self.load_p = 1 # load value (MW)
        self.load_pf = 1 # power factor of load

            # TEST CASES
        self.ROCOF_TEST = 0
        self.IBR_FAULT_TEST = 1
        self.LOAD_FAULT_TEST = 2
        self.LOAD_JUMP_TEST = 3
            # FAULT CASES
        self.NO_FAULT = 0
        self.P2G_A = 1
        self.P2G_B = 2
        self.P2G_C = 3
        self.P2G_AB = 4
        self.P2G_AC = 5
        self.P2G_BC = 6
        self.P2G_ABC = 7
        self.P2P_AB = 8
        self.P2P_AC = 9
        self.P2P_BC = 10
        self.P2P_ABC = 11
        
    def set_ROCOF(self, user_rocof = 1):
        self.test_case = self.ROCOF_TEST
        self.rocof_mag = user_rocof
    def set_IBR_FAULT(self):
        self.test_case = self.IBR_FAULT_TEST
    def set_LOAD_FAULT(self):
        self.test_case = self.LOAD_FAULT_TEST
    def set_LOAD_JUMP(self):
        self.test_case = self.LOAD_JUMP_TEST
# ------------------------------------------------------------------
# Component Parameter Setters
# ------------------------------------------------------------------

def set_PrefA(value: float, project) -> None:
    """Update the PrefA slider value."""
    slider = project.component(830232143)
    slider.parameters(Value=value)
    print(f"[INFO] PrefA set to {value} (pu)")

def set_SCL(value: float, project) -> None:
    """Update the SCL slider value."""
    slider = project.component(1715080837)
    slider.parameters(Value=value)
    print(f"[INFO] SCL set to {value}")

def set_XR_ratio(value: float, project) -> None:
    """Update the grid X/R slider value."""
    grid_model = project.component(1186628671)
    slider = grid_model.canvas().component(1448664316)
    slider.parameters(Value=value)
    print(f"[INFO] X/R set to {value}")

def set_H(value: float, project) -> None:
    """Update the inertia constant H of the VSM controller """
    BESS_plant0 = project.component(477036609).canvas()
    BESS_plant1 = BESS_plant0.component(1672393785).canvas()
    inverter_model = BESS_plant1.component(102488955).canvas()
    converter_controls = inverter_model.component(952269080).canvas()
    slider_H = converter_controls.component(999528713) 
    slider_H.parameters(Value=value)
    print(f"[INFO] H set to {value}")

def set_D(value: float, project) -> None:
    """Update the Dammping D of the VSM controller """
    BESS_plant0 = project.component(477036609).canvas()
    BESS_plant1 = BESS_plant0.component(1672393785).canvas()
    inverter_model = BESS_plant1.component(102488955).canvas()
    converter_controls = inverter_model.component(952269080).canvas()
    slider_D = converter_controls.component(445867551) 
    slider_D.parameters(Value=value)
    print(f"[INFO] D set to {value}")

def set_fdroop(value: float, project) -> None:
    """Update the frequency droop of the BESS plant """
    BESS_plant0 = project.component(477036609).canvas()
    BESS_plant1 = BESS_plant0.component(1672393785).canvas()
    slider_fdroop = BESS_plant1.component(1505948255) 
    slider_fdroop.parameters(Value=value)
    print(f"[INFO] Fdroop set to {value}")

def set_inverter_size(value: float, project) -> None:
    """Update the single inverter Sbase (MVA) """
    BESS_plant0 = project.component(477036609).canvas()
    BESS_plant1 = BESS_plant0.component(1672393785).canvas()
    inverter_size_constant = BESS_plant1.component(1643639519) 
    inverter_size_constant.parameters(Value=value)
    print(f"[INFO] Single Inverter Sbase set to {value} (MVA)")

def set_no_inverters(value: int, project) -> None:
    """Update the number of inverters comprising BESS """
    BESS_plant0 = project.component(477036609).canvas()
    no_inverter_int = BESS_plant0.component(1834444465) 
    no_inverter_int.parameters(Value=value)
    print(f"[INFO] Number of Inverters set to {value}")

def set_POD(value: float, project) -> None:
    """Update the Power Oscillation Damper functionality """
    BESS_plant0 = project.component(477036609).canvas()
    BESS_plant1 = BESS_plant0.component(1672393785).canvas()
    inverter_model = BESS_plant1.component(102488955).canvas()
    converter_controls = inverter_model.component(952269080).canvas()
    POD_en_switch = converter_controls.component(2046559337) 
    POD_en_switch.parameters(Value=value)
    print(f"[INFO] POD_en set to {value}")

def set_line_length(value: float, project) -> None:
    """Update transmission line length between IBR and SMIB """
    transmission_line = project.component(591664577)
    transmission_line.parameters(len=value)
    print(f"[INFO] Transmission line length set to {value} (m)")

def clear_test_env(project) -> None:
    """Clears all faults, loads, frequency conditions"""
    # Faults and loads
    IBR_flt_switch = project.component(1330750280)
    IBR_flt_switch.parameters(Value = 0)
    load_flt_switch = project.component(1967375294)
    load_flt_switch.parameters(Value = 0)
    grid_cb = project.component(1040814752)
    grid_cb.parameters(Value = 0)
    load_cb = project.component(127299003)
    load_cb.parameters(Value = 1)

    # frequency ramp disabled
    grid_model = project.component(1186628671).canvas()
    RoCoF_en = grid_model.component(593429605)
    RoCoF_en.parameters(G = 0) # multiplying constant
    print(f"[INFO] Cleared Simulation Environment")
    
def set_test_case_paramters(sim: Sim, project) -> None:
    match sim.test_case:
        case sim.ROCOF_TEST:
            grid_model = project.component(1186628671).canvas()
            RoCoF_en = grid_model.component(593429605)
            RoCoF_en.parameters(G = sim.rocof_mag) # multiplying constant
            print(f"[INFO] RoCoF test: Enabled")

        case sim.IBR_FAULT_TEST:
            print("[INFO] IBR fault test enabled")
            if( sim.fault_type > sim.P2P_ABC or sim.fault_type < sim.NO_FAULT ):
                    print("[ERR] IBR Fault : Invalid fault code")
                    return
            IBR_flt = project.component(1330750280) # sets fault type
            IBR_flt.parameters(Value = sim.fault_type)
            IBR_flt_logic = project.component(754742834)
            IBR_flt_logic.parameters(TF = sim.fault_time, DF = sim.fault_duration)
            print(f"[INFO] Set IBR Fault : {sim.fault_type}")
            
        case sim.LOAD_FAULT_TEST:
            print("[INFO] Load fault test enabled")
            if( sim.fault_type > sim.P2P_ABC or sim.fault_type < sim.NO_FAULT ):
                    print("[ERR] Load Fault : Invalid fault code")
                    return
            Load_flt = project.component(1967375294) # sets fault type
            Load_flt.parameters(Value = sim.fault_type)
            LOAD_flt_logic = project.component(1952267882)
            LOAD_flt_logic.parameters(TF = sim.fault_time, DF = sim.fault_duration)
            print(f"[INFO] Set load Fault : {sim.fault_type}")

        case sim.LOAD_JUMP_TEST:
            load_cb = project.component(127299003)
            load_cb.parameters(Value = 0)
            print("[INFO] Load jump test enabled")
            pload = project.component(1379641378)
            pload.parameters(Value = sim.load_p) # (in MW)
            pf = project.component(1806668041)
            pf.parameters(Value = sim.load_pf)
            print(f"[INFO] Load set : P = {sim.load_p} (MW) @ pf = {sim.load_pf}")
        
        case _:
            raise ValueError(f"Unknown test case {sim.test_case}")

# ------------------------------------------------------------------
# Simulation Worker
# ------------------------------------------------------------------
def run_simulation(
    sim : Sim,
    queue: Queue,
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
        case = os.path.join(sim_folder, sim.sim_name)
        if os.path.exists(case):
            shutil.rmtree(case)
        os.makedirs(case)
        shutil.copy(master, case)

        # --- 2. Launch PSCAD and load project ---------------------------------------
        pscad = mhi.pscad.launch(version="5.0.2", settings=settings)
        if not pscad:
            raise RuntimeError("[ERR] Failed to launch PSCAD")

        pscad.load([os.path.join(case, f"{project_name}.pscx")])
        project = pscad.project(project_name)
        project.parameters(
            output_filename=sim.sim_name,
            time_duration=time_params[0],
            time_step=time_params[1],
            sample_step=time_params[2],
        )
        main = project.canvas("Main")

        # --- 3. Set parameters and run ---------------------------------------------
        clear_test_env(main)
        set_PrefA(sim.prefA, main)
        set_SCL(sim.scl, main)
        set_XR_ratio(sim.xr, main)
        set_H(sim.H, main)
        set_D(sim.D, main)
        set_fdroop(sim.fdroop, main)
        set_POD(sim.POD_en, main)
        set_inverter_size(sim.inverter_size, main)
        set_no_inverters(sim.no_inverters, main)
        set_line_length(sim.line_length, main)
        set_test_case_paramters(sim, main)

        print(f"[RUN] {sim.sim_name}")
        project.run()

        psout_path = os.path.join(case, f"{project_name}{fortran_ext}", sim.sim_name)

        # --- 4. Signal success -------------------------------------------------------
        queue.put({
            "psout_path": psout_path,
            "test_name": sim.sim_name,
            "success": True
        })
        print(f"[OK ] {sim.sim_name} completed successfully")

        pscad.quit()

    except Exception as e:
        print(f"[ERR] {sim.sim_name} failed: {e}\n")
        queue.put({"success": False, "error": str(e)})


# ------------------------------------------------------------------
# Result Processing
# ------------------------------------------------------------------

def collect_results(results_queue: Queue) -> list:
    """
    Collect all successful simulation results from the queue.
    
    Args:
        results_queue: Multiprocessing queue containing simulation results
        
    Returns:
        List of successful test result dictionaries
    """

    print("[INFO] Collecting results...")
    test_results = []
    while not results_queue.empty():
        res = results_queue.get()
        if res.get("success"):
            test_results.append(res)
    return test_results

def convert_results_to_csv(test_results: list, simulations_dir: str, working_dir: str) -> None:
    """
    Convert .psout files to CSV format for all successful test cases.
    
    Args:
        test_results: List of result dictionaries from completed simulations
        simulations_dir: Directory containing all simulation folders
        working_dir: Base working directory to return to
    """
    for case in test_results:
        psout = case["psout_path"]
        name = case["test_name"]
        csv_name = f"{name}.csv"

        os.chdir(os.path.join(simulations_dir, name))
        OutFile(psout).toCSV(csv_name)
        os.chdir(working_dir)
        print(f"[SAVE] {csv_name}")


