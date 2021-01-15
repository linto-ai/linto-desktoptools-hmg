import os
import sys

def getIconPath(caller: str, iconFileName: str):
    if getattr(sys, 'frozen', False):
        dir_path = os.path.dirname(sys.executable)
    else:
        dir_path = os.path.dirname(os.path.dirname(caller))
    
    return os.path.join(dir_path, iconFileName)