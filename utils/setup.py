import csv
import os
import subprocess
import sys
import parameters
from datetime import datetime

LOG_FILE = "setup_log.txt"

def log(message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    full_message = f"[{timestamp}] {message}"
    print(full_message)
    with open(LOG_FILE, 'a', encoding='utf-8') as log_file:
        log_file.write(full_message + '\n')

def setup_environments(report_csv, folder):
    # Verifica iniziale delle cartelle
    if not os.path.exists(folder):
        log(f"ERRORE: Cartella principale '{folder}' non trovata")
        return

    # Leggi il CSV
    try:
        with open(report_csv, mode='r') as file:
            projects = list(csv.DictReader(file))
    except Exception as e:
        log(f"ERRORE lettura CSV: {str(e)}")
        return

    for idx, project in enumerate(projects, 1):
        project_name = project['Project']
        has_reqs = project['Requirements'].lower() == 'true'
        project_path = os.path.join(folder, project_name)
        
        log("\n" + "-"*50)
        log(f"[{idx}/{len(projects)}] Elaboro: {project_name}")

        if not has_reqs:
            log("  Salto: requirements=False nel CSV")
            continue
            
        if not os.path.exists(project_path):
            log(f"  ATTENZIONE: Cartella progetto non trovata in {project_path}")
            continue

        # Gestione ambiente virtuale
        venv_path = os.path.join(project_path, 'venv')
        
        # Rimozione venv esistente
        if os.path.exists(venv_path):
            log("  Rimuovo ambiente virtuale esistente...")
            try:
                subprocess.run(['rm', '-rf', venv_path], check=True)
            except subprocess.CalledProcessError:
                log("  ERRORE: rimozione venv fallita")
                continue

        # Creazione nuovo venv
        log("  Creo nuovo ambiente virtuale...")
        try:
            subprocess.run([sys.executable, '-m', 'venv', venv_path], check=True)
        except subprocess.CalledProcessError:
            log("  ERRORE: creazione venv fallita")
            continue

        # Installazione requirements
        pip_path = os.path.join(venv_path, 'bin', 'pip')
        
        # Cerco file di requirements
        req_files = [f for f in os.listdir(project_path) 
                   if f.lower().startswith('requirements') and f.lower().endswith('.txt')]
        
        if not req_files:
            log("  ATTENZIONE: Nessun file requirements*.txt trovato")
        else:
            for req_file in req_files:
                req_path = os.path.join(project_path, req_file)
                log(f"  Installo da {req_file}...")
                try:
                    subprocess.run([pip_path, 'install', '-r', req_path], check=True)
                except subprocess.CalledProcessError:
                    log(f"  ERRORE: installazione da {req_file} fallita")

        # Installazione Pynguin (se specificato)
        if hasattr(parameters, 'PYNGUIN'):
            log("  Installo Pynguin...")
            try:
                subprocess.run([pip_path, 'install', parameters.PYNGUIN], check=True)
            except subprocess.CalledProcessError:
                log("  ERRORE: installazione Pynguin fallita")

if __name__ == "__main__":
    # Inizializzazione log
    with open(LOG_FILE, 'w') as f:
        f.write("=== LOG SETUP AMBIENTI ===\n\n")
        
    setup_environments(parameters.REPORT, parameters.PROJECTS)