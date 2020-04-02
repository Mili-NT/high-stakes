import os
import random
from platform import system

def get_files(root_dir, number_of_files_bet):
    def spider_current_level(current_dir):
        # Get all directories and files in the current level
        dirs = [subdir for subdir in os.listdir(current_dir) if os.path.isdir(subdir)]
        files = [f"{current_dir}/{f}" for f in os.listdir(current_dir) if os.path.isfile(f)]
        # If len(dirs) == 0, we've exhausted that path branch
        for subdir in dirs:
            # We simply recurse and spider all the subdirectories
            spider_current_level(dirs)

    spider_current_level(root_dir)

def outcome(win, bet):
    top_level_dirs = {'Windows':'C:\\', 'Linux':'/'}
