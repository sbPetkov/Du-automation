import subprocess
import os
import glob
from .config import HDBCLIENT_DIR, HALM_USER, HALM_PASS

def run_cmd(args):
    env = os.environ.copy()
    if HALM_PASS:
        env["HDBALM_PASSWD"] = HALM_PASS
    try:
        result = subprocess.run(args, cwd=HDBCLIENT_DIR, capture_output=True, text=True, check=True, env=env)
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        return False, e.stderr or e.stdout

def list_dus(hostname, port):
    cmd = ["python", "-W", "ignore", "hdbalm3.py", "-s", "-h", hostname, "-p", str(port), "-u", HALM_USER, "du", "list"]
    return run_cmd(cmd)

def export_du(hostname, port, du_name):
    cmd = ["python", "-W", "ignore", "hdbalm3.py", "-s", "-h", hostname, "-p", str(port), "-u", HALM_USER, "fs_transport", "export", "-d", ".", du_name, "SchwarzIT"]
    success, output = run_cmd(cmd)
    
    if success:
        # Find the most recently downloaded .tgz file automatically
        tgz_files = glob.glob(os.path.join(HDBCLIENT_DIR, "*.tgz"))
        if tgz_files:
            latest_tgz = max(tgz_files, key=os.path.getctime)
            return True, os.path.basename(latest_tgz)
    return False, output

def get_latest_export(du_name):
    """Finds the most recent .tgz file for a specific DU name."""
    # Pattern looks for files exported by our tool: e.g. HANA_SIT_AM_TEN_RISE_2024...tgz
    # Or simply the latest .tgz in the directory if we don't have a strict naming convention yet.
    tgz_files = glob.glob(os.path.join(HDBCLIENT_DIR, "*.tgz"))
    if not tgz_files:
        return None
    
    # Filter files that contain the DU name if possible, otherwise just get latest
    matching_files = [f for f in tgz_files if du_name in os.path.basename(f)]
    target_list = matching_files if matching_files else tgz_files
    
    latest_tgz = max(target_list, key=os.path.getctime)
    return os.path.basename(latest_tgz)

def import_du(hostname, port, filename):
    cmd = ["python", "-W", "ignore", "hdbalm3.py", "-y", "-s", "-h", hostname, "-p", str(port), "-u", HALM_USER, "import", filename]
    return run_cmd(cmd)