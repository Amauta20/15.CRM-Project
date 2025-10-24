
import os
import shutil
from pathlib import Path

DRIVE_ROOT = Path("C:/CRM_Drive") # This will be the root of our local "drive"

def upload_file(opportunity_id, file_path):
    """
    Uploads a file to the 'drive' for a specific opportunity.
    
    For now, it copies the file to a local directory structure.
    DRIVE_ROOT/opportunity_{opportunity_id}/<filename>
    """
    
    opportunity_folder = DRIVE_ROOT / f"opportunity_{opportunity_id}"
    opportunity_folder.mkdir(parents=True, exist_ok=True)
    
    destination_path = opportunity_folder / Path(file_path).name
    
    shutil.copy(file_path, destination_path)
    
    return str(destination_path), str(opportunity_folder)

