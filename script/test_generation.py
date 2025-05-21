import os
import sys
import subprocess
import csv
from datetime import datetime
from pyJoules.energy_meter import measure_energy
from pyJoules.device.rapl_device import RaplPackageDomain
from pyJoules.handler.pandas_handler import PandasHandler

def run_pynguin(venv_python, project_path, module_name, run_id, algorithm, maximum_search_time=180):

    env = os.environ.copy()
    env["PYNGUIN_DANGER_AWARE"] = "1"
    
    try:
        subprocess.run([
            venv_python, "-m", "pynguin",
            "--project-path", project_path,
            "--module-name", module_name,
            "--output-path", os.path.join(project_path, "pynguin_tests_EnergyConsumption", f"run_{run_id}"),
            "--maximum_search_time", str(maximum_search_time),
            "--maximum-iterations", str(1000),
            "--algorithm", algorithm,
            "--constant_seeding",
            "--seeded_primitives_reuse_probability", str(0.2),
            "--dynamic_constant_seeding",
            "--seeded_dynamic_values_reuse_probability", str(0.6),
            "--assertion-generation", "NONE",
            "--no-rich",
            "-v"
        ], check=True, env=env, timeout=60*10)
    except subprocess.TimeoutExpired:
        print(f"[TIMEOUT] Pynguin exceeded time limit for {module_name}")
        raise
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Pynguin failed for {module_name}: {e}")
        raise
    except Exception as e:
        print(f"[UNEXPECTED ERROR] in Pynguin for {module_name}: {e}")
        raise

def setup(project_path):
    venv_python = os.path.join(project_path, "venv", "bin", "python")
    
    if not os.path.exists(venv_python):
        print(f"[ERROR] Virtual environment not found at {venv_python}")
        return None

    try:
        print("[INFO] Installing required packages in virtual environment...")
        subprocess.run([
            venv_python, "-m", "pip", "install", "-q",
            "pyjoules", "pynguin==0.40.0", "pandas"
        ], check=True)

    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Failed to install dependencies in venv: {e}")
        return None
    
    return venv_python

def main():
    if len(sys.argv) != 7:
        print("Usage: python3 test_generation.py <project_path> <module_path> <output_dir> <algorithm> <timeout> <runs>")
        return

    print(f"[INFO] Running with args: {sys.argv}")
    has_errors = False

    project_path = sys.argv[1]
    module_path = sys.argv[2]
    output_dir = sys.argv[3]
    algorithm = sys.argv[4]
    timeout = int(sys.argv[5])
    runs = int(sys.argv[6])

    venv_python = setup(project_path)
    if venv_python is None:
        print("[ERROR] Failed to set up virtual environment.")
        return

    # Results directory
    os.makedirs(output_dir, exist_ok=True)

    # Module name 
    module_name = module_path.replace("/", ".").replace(".py", "")

    # Output CSV
    output_csv = os.path.join(output_dir, f"{module_name}_{algorithm}_generation.csv")
    with open(output_csv, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Run', 'Energy_Joules', 'Timestamp', 'Algorithm', 'Timeout'])

    domain = RaplPackageDomain(0)

    # Measure energy consumption
    for i in range(1, runs + 1):
        print(f"[INFO] Execution {i}/{runs} - Module: {module_name} - Algorithm: {algorithm} - Maximum Search Time: {timeout} seconds")
        pandas_handler = PandasHandler()

        @measure_energy(domains=[domain], handler=pandas_handler)
        def wrapped():
            run_pynguin(venv_python, project_path, module_name, i, algorithm, timeout)

        try:
            wrapped()
            energy_df = pandas_handler.get_dataframe()
            total_energy = energy_df['package_0'].sum()

        except Exception as e:
            print(f"[UNEXPECTED ERROR] Run {i} crashed: {e}")
            total_energy = -1
            has_errors=True
        
        finally:
            timestamp = datetime.now().isoformat()
            with open(output_csv, 'a', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([i, total_energy, timestamp, algorithm, timeout])


    print(f"[INFO] Results saved to {output_csv}")

    if has_errors:
        sys.exit(1)


if __name__ == "__main__":
    main()
