import tarfile
import tempfile
import difflib
import os
import shutil
from django.conf import settings

def clean_hana_metadata(lines):
    """
    Removes the HANA repo metadata from the first line so it doesn't trigger a false diff.
    """
    if not lines:
        return []
    first_line = lines[0].strip()
    if first_line and first_line[0].isdigit() and ('role' in first_line or 'hdbrole' in first_line):
        return lines[1:]
    return lines

def generate_diff(old_archive, new_archive):
    """Compares two .tgz files and returns a unified diff string, ignoring HANA noise."""
    diff_lines = []
    
    with tempfile.TemporaryDirectory() as old_dir, tempfile.TemporaryDirectory() as new_dir:
        with tarfile.open(old_archive, 'r:gz') as old_tar: old_tar.extractall(old_dir)
        with tarfile.open(new_archive, 'r:gz') as new_tar: new_tar.extractall(new_dir)
        
        for root, _, files in os.walk(new_dir):
            for file in files:
                new_file = os.path.join(root, file)
                rel_path = os.path.relpath(new_file, new_dir)
                normalized_path = rel_path.replace('\\', '/')
                
                if "archive-header" in normalized_path or "manifest.txt" in normalized_path or "ti/lists/" in normalized_path:
                    continue
                
                old_file = os.path.join(old_dir, rel_path)
                try:
                    with open(new_file, 'r', encoding='utf-8') as f: new_text = f.readlines()
                except UnicodeDecodeError:
                    continue 
                    
                if os.path.exists(old_file):
                    with open(old_file, 'r', encoding='utf-8') as f: old_text = f.readlines()
                else:
                    old_text = []
                    
                old_text_clean = clean_hana_metadata(old_text)
                new_text_clean = clean_hana_metadata(new_text)
                
                if old_text_clean == new_text_clean:
                    continue
                    
                file_diff = list(difflib.unified_diff(
                    old_text_clean, new_text_clean, 
                    fromfile=f"old/{normalized_path}", 
                    tofile=f"new/{normalized_path}", 
                    n=3
                ))
                
                if file_diff:
                    diff_lines.extend(file_diff)
                    diff_lines.append('\n')
                    
    return "".join(diff_lines) if diff_lines else "✅ No actual role changes detected."

def process_export_and_diff(hdbclient_dir, exported_filename, du_name):
    """Handles the comparison and updates the baseline in the baselines folder."""
    new_archive_path = os.path.join(hdbclient_dir, exported_filename)
    
    # Use the BASELINES_DIR defined in settings
    baselines_dir = getattr(settings, 'BASELINES_DIR', '.')
    baseline_path = os.path.join(baselines_dir, f"baseline_{du_name}.tgz")
    
    diff_text = ""
    if os.path.exists(baseline_path):
        diff_text = generate_diff(baseline_path, new_archive_path)
    else:
        diff_text = f"ℹ️ No previous baseline found for {du_name}. This will be saved as the first baseline."
        
    try:
        # Ensure the directory exists
        os.makedirs(os.path.dirname(baseline_path), exist_ok=True)
        shutil.copy2(new_archive_path, baseline_path)
    except Exception as e:
        diff_text += f"\n\n⚠️ Warning: Failed to save baseline: {str(e)}"
        
    return diff_text
