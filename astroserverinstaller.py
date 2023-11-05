import tkinter as tk
import subprocess
import configparser
import os
import requests
import zipfile
import psutil
import shutil
import ctypes
import sys
import webbrowser


def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def run_as_admin():
    if sys.platform != 'win32':
        return

    try:
        ASADMIN = 'asadmin'
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, ASADMIN, None, 1)
    except Exception as e:
        print("Failed to run as admin:", e)
        sys.exit(1)

if not is_admin():
    run_as_admin()
    sys.exit(0)





def download_steamcmd():
    url = 'https://nssm.cc/release/nssm-2.24.zip'
    r = requests.get(url)
    with open("nssm-2.24.zip", "wb") as code:
        code.write(r.content)

    fantasy_zip = zipfile.ZipFile('nssm-2.24.zip')
    fantasy_zip.extractall('')
    fantasy_zip.close()
    shutil.copy('nssm-2.24/win64/nssm.exe', '.')
    if os.path.exists('nssm-2.24.zip'):
        os.remove('nssm-2.24.zip')
    if os.path.exists('nssm-2.24'):
        shutil.rmtree('nssm-2.24')

        
    url = 'https://steamcdn-a.akamaihd.net/client/installer/steamcmd.zip'
    r = requests.get(url)
    with open("steamcmd.zip", "wb") as code:
        code.write(r.content)
    fantasy_zip = zipfile.ZipFile('steamcmd.zip')
    fantasy_zip.extractall('steamcmd')
    fantasy_zip.close()
    os.remove("steamcmd.zip")

    command = 'steamcmd/steamcmd.exe'
    args = [
        '+login', 'anonymous',
        '+force_install_dir', '..\\Astro_Colony',  
        '+app_update', '2662210', 'validate', '+quit'  
    ]
    subprocess.Popen([command] + args, cwd='steamcmd')

def download_astro_colony():
    command = 'steamcmd/steamcmd.exe'
    args = [
        '+login', 'anonymous',
        '+force_install_dir', '..\\Astro_Colony',  
        '+app_update', '2662210', 'validate', '+quit'  
    ]
    subprocess.Popen([command] + args, cwd='steamcmd')

def create_server():
    server_name = server_name_entry.get()  
    query_port = query_port_entry.get()  
    log_enabled = log_var.get()

    config = configparser.ConfigParser()
    config['Server'] = {
        'SteamServerName': server_name,
        'QueryPort': query_port,
        'LogEnabled': log_enabled
    }


    with open('conf.ini', 'w') as configfile:
        config.write(configfile)

    server_command = f'Astro_Colony\\AstroColonyServer.exe -SteamServerName={server_name} -QueryPort={query_port}'
    if log_enabled:
        server_command += ' -log'
    subprocess.Popen(server_command, shell=True, close_fds=True)


def open_server_config():
    subprocess.Popen('notepad.exe Astro_Colony/AstroColony/Saved/Config/WindowsServer/ServerSettings.ini', shell=True)

def kill_server_process():
    for process in psutil.process_iter(attrs=['pid', 'name']):
        if 'AstroColonyServer.exe' in process.info['name']:
            try:
                psutil.Process(process.info['pid']).terminate()
            except psutil.NoSuchProcess:
                pass

def open_ports(query_port):
    cmd_command = f'powershell.exe New-NetFirewallRule -DisplayName "Allow-AstroColony-UDP-Port" -Direction Inbound -Action Allow -EdgeTraversalPolicy Allow -Protocol UDP -LocalPort {query_port},7777'
    os.system(f'cmd /C "{cmd_command} & timeout 5 & exit"')




def on_install_service(server_name, query_port):
    cmd_command = f'nssm.exe install AstroColonyServerService %CD%\\Astro_Colony\\AstroColonyServer.exe -SteamServerName={server_name} -QueryPort={query_port}'
    os.system(f'cmd /C "{cmd_command} & timeout 3"')





def on_start_service():
    cmd_command = 'nssm.exe start AstroColonyServerService'
    os.system(f'cmd /C "{cmd_command} & timeout 3"')


def on_stop_service():
    cmd_command = 'nssm.exe stop AstroColonyServerService'
    os.system(f'cmd /C "{cmd_command} & timeout 3"')

def on_delete_service():
    cmd_command = 'nssm.exe remove AstroColonyServerService'
    os.system(f'cmd /C "{cmd_command} & timeout 3"')

def on_open_guide():
    url = "https://bit.ly/AstroColonyDedicatedDoc"
    webbrowser.open(url)


root = tk.Tk()
root.title("Astro Colony Server Manager")
root.geometry("300x400")


server_name_label = tk.Label(root, text="Server Name:")
server_name_label.pack()
server_name_entry = tk.Entry(root)
server_name_entry.pack()



query_port_label = tk.Label(root, text="Query Port:")
query_port_label.pack()
config = configparser.ConfigParser()
if config.read('conf.ini'):
    query_port = ()
else:
    query_port = 27015 

query_port_entry = tk.Entry(root)
query_port_entry.insert(0, query_port)
query_port_entry.pack()




log_var = tk.BooleanVar()
log_checkbutton = tk.Checkbutton(root, text="Enable Logging and Console", variable=log_var)
log_checkbutton.pack()


log_checkbutton.config(variable=log_var)

download_steamcmd_button = tk.Button(root, text="Download SteamCMD & Install", command=download_steamcmd)
download_steamcmd_button.pack()

download_astro_colony_button = tk.Button(root, text="Download Astro Colony and Update", command=download_astro_colony)
download_astro_colony_button.pack()

create_server_button = tk.Button(root, text="Start Server", command=create_server)
create_server_button.pack()

kill_server_button = tk.Button(root, text="Close process AstroColonyServer", command=kill_server_process)
kill_server_button.pack()

Install_service_button = tk.Button(root, text="Install Service", command=lambda: on_install_service(server_name_entry.get(), query_port_entry.get()))
Install_service_button.pack()
start_service_button = tk.Button(root, text="Start Service", command=on_start_service)
start_service_button.pack()
stop_server_button = tk.Button(root, text="Stop Service", command=on_stop_service)
stop_server_button.pack()
delete_server_button = tk.Button(root, text="Delete Service", command=on_delete_service)
delete_server_button.pack()


open_config_button = tk.Button(root, text="Open Server Config", command=open_server_config)
open_config_button.pack()


open_ports_button = tk.Button(root, text="Open UDP Ports", command=lambda: open_ports(int(query_port_entry.get())))
open_ports_button.pack()


on_open_guide = tk.Button(root, text="Open Guide page", command=on_open_guide)
on_open_guide.pack()




config = configparser.ConfigParser()
if config.read('conf.ini'):
    server_name_entry.insert(0, config['Server']['SteamServerName'])
    query_port_entry.insert(0, config['Server']['QueryPort'])
    log_var.set(config.getboolean('Server', 'LogEnabled'))
    

root.mainloop()