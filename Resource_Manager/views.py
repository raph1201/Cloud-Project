from flask import render_template, request, jsonify
import requests
import pycurl
from io import BytesIO
import json
from __main__ import *
import time
import pandas as pd

#Get the URL of the Proxy
cURL = pycurl.Curl()
rm_url = 'http://10.140.17.105:3000'

def index():
    # Making sure the cloud is online
    try:
        stat = get_cloud_status()
        init = "Connected"
        
    except Exception as e:
        print(e)
        stat = []
        init = "Error Clound not Launched"
        
    lt_avail = "0"
    md_avail = "0"
    hv_avail = "0"
    if len(stat) > 0:
        nd_ls = get_cloud_nodes(stat)
        for nodes in nd_ls:
            if 'LIGHT' == nodes['Pod']:
                lt_avail = str(len(nodes) - 1)
            if 'MEDIUM' == nodes['Pod']:
                md_avail = str(len(nodes) - 1)
            else:
                hv_avail = str(len(nodes) - 1)
    
    #get HAProxy stats
    lt_stats, md_stats, hv_stats = get_proxy_stats()
    total_req = int(lt_stats["requests"]) + int(md_stats["requests"]) + int(hv_stats["requests"])
        

    return render_template("index.html", cloud_status=init, total_requests=total_req,
                           light_avail=lt_avail, med_avail=md_avail, heavy_avail=hv_avail,
                           lt_resumed=lt_stats["resumed"], lt_process=lt_stats["processing"], lt_request=lt_stats["requests"],
                           med_resumed=md_stats["resumed"], med_process=md_stats["processing"], med_request=md_stats["requests"],
                           hv_resumed=hv_stats["resumed"], hv_process=hv_stats["processing"], hv_request=hv_stats["requests"])

def stats():
    data = BytesIO()
    cURL.setopt(cURL.URL, rm_url + f'/cloud/haproxy/stats')
    cURL.setopt(cURL.WRITEFUNCTION, data.write)
    cURL.perform()
    dct = json.loads(data.getvalue())
    
    
    return render_template("stats.html", info_dct=dct, len=len(dct["pxname"]))

def clusters():
    dct = get_cloud_nodes()
    val = []
    for k in dct:
        l = dct[k].split(",")
        name = l[0].split()[1]
        id_num = l[1].split()[1]
        num_nodes = l[2].split()[1]
        val.append([name + id_num, id_num, num_nodes])
    
    return render_template("clusters.html", lst=val)

def pods(pod_id):
    dct = get_cloud_nodes([pod_id])
    if len(dct) > 0:
        dct = dct[0]
        dct.pop('Pod')
    val = []
    
    data = BytesIO()
    cURL.setopt(cURL.URL, rm_url + f'/dashboard/status/{pod_id}')
    cURL.setopt(cURL.WRITEFUNCTION, data.write)
    cURL.perform()
    dct_2 = json.loads(data.getvalue())
    paused = dct_2['result']
    
    if pod_id == 'L':
        pod_id = 'Light Pod'
    elif pod_id == 'M':
        pod_id = 'Medium Pod'
    else:
        pod_id = 'Heavy Pod'
    
    if paused:
        paused = "Paused"
    else:
        paused = "Resumed"
      
    for k in dct:
        l = dct[k].split(" - ")
        print(l)
        id_num = k
        nd_name = l[0].split()[1]
        num_port = l[1].split()[1]
        nd_status = l[2].split()[1]
        val.append([nd_name, id_num, num_port, nd_status])
    
    val.sort(key=lambda v : int(v[1])) 
    
    
    proxy_dct = get_running_jobs()
    
    for ls in val:
        if ls[0] in proxy_dct["svname"]:
            for i in range(len(proxy_dct["svname"])):
                if proxy_dct["svname"][i] == ls[0]:
                    if proxy_dct["scur"][i] == "0":
                        ls.append(False)
                    else:
                        ls.append(True)
                    ls.append(proxy_dct["stot"][i])
        
    
    return render_template("cluster_overview.html", pod_id=pod_id, lst=val, running=paused, unique_id=pod_id[0])

#--------------------------HELPER FUNCTIONS-------------------------
def get_nodes_info(node_ls):
    pass

def get_cloud_status(): 
    pod_ls = ("L", "M", "H")
    
    result = []

    for id in pod_ls:
        #Logic to invoke RM-Proxy
        data = BytesIO()
        cURL.setopt(cURL.URL, rm_url + f'/cloud/node/ls/{id}')
        cURL.setopt(cURL.WRITEFUNCTION, data.write)
        cURL.perform()
        dct = json.loads(data.getvalue())
        print(dct)
        
        if (dct['result'] == 'Success'):
            result.append(id)
        
    return result


def get_cloud_nodes(pod_ls):
    result = []
    
    for id in pod_ls: 
        #Logic to invoke RM-Proxy
        data = BytesIO()
        
        cURL.setopt(cURL.URL, rm_url + f'/cloud/node/ls/{id}')
        cURL.setopt(cURL.WRITEFUNCTION, data.write)
        cURL.perform()      
        dct = json.loads(data.getvalue())
        
        if (dct['result'] == 'Success'):
            dct.pop('result')
            result.append(dct)
    
    return result


def get_running_jobs():
    #request HAProxy stats from Resource Manager
    data = BytesIO()
    cURL.setopt(cURL.URL, rm_url + '/cloud/haproxy/stats')
    cURL.setopt(cURL.WRITEFUNCTION, data.write)
    cURL.perform()
    #converts into a dictionary 
    data_dct = json.loads(data.getvalue())
    
    print(data_dct)

    return data_dct

#Process HAProxy stats for the different pods
def get_proxy_stats():
    dct = get_running_jobs()
    
    lt_stats = {"resumed": -1, "processing": 0, "requests": 0}
    md_stats = {"resumed": -1, "processing": 0, "requests": 0}
    hv_stats = {"resumed": -1, "processing": 0, "requests": 0}
    
    i = -1
    # getting current number of requests for heavy
    for v in dct["pxname"]:
        i += 1
        if v == "heavy-servers" and dct["svname"][i] == "BACKEND":
            hv_stats["processing"] = dct["scur"][i]
            hv_stats["resumed"] += 1
            hv_stats["requests"] = dct["stot"][i]
            
        elif v == "heavy-servers":
            hv_stats["resumed"] += 1
            
        if v == "light-servers" and dct["svname"][i] == "BACKEND":
            lt_stats["processing"] = dct["scur"][i]
            lt_stats["resumed"] += 1
            lt_stats["requests"] = dct["stot"][i]
            
        elif v == "light-servers":
            lt_stats["resumed"] += 1
            
        if v == "medium-servers" and dct["svname"][i] == "BACKEND":
            md_stats["processing"] = dct["scur"][i]
            md_stats["resumed"] += 1
            md_stats["requests"] = dct["stot"][i]
            
        elif v == "medium-servers":
            md_stats["resumed"] += 1
    
    return lt_stats, md_stats, hv_stats