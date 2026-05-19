import os
import sys
import time
import json
import subprocess
from datetime import datetime

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CMD_FILE = os.path.join(REPO_ROOT, "runner_cmd.json")
STATUS_FILE = os.path.join(REPO_ROOT, "runner_status.json")
LOG_FILE = os.path.join(REPO_ROOT, "runner_output.log")

def get_file_mtimes(paths):
    mtimes = {}
    for path in paths:
        if os.path.isdir(path):
            for root, dirs, files in os.walk(path):
                for f in files:
                    if f.endswith(".py"):
                        full_path = os.path.join(root, f)
                        try:
                            mtimes[full_path] = os.path.getmtime(full_path)
                        except Exception:
                            pass
        elif os.path.isfile(path):
            if path.endswith(".py"):
                try:
                    mtimes[path] = os.path.getmtime(path)
                except Exception:
                    pass
    return mtimes

def execute_cmd(cmd_str):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Executing: {cmd_str}")
    with open(LOG_FILE, "w", encoding="utf-8") as lf:
        lf.write(f"--- Running: {cmd_str} ---\n")
        lf.flush()
        
        env = os.environ.copy()
        env["PYTHONPATH"] = REPO_ROOT
        
        start_time = time.time()
        try:
            # We run subprocess and stream output to the log file in real-time
            process = subprocess.Popen(
                cmd_str,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                env=env,
                cwd=REPO_ROOT,
                text=True,
                encoding="utf-8",
                errors="replace"
            )
            
            while True:
                line = process.stdout.readline()
                if not line:
                    break
                sys.stdout.write(line)
                sys.stdout.flush()
                lf.write(line)
                lf.flush()
                
            process.wait()
            elapsed = time.time() - start_time
            status = "success" if process.returncode == 0 else "failed"
            lf.write(f"\n--- Finished: {status} in {elapsed:.2f}s (Exit code: {process.returncode}) ---\n")
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Done with status: {status}")
            return status, process.returncode
        except Exception as e:
            lf.write(f"\nError launching command: {e}\n")
            print(f"Error launching command: {e}")
            return "error", -1

def main():
    print("=" * 60)
    print(" Continuous Runner and File Watcher for 2Top Geometry ")
    print("=" * 60)
    print(f"Watching directory: {REPO_ROOT}")
    print(f"Command JSON file: {CMD_FILE}")
    print(f"Log file: {LOG_FILE}")
    print("=" * 60)
    
    # Initialize files
    if os.path.exists(CMD_FILE):
        try:
            os.remove(CMD_FILE)
        except Exception:
            pass
            
    with open(STATUS_FILE, "w") as f:
        json.dump({"status": "idle", "last_run": None}, f)
        
    watch_paths = [
        os.path.join(REPO_ROOT, "geometry"),
        os.path.join(REPO_ROOT, "tests"),
        os.path.join(REPO_ROOT, "tools")
    ]
    
    last_mtimes = get_file_mtimes(watch_paths)
    last_cmd_timestamp = 0.0
    
    # Periodic run parameters
    periodic_interval = None
    periodic_command = None
    last_periodic_run = 0.0
    
    # Check for command-line arguments for periodic run
    if len(sys.argv) > 2:
        for i in range(1, len(sys.argv) - 1):
            if sys.argv[i] == "--interval":
                try:
                    periodic_interval = float(sys.argv[i+1])
                except ValueError:
                    pass
            elif sys.argv[i] == "--command":
                periodic_command = sys.argv[i+1]
    
    # Run initial test on startup to verify state (unless periodic CLI overrides it)
    if not periodic_command:
        initial_cmd = "pytest tests/unit/test_verify_geometry_against_dataset.py"
        execute_cmd(initial_cmd)
    
    print("\nWatcher active. Change any python file or write to runner_cmd.json to run commands.\n")
    if periodic_command and periodic_interval:
        print(f"Running periodic command: '{periodic_command}' every {periodic_interval} seconds.\n")
    
    try:
        while True:
            time.sleep(1.0)
            
            # 1. Check for explicit command via runner_cmd.json
            if os.path.exists(CMD_FILE):
                try:
                    with open(CMD_FILE, "r") as f:
                        cmd_data = json.load(f)
                    
                    cmd_ts = cmd_data.get("timestamp", 0.0)
                    cmd_str = cmd_data.get("command")
                    p_interval = cmd_data.get("periodic_interval")
                    
                    if cmd_ts > last_cmd_timestamp:
                        last_cmd_timestamp = cmd_ts
                        
                        # If a periodic interval is specified, update periodic settings
                        if p_interval is not None:
                            periodic_interval = float(p_interval) if p_interval > 0 else None
                            periodic_command = cmd_str
                            last_periodic_run = 0.0  # trigger immediately
                            print(f"Updated periodic run: '{periodic_command}' every {periodic_interval}s")
                        else:
                            # Single-shot run
                            periodic_interval = None
                            periodic_command = None
                            
                            if cmd_str:
                                # Update status to running
                                with open(STATUS_FILE, "w") as sf:
                                    json.dump({"status": "running", "command": cmd_str, "start_time": time.time()}, sf)
                                    
                                status, code = execute_cmd(cmd_str)
                                
                                with open(STATUS_FILE, "w") as sf:
                                    json.dump({
                                        "status": status,
                                        "exit_code": code,
                                        "command": cmd_str,
                                        "finished_time": time.time()
                                    }, sf)
                            
                except Exception as e:
                    print(f"Error reading/parsing command file: {e}")
                    time.sleep(0.5)
                    
            # 2. Check for periodic run
            if periodic_interval and periodic_command:
                now = time.time()
                if now - last_periodic_run >= periodic_interval:
                    last_periodic_run = now
                    
                    # Update status to running
                    with open(STATUS_FILE, "w") as sf:
                        json.dump({
                            "status": "running",
                            "command": periodic_command,
                            "start_time": now,
                            "periodic": True
                        }, sf)
                        
                    status, code = execute_cmd(periodic_command)
                    
                    with open(STATUS_FILE, "w") as sf:
                        json.dump({
                            "status": status,
                            "exit_code": code,
                            "command": periodic_command,
                            "finished_time": time.time(),
                            "periodic": True
                        }, sf)
            
            # 3. Check for file changes (only when not running a periodic command)
            else:
                current_mtimes = get_file_mtimes(watch_paths)
                changed_files = []
                
                for path, mtime in current_mtimes.items():
                    if path not in last_mtimes or mtime > last_mtimes[path]:
                        if "continuous_runner" not in path and "runner_" not in path:
                            changed_files.append(path)
                            
                # Update cache
                last_mtimes = current_mtimes
                
                if changed_files:
                    print(f"\nDetected changes in: {[os.path.basename(f) for f in changed_files]}")
                    time.sleep(0.5)
                    auto_cmd = "pytest tests/unit/test_verify_geometry_against_dataset.py"
                    
                    with open(STATUS_FILE, "w") as sf:
                        json.dump({"status": "running", "command": auto_cmd, "start_time": time.time()}, sf)
                        
                    status, code = execute_cmd(auto_cmd)
                    
                    with open(STATUS_FILE, "w") as sf:
                        json.dump({
                            "status": status,
                            "exit_code": code,
                            "command": auto_cmd,
                            "finished_time": time.time()
                        }, sf)
                        
    except KeyboardInterrupt:
        print("\nContinuous runner stopped.")

if __name__ == "__main__":
    main()
