#Python 3.13.2 64-bit(pip v.26.0.1)
import ctypes
from json import loads as Jloads, dumps as Jdumps
from time import sleep
from datetime import datetime
from collections import defaultdict

import psutil   #v.7.2.2
from keyboard import is_pressed, wait as k_wait   #v.0.13.5

#--------------------------------------------------------------------------------------(DEFS)
def get_active_window_pid() -> int | None:
    """
    Возвращает PID процесса владельца активного окна в Windows.
    Возвращает None, если активного окна нет или получить PID не удалось.
    """
    user32 = ctypes.windll.user32
    GetForegroundWindow = user32.GetForegroundWindow
    GetWindowThreadProcessId = user32.GetWindowThreadProcessId

    hwnd = GetForegroundWindow()
    if not hwnd:
        return None

    pid = ctypes.c_ulong()
    GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
    return pid.value if pid.value != 0 else None

def get_process_subtree(pid: int):
    """Возврощает все PID вниз от заданого PID"""
    try:
        root = psutil.Process(pid)
        return [root.pid] + [p.pid for p in root.children(recursive=True)]
    except psutil.NoSuchProcess:
        return []

def dump_edit(massage: str, time: bool=True, new: bool=False):
    """Edit dump file."""
    if new:
        with open("dump", "r", encoding="utf-8") as Dfile:
            Dfile.write(f"[{datetime.now()}]|{massage}" if time else massage)
    
    else:
         with open("dump", "a", encoding="utf-8") as Dfile:
            Dfile.write(f"[{datetime.now()}]|{massage}" if time else massage)

#--------------------------------------------------------------------------------------(MAIN)

#--------------------------------------------------------------------------------------load_"keys_bind"_from_json_file
try:
    with open("keys_bind.json", "r", encoding="utf-8") as Jfile:
          Json = Jloads(Jfile.read())
          keys_bind, keys_exit = Json["keys_bind"], Json["keys_exit"]


except Exception as error:
    dump_edit(f'Unexpected error(load_"keys_bind"_from_json_file): \n\t{error}\n')

    with open("keys_bind.json", "w", encoding="utf-8") as Jfile:
        Jfile.write(Jdumps({"keys_bind": "alt + ctrl", "keys_exit": "ctrl + shift"}))

        dump_edit("\tNew Json file has created.\n", time=False)

    keys_bind = "alt + ctrl"
    keys_exit = "ctrl + shift"

#--------------------------------------------------------------------------------------main_loop
while True:
    if is_pressed(keys_bind) and (pid := get_active_window_pid()):
        try:
            proc = psutil.Process(pid)

            proc_list = list(map(psutil.Process, get_process_subtree(pid)))
            for proc in proc_list:
                proc.suspend()

            sleep(0.2)

            k_wait(keys_bind)
            for proc in proc_list:
                proc.resume()

            sleep(0.5)
        except Exception as error:
            dump_edit(f'Unexpected error(main_loop): \n\t{error}\n')

    elif is_pressed(keys_exit):
        break
