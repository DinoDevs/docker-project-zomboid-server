#!/usr/bin/env python3
import requests
import json
import time
import datetime
import sys
import os
import subprocess
from zomboid_rcon import ZomboidRCON
from os import path

global run_count
global startup_update_times_dict
global compare_update_times_dict

global hasStarted


######## USER SUPPLIED VALUES ######## 

# File Locations
ini_file = sys.argv[1]
start_file = '/home/steam/pz-dedicated/start-server.sh'

# RCON details
server_address = sys.argv[2]
rcon_port = 27015
rcon_password = sys.argv[3]
server_args = sys.argv[4]
###################################### 

rcon_details = (server_address, int(rcon_port))
run_count = 0
startup_update_times_dict = {}
compare_update_times_dict = {}
ws_line = "WorkshopItems="
post_dict = {}
id_list = []
#startup_update_times_dict = []
#compare_update_times_dict = []

#Testing zone


def restart_server():
    hasStarted = False
    subprocess.Popen(f"sh {os.path.relpath(start_file)} {server_args}", shell=True, start_new_session=True)
    while hasStarted == False:
        try: 
            pz = ZomboidRCON(ip=server_address, port=rcon_port, password=rcon_password)
            pz.serverMsg("Server started")
            hasStarted = True
        except (ConnectionRefusedError, TimeoutError):
            print("Server is still starting")
            time.sleep(10)
            pass

    self_path = str(os.path.abspath(__file__))
    subprocess.run(f"python3 {self_path} {ini_file} {server_address} {rcon_password} '{server_args}'", shell=True, start_new_session=True)
    time.sleep(1)
    exit(0)

def close_server(server_address, rcon_port, rcon_password):
    pz = ZomboidRCON(ip=server_address, port=rcon_port, password=rcon_password)
    # Add timer and to immediately shut down if there are no players
    command = pz.serverMsg("Mod update found. Shutting down server in 5 minutes")
    print(command.response)

    pz.quit()
    time.sleep(15) # Change to checking if the server is running instead of a fixed time)
    restart_server()
    
    

def check_again(server_address, rcon_port, rcon_password):
    print("Rechecking mods for updates - "+str(datetime.datetime.now().replace(microsecond=0)))
    #For any additional executions of generate_batches() you need to ensure compare_update_times_dict is set back to {} first
    global compare_update_times_dict
    compare_update_times_dict = {}
    generate_batches()
    if startup_update_times_dict == compare_update_times_dict:
        print("No mod updates detected.")
        close_server(server_address, rcon_port, rcon_password)
    else:
        print("Mod update detected. Restarting server now.")
        close_server(server_address, rcon_port, rcon_password)
    print("Time until next check: ")
    # Rechecks every 5 minutes.
    t = 30
    while t:
        mins, secs = divmod(t, 60)
        timer = '{:02d}:{:02d}'.format(mins, secs)
        print(timer, end="\r")
        time.sleep(1)
        t -= 1
    
    print("00:00 - Rechecking now!")
        
def update_dict_maker(data):
    index = 0
    global run_count
    if run_count == 1:
        dict_name = "startup_update_times_dict"
    else:
        dict_name = "compare_update_times_dict"
    while index < len(data):
        try:
            mod_id = data[index]['publishedfileid']
            update_time = data[index]['time_updated']
            globals()[dict_name][mod_id] = update_time
            # Increasing index has to be at the bottom or it breaks
            index += 1
        except (KeyError):
            print("Unexpected workshop info returned for mod "+str(data[index]['publishedfileid'])+"! Unable to check last updated time.")
            #Increment even on failure or it will be stuck in a death loop
            index += 1

def post_request(post_dict):
    r = requests.post("https://api.steampowered.com/ISteamRemoteStorage/GetPublishedFileDetails/v1/", data=post_dict)
    pp = json.loads(r.text)
    #print(json.dumps(pp['response']['publishedfiledetails'], indent=2))
    data = pp['response']['publishedfiledetails']
    update_dict_maker(data)
    
#https://stackoverflow.com/questions/8290397/how-to-split-an-iterable-in-constant-size-chunks
def batch(iterable, n=1):
    l = len(iterable)
    for ndx in range(0, l, n):
        yield iterable[ndx:min(ndx + n, l)]

def generate_batches():
    global run_count
    run_count += 1
    for x in batch(id_list, 10):
        post_dict = {}
        id_index = 0
        post_dict["itemcount"] = len(x)
        for mod_id in x:
            post_dict["publishedfileids["+str(id_index)+"]"] = mod_id
            id_index += 1
        post_request(post_dict)


def main(ini_file,ws_line):
        file_path = path.relpath(ini_file)
        with open(file_path) as file_read:
            lines = file_read.readlines()
            new_list = []
            idx = 0
            for line in lines:
                if ws_line in line:
                    new_list.insert(idx, line)
                    idx += 1
            if len(new_list)==0:
                print("\n\"" +ws_line+ "\" is not found in \"" +file_path+ "\"!")
            else:
                # 2 lines contain "WorkshopItems=", we want the second one.
                id_string = end=new_list[1][14:].rstrip()
        #Made this global so there is no need to rerun this portion for subsequent tests.
        #Still rerunning batching because I don't want to bother making variable amounts of global vars and it really isn't a huge load to batch.
        #Subsequent runs will just recall generate_batches()
        global id_list
        id_list = id_string.split(";")
        generate_batches()



main(ini_file,ws_line)
time.sleep(30)
while True:
    check_again(server_address, rcon_port, rcon_password)