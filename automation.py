import mhi.pscad
from mhi.pscad.utilities.file import File
from mhi.pscad.utilities.file import OutFile  
import os, shutil
import matplotlib.pyplot as plt
from multiprocessing import Process, Queue
import time

print("Automation Library:", mhi.pscad.VERSION)

def set_PrefA(PrefA_value, project):
    PrefA_slider = project.component(830232143)
    PrefA_slider.parameters(Value=PrefA_value)
    print(f"Successfully set PrefA = {PrefA_value}\n")
    return

def set_SCL(scl_value, project):
    SCL_slider = project.component(1715080837)
    SCL_slider.parameters(Value=scl_value)
    print(f"Successfully set SCL = {scl_value}\n")
    return

def process_outputs(psout_path):
    outfile = OutFile(psout_path)
    PBESS_NAME = "P - Bus 33A"
    PBESS_COL = outfile.column(PBESS_NAME)
    
    time_values = []
    PBESS = []
    
    with outfile as data:
        next(data)
        for values in data:
            time_values.append(float(values[0]))
            PBESS.append(float(values[PBESS_COL]))
    
    return time_values, PBESS

def run_simulation(test_name, result_queue, prefA_value, SCL_value, working_dir, src_folder, dst_folder, project_name, settings, fortran_ext):
    try:
        # 1) launch pscad with settings
        pscad = mhi.pscad.launch(version = '5.0.2', settings = settings)
        if not pscad:
            raise RuntimeError(f'Failed to launch PSCAD')
        
        # 2) launch project
        pscad.load([working_dir + project_name + ".pscx"])
        project = pscad.project(project_name)
        main = project.canvas('Main')

        # 3) set parameters for simulation
        set_PrefA(prefA_value, main)
        set_SCL(SCL_value, main)

        # 4) Run simulation
        project.run()

        # 5) Process outputs
        test_folder = os.path.join(dst_folder, test_name)
        File.move_files(src_folder, test_folder, ".out", ".inf")
        psout_path = os.path.join(test_folder, "Test1")

        # 6) Send data back to main process with queue
        result_queue.put({
            'psout_path' : psout_path,
            'test_name' : test_name,
            'success' : True
        })

        # 7) Clean up
        print(f'Process : {test_name} was successful, now closing \n')
        pscad.quit()

    except Exception as e:
        print(f'Process : {test_name} was unsuccessful, now closing \n')
        result_queue.put({
            'success': False,
            'error': str(e)
        })


if __name__ == '__main__':
    # pscad project settings
    settings = {'fortran_version': 'GFortran 4.6.2'}
    fortran_ext = '.gf46'
    project_name = 'GFMBESS20251112'
    working_dir = os.getcwd() + "\\"
    src_folder = working_dir + project_name + fortran_ext
    dst_folder = working_dir + "POW_output"

    # Clean output folder
    if os.path.exists(dst_folder):
        shutil.rmtree(dst_folder)
    os.mkdir(dst_folder)

    # parameters to parallelise
    prefa_values = [0, 0, 0]
    scl_values = [20, 10, 5]
    test_names = ['SCL20', 'SCL10', 'SCL5']
    num_processes = len(test_names)
    results_queue = Queue() # to store data

    # create processes
    processes = []
    for prefA_value, scl_value, test_name in zip(prefa_values, scl_values, test_names):

        p = Process(
            target=run_simulation,
            args=(test_name, results_queue, prefA_value, scl_value, working_dir, src_folder, dst_folder, project_name, settings, fortran_ext)
        )
        processes.append(p)
        p.start() #
        time.sleep(2) # Small delay to avoid PSCAD conflicts

    # wait for all processes to finished
    for p in processes:
        p.join()

    # collect results
    psout_paths = []
    while not results_queue.empty():
        result = results_queue.get()    
        if(result['success']):
            psout_paths.append(result['psout_path'])

    pbess_data = []
    time_data = None
    for path in psout_paths:
        time_data, pbess = process_outputs(path)
        pbess_data.append(pbess)

     # Create plot
    colours = ['b-', 'r-', 'g-']
    plt.figure(figsize=(10, 6))
    for i in range(num_processes):
        plt.plot(time_data, pbess_data[i], colours[i], linewidth=1, label=test_names[i])
    plt.xlabel('Time (s)')
    plt.ylabel('Power (MW)')
    plt.title('PBESS vs Time')
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.show()