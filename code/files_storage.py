import os
from pathlib import Path
import shutil

from pydantic import BaseModel

SOURCE_FOLDER = '.source_data'
RESULTS_FOLDER = '.results'
os.makedirs(RESULTS_FOLDER, exist_ok=True)

class PayslipFile(BaseModel):
    name: str
    path: Path

class FilesStorage:
    def delete_old_results(self):
        for file in os.listdir(RESULTS_FOLDER):
            os.remove(os.path.join(RESULTS_FOLDER, file))

    def copy_source_to_results(self):    
        for file in os.listdir(SOURCE_FOLDER):
            # check if target file already exists
            if os.path.exists(os.path.join(RESULTS_FOLDER, file)):
                continue
            source_file = os.path.join(SOURCE_FOLDER, file)
            target_file = os.path.join(RESULTS_FOLDER, file)
            
            # Copy the file to the target folder
            shutil.copy2(source_file, target_file)


    def get_files(self):
        files = []
        for file in os.listdir(RESULTS_FOLDER):
            files.append(PayslipFile(name=file, path=Path(os.path.join(RESULTS_FOLDER, file))))
        return files