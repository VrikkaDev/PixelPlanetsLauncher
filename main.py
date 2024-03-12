import json
import os
import platform
import shutil
import threading
import time
import tkinter
import zipfile
from tkinter import ttk, CENTER
from dotenv import load_dotenv

import itchiodl
import sv_ttk
import requests
import subprocess

load_dotenv()
API_KEY = os.getenv("ITCH_IO_API_KEY") or ''
GAME_URL = f'https://itch.io/api/1/{API_KEY}/game/2573009'

DATA_FILE = 'launcher_data.json'

UPDATING = False


# ---------- VERSION ----------

def read_current_version() -> str:
    try:
        with open(DATA_FILE, 'rb') as json_file:
            json_data = json.load(json_file)
            return json_data['game_version']
    except:
        print(f'No {DATA_FILE} file found.')
    return ''


def check_for_update():
    response = requests.get(GAME_URL, stream=True)
    if response.status_code == 200:
        at = response.json()['game']['published_at']
        return at
    return None


# ---------- INSTALLATION ----------

def cleanup_installation():
    shutil.rmtree('studio-powerful')


def unzip_game():
    with zipfile.ZipFile('studio-powerful/pixel-planet-classic/PixelPlanetClassic.zip', 'r') as zip_ref:
        zip_ref.extractall('')


def download_latest(version):
    response = requests.get(GAME_URL, stream=True)
    g = itchiodl.Game(response.json())
    g.download(API_KEY, platform.system().lower())

    # Save the 'version' to the data file
    try:
        with open(DATA_FILE, 'w') as outfile:
            outfile.write(json.dumps({'game_version': version}, sort_keys=True, indent=4))
    except:
        print('Something went wrong trying to save the json file.')


def try_update():
    global UPDATING
    UPDATING = True
    current_version = read_current_version()
    new_version = check_for_update()

    if new_version and new_version != current_version:
        print('Downloading new version:', new_version)
        download_latest(new_version)
        unzip_game()
        cleanup_installation()
    else:
        print('You have the latest version.')
    UPDATING = False


# ---------- SOMETHING ----------

def launch_game():
    subprocess.Popen('PixelPlanetClassic')


# ---------- GUI ----------

def gui_check_updates_button():
    curr = read_current_version()
    new = check_for_update()

    # Set the update button state and info text
    btn: ttk.Button = root.nametowidget('u_button')
    tx: ttk.Label = root.nametowidget('info_text')
    if curr != new:
        btn['state'] = 'normal'
        tx['text'] = 'There is new version available'
    else:
        btn['state'] = 'disabled'
        tx['text'] = 'You have the latest version.'


def gui_updating():
    tx: ttk.Label = root.nametowidget('status_text')
    n = 0
    t = "..."
    while UPDATING:

        tx['text'] = f'Downloading PixelPlanet{t[:n]}'

        n += 1
        if n > 3:
            n = 0

        time.sleep(0.5)
    btn: ttk.Button = root.nametowidget('p_button')

    btn['state'] = 'normal'
    tx['text'] = ''
    gui_check_updates_button()


def gui_update_button():
    # Set the status text and play button state
    tx: ttk.Label = root.nametowidget('status_text')
    tx['text'] = 'Downloading PixelPlanet'
    btn: ttk.Button = root.nametowidget('p_button')

    btn['state'] = 'disabled'

    ut = threading.Thread(target=try_update)
    upt = threading.Thread(target=gui_updating)

    ut.start()
    upt.start()


def gui_play_button():
    launch_game()


def run_gui():
    root.wm_title('PixelPlanet launcher')
    root.geometry('400x300')

    lu_text = ttk.Label(root, text='You have the latest version.', name='info_text')
    lu_text.place(relx=0.5, rely=0.4, anchor=CENTER)

    cfu_button = ttk.Button(root, text='Check for updates!', name='cfu_button', command=gui_check_updates_button)
    cfu_button.place(relx=0.25, rely=0.5, anchor=CENTER)

    u_button = ttk.Button(root, text='Update', state='disabled', name='u_button', command=gui_update_button)
    u_button.place(relx=0.25, rely=0.61, anchor=CENTER)

    p_button = ttk.Button(root, text='Play', width=20, name='p_button', command=gui_play_button)
    p_button.place(relx=0.7, rely=0.5, anchor=CENTER)

    s_text = ttk.Label(root, text='', name='status_text', width=22)
    s_text.place(relx=0.5, rely=0.7, anchor=CENTER)

    # Set the update button state at start
    gui_check_updates_button()

    sv_ttk.set_theme('dark')

    root.mainloop()


# TODO make a thing that tells if there is new download available for this launcher

if __name__ == '__main__':
    root = tkinter.Tk()
    root.resizable(False, False)

    run_gui()
