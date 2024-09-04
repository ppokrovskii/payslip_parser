import os
from pathlib import Path
import re
import shutil

from pydantic import BaseModel

SOURCE_FOLDER = '.source_data'
TO_DO_FOLDER = '.to_do'
PROCESSED_FOLDER = '.processed'
os.makedirs(TO_DO_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)

class PayslipFile(BaseModel):
    name: str
    path: Path
    new_file_name: str = None
    new_file_path: Path = None

class FilesStorage:
    def delete_old_todos(self):
        for file in os.listdir(TO_DO_FOLDER):
            os.remove(os.path.join(TO_DO_FOLDER, file))

    def copy_source_to_todo(self):    
        for file in os.listdir(SOURCE_FOLDER):
            # check if target file already exists
            if os.path.exists(os.path.join(TO_DO_FOLDER, file)):
                continue
            source_file = os.path.join(SOURCE_FOLDER, file)
            target_file = os.path.join(TO_DO_FOLDER, file)
            
            # Copy the file to the target folder
            shutil.copy2(source_file, target_file)


    def get_todo_files(self):
        files = []
        for file in os.listdir(TO_DO_FOLDER):
            files.append(PayslipFile(name=file, path=Path(os.path.join(TO_DO_FOLDER, file))))
        return files
    
    def ensure_uniq_filename(self, filename, path):
        # check if path is Path and convert if required
        if not isinstance(path, Path):
            path = Path(path)
        new_path = path / filename
        # if the new path already exists, add a number to the filename or increase the number
        if new_path.exists():
            ext = filename.split('.')[-1]
            filename = filename.replace(f".{ext}", "")
            # get current number from the filename
            i_str = filename.split('_')[-1]
            if i_str.isdigit():
                i = int(i_str)
            else:
                i = 1
            i += 1
            filename = f"{filename}_{i}.{ext}"
            # return old folder with new name
            return filename
        return filename
    
    def rename_file(self, old_path, new_name):
        # if the new path already exists, add a number to the filename or increase the number
        new_name = self.ensure_uniq_filename(new_name, old_path.parent)
        new_path = old_path.parent / new_name
        os.rename(old_path, new_path)
        return new_path
    
    def move_file_to_processed(self, path):
        filename = path.name
        filename = self.ensure_uniq_filename(filename, PROCESSED_FOLDER)
        shutil.move(path, PROCESSED_FOLDER)