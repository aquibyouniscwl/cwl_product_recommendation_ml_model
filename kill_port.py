import os
import subprocess

def kill_port(port):
    try:
        output = subprocess.check_output(f"netstat -ano | findstr :{port}", shell=True).decode()
        for line in output.split('\n'):
            if 'LISTENING' in line:
                parts = line.strip().split()
                pid = parts[-1]
                print(f"Found process {pid} listening on port {port}. Killing...")
                os.system(f"taskkill /F /T /PID {pid}")
    except Exception as e:
        print("No process found on port 8000.")

kill_port(8000)
