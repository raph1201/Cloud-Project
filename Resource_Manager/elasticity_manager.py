from flask import Flask, jsonify, request
import pycurl
import json
from io import BytesIO
from threading import Thread
import time
import random
import string

#Create instance of Flask
app = Flask(__name__)

cURL = pycurl.Curl()

rm_url = '10.140.17.105:3000'
light_proxy_ip = 'http://10.140.17.106:5000'
medium_proxy_ip = 'http://10.140.17.106:5001'
heavy_proxy_ip = 'http://10.140.17.106:5002'


#Pod elasticity Status Identifiers
PodElasticityIdentifierDict = {'L': False,
                               'M': False, 
                               'H': False}

#Where threads are stored
elasticResouceManagementThreads = {'L': None,
                                   'M': None,
                                   'H': None}


#Thread that will continuously run for each pod.
#Will get : util, lower_thr, upper_thr and send commands accordingly
def runERMThreads(pod_ID, pod_url):
    while(1):
        global PodElasticityIdentifierDict
        
        #If Elasticity mode off, skip
        if PodElasticityIdentifierDict[pod_ID] == False:
            continue
        
        else:
            #Else connect to pod and fetch important stats
            t_cURL = pycurl.Curl()
            t_cURL.setopt(cURL.URL, pod_url + '/elastic/resource/management')
            buffer = bytearray()
            t_cURL.setopt(cURL.WRITEFUNCTION, buffer.extend)
            t_cURL.perform()
            
            #If connection successful
            if t_cURL.getinfo(cURL.RESPONSE_CODE) == 200:
                
                #Load dictionary
                result_dict = json.loads(buffer.decode())
                paused = result_dict['paused']
                if paused == True:
                    print(f'POD {pod_ID} CURRENTLY PAUSED')

                else:
                    lower_thr = result_dict['lower_thr']
                    upper_thr = result_dict['upper_thr']
                    util = result_dict['utilization']
                    lower_limit = result_dict['lower_node_limit']
                    upper_limit = result_dict['upper_node_limit']
                    onlineNodes = result_dict['online_nodes']
                    print(f"POD {pod_ID} – {onlineNodes} nodes ONLINE")
                    print(f"Upper Thr {upper_thr} – CPU Usage {util:.2f}% – Lower Thr {lower_thr}")
                    
                    #If Utilization too high, need to add nodes according to limit
                    if (float(util)/100.0 > float(upper_thr)):
                        if (onlineNodes < upper_limit):
                            print("Util above threshold --> Need to add nodes")
                            #Generate a random name
                            name = getRandomName()

                            #Register a new node with random name
                            registerNode(name, pod_ID)

                            #Launch said node
                            launchNode(pod_ID)

                        else:
                            print('Utilization too high but limit prevents addition of more nodes.\nPlease raise the threshold.')
                    
                    #If Utilization too low, need to remove nodes according to limit
                    elif (float(util)/100.0 < float(lower_thr)):
                        if (onlineNodes > lower_limit):
                            print("Util below threshold --> Need to remove nodes")
                            #Remove excess node
                            removeNode(pod_ID)
                    
                        else:
                            print('Utilization too low but limit prevents addition of more nodes.\nPlease lower the threshold.')

                    #Else, utilization is satisfactory
                    else:
                        print("Util within threshold")
            
            print()
            time.sleep(2)


#Enable elasticity mode
#Cloud user must specify POD_ID MIN_NODES MAX_NODES
@app.route('/enable/<pod_ID>/<lower_size>/<upper_size>')
def enableElasticityPod(pod_ID, lower_size, upper_size):
    print(f"\nElasticity Enable command on {pod_ID} executing. Lower_size: {lower_size} - Upper_size: {upper_size}.")
    ip = ''
    if pod_ID == 'L':
        ip = light_proxy_ip

    elif pod_ID == 'M':
        ip = medium_proxy_ip
        
    elif pod_ID == 'H':
        ip = heavy_proxy_ip

    data = BytesIO()
    cURL.setopt(cURL.URL, ip + '/enable/elasticity/' + lower_size + '/' + upper_size)
    cURL.setopt(cURL.WRITEFUNCTION, data.write)
    cURL.perform()
    print(f"Sending request to setup elasticity parameters (lower size: {lower_size} & upper size: {upper_size}) to backend: {pod_ID}.")
    print(cURL.getinfo(cURL.RESPONSE_CODE))

    #If connection successful
    if cURL.getinfo(cURL.RESPONSE_CODE) == 200:
        dct = json.loads(data.getvalue())
        result = dct['result']

        if result == 'Success':
            global PodElasticityIdentifierDict
            PodElasticityIdentifierDict[pod_ID] = True
            print(f"POD: {pod_ID} Elastic mode on --> {PodElasticityIdentifierDict[pod_ID]}")
            return jsonify({'result': 'Success',
                            'pod_id': pod_ID,
                            'elasticity': 'enabled'})
        
        else:
            reason = dct['reason']
            return jsonify({'result': result,
                            'reason': reason})
    
    return jsonify({'response' : 'failure',
                    'reason' : 'Unknown'})


#Disable elasticity mode
@app.route('/disable/<pod_ID>')
def disableElasticityPod(pod_ID):
    print(f"\nElasticity Disable command on {pod_ID} executing.")
    ip = ''
    if pod_ID == 'L':
        ip = light_proxy_ip

    elif pod_ID == 'M':
        ip = medium_proxy_ip
        
    elif pod_ID == 'H':
        ip = heavy_proxy_ip

    data = BytesIO()
    cURL.setopt(cURL.URL, ip + '/disable/elasticity')
    cURL.setopt(cURL.WRITEFUNCTION, data.write)
    cURL.perform()
    print(cURL.getinfo(cURL.RESPONSE_CODE))

    #If connection successful
    if cURL.getinfo(cURL.RESPONSE_CODE) == 200:
        dct = json.loads(data.getvalue())
        result = dct['result']

        if result == 'Success':
            global PodElasticityIdentifierDict
            PodElasticityIdentifierDict[pod_ID] = False
            print(f"POD: {pod_ID} Elastic mode on --> {PodElasticityIdentifierDict[pod_ID]}")
            return jsonify({'result': 'Success',
                            'pod_id': pod_ID,
                            'elasticity': 'disabled'})
        
        else:
            reason = dct['reason']
            return jsonify({'result': result,
                            'reason': reason})
    
    return jsonify({'response' : 'failure',
                    'reason' : 'Unknown'})


#Set Lower Threshold for utilization
@app.route('/lowerthreshold/<pod_ID>/<value>')
def elasticityLowerThreshold(pod_ID, value):
    print(f"\nSetting Elasticity Lower Threshold ({value}) for backend: {pod_ID}.")
    ip = ''
    if pod_ID == 'L':
        ip = light_proxy_ip

    elif pod_ID == 'M':
        ip = medium_proxy_ip
        
    elif pod_ID == 'H':
        ip = heavy_proxy_ip
    
    #Check for input correctness
    if value.startswith('-') or (not is_float_between_0_and_1(value)):
        return jsonify({'result' : 'Failure',
                        'reason' : 'Wrong value - Please enter a positive float between [0,1] for lower threshold value'})

    data = BytesIO()
    cURL.setopt(cURL.URL, ip + '/elastic/resource/management')
    cURL.setopt(cURL.WRITEFUNCTION, data.write)
    cURL.perform()
    if cURL.getinfo(cURL.RESPONSE_CODE) == 200:
        dct = json.loads(data.getvalue())
        upper_thr = dct['upper_thr']

        if float(value) >= float(upper_thr):
            return jsonify({'result' : 'Failure',   
                            'reason' : 'Wrong value - Please enter a threshold lower than the upper threshold'})

        elif (float(upper_thr) - float(value)) < 0.1:
            return jsonify({'result' : 'Failure',
                            'reason' : 'Wrong value - Please leave a 10% margin between upper and lower threshold'})


    #If input is correct, send curl request to modify it
    data = BytesIO()
    cURL.setopt(cURL.URL, ip + '/lowerthreshold/' + value)
    cURL.setopt(cURL.WRITEFUNCTION, data.write)
    cURL.perform()
    print(cURL.getinfo(cURL.RESPONSE_CODE))

    #If connection successful
    if cURL.getinfo(cURL.RESPONSE_CODE) == 200:
        dct = json.loads(data.getvalue())
        result = dct['result']

        if result == 'Success':
            return jsonify({'result': 'Success',
                            'pod_id': pod_ID,
                            'elasticity LT': value})
    
    return jsonify({'response' : 'failure',
                    'reason' : 'Unknown'})


#Set Upper Threshold for utilization
@app.route('/upperthreshold/<pod_ID>/<value>')
def elasticityUpperThreshold(pod_ID, value):
    print(f"\nSetting Elasticity Upper Threshold ({value}) for backend: {pod_ID}.")
    ip = ''
    if pod_ID == 'L':
        ip = light_proxy_ip

    elif pod_ID == 'M':
        ip = medium_proxy_ip
        
    elif pod_ID == 'H':
        ip = heavy_proxy_ip
    
    #Check for input correctness
    if value.startswith('-') or (not is_float_between_0_and_1(value)):
        return jsonify({'result' : 'Failure',
                        'reason' : 'Wrong value - Please enter a positive float between [0,1] for lower threshold value'})

    data = BytesIO()
    cURL.setopt(cURL.URL, ip + '/elastic/resource/management')
    cURL.setopt(cURL.WRITEFUNCTION, data.write)
    cURL.perform()
    if cURL.getinfo(cURL.RESPONSE_CODE) == 200:
        dct = json.loads(data.getvalue())
        lower_thr = dct['lower_thr']

        if float(value) <= float(lower_thr):
            return jsonify({'result' : 'Failure',
                            'reason' : 'Wrong value - Please enter a threshold higher than the lower threshold'})

        elif (float(value) - float(lower_thr)) < 0.1:
            return jsonify({'result' : 'Failure',
                            'reason' : 'Wrong value - Please leave a 10% margin between upper and lower threshold'})
    

    #If input correct, send curl request to modify it
    data = BytesIO()
    cURL.setopt(cURL.URL, ip + '/upperthreshold/' + value)
    cURL.setopt(cURL.WRITEFUNCTION, data.write)
    cURL.perform()
    print(cURL.getinfo(cURL.RESPONSE_CODE))

    #If connection successful
    if cURL.getinfo(cURL.RESPONSE_CODE) == 200:
        dct = json.loads(data.getvalue())
        result = dct['result']

        if result == 'Success':
            return jsonify({'result': 'Success',
                            'pod_id': pod_ID,
                            'elasticity UT': value})
    
    return jsonify({'response' : 'failure',
                    'reason' : 'Unknown'})


#-------------------------- HELPER METHODS ----------------------------#
#Random name generator for adding nodes
def getRandomName():
    letters = string.ascii_lowercase
    name = ''
    for i in range(10):
        name = name + random.choice(letters)
    return name


#Register node by sending curl request to RM
def registerNode(name, pod_ID):
    cURL = pycurl.Curl()
    data = BytesIO()
    cURL.setopt(cURL.URL, rm_url + '/cloud/nodes/' + name + '/' + pod_ID)
    cURL.setopt(cURL.WRITEFUNCTION, data.write)
    cURL.perform()
    dct = json.loads(data.getvalue())
    result= dct['result']

    if result == 'Failure':
        reason = dct['reason']
        print(f"result: {result} - reason: {reason}\n")

    else:
        port, name, status = dct['port'], dct['name'], dct['status']
        print(f"result: {result} - port: {port} - name: {name} - status: {status}\n")


#Launch node by sending curl request to RM
def launchNode(pod_ID):
    data = BytesIO()
    cURL.setopt(cURL.URL, rm_url + '/cloud/launch/' + pod_ID)
    cURL.setopt(cURL.WRITEFUNCTION, data.write)
    cURL.perform()
    dct = json.loads(data.getvalue())
    result= dct['result']

    if result == 'Failure':
        reason = dct['reason']
        print(f"result: {result} - reason: {reason}")

    #Result == 'Success'
    else:
        #If node ONLINE and if Pod not paused
        if len(dct) == 4:
            port, name, status = dct['port'], dct['name'], dct['status']
            print(f"result: {result} - port: {port} - name: {name} - status: {status}\n")

        #If Pod paused
        else:
            print(f"result: {result} - pod: paused\n")


#Remove node by getting list of online nodes and removing one of them
def removeNode(pod_ID):
    #Set IP according to pod_ID 
    ip = ''
    if pod_ID == 'L':
        ip = light_proxy_ip

    elif pod_ID == 'M':
        ip = medium_proxy_ip

    elif pod_ID == 'H':
        ip = heavy_proxy_ip
        
    #Get last node in node_list
    data = BytesIO()
    cURL.setopt(cURL.URL,ip  + '/get/node/name')
    cURL.setopt(cURL.WRITEFUNCTION, data.write)
    cURL.perform()
    dct = json.loads(data.getvalue())
    name = dct['name']
    print(name)

    #Remove it from POD thru curl request
    data = BytesIO()
    cURL.setopt(cURL.URL, rm_url + '/cloud/nodes/remove/' + name + '/' + pod_ID)
    cURL.setopt(cURL.WRITEFUNCTION, data.write)
    cURL.perform()
    dct = json.loads(data.getvalue())
    result = dct['result']

    if result == 'Failure':
        reason = dct['reason']
        print(f"result: {result} - reason: {reason}\n")

    else:
        port, name, status = dct['port'], dct['name'], dct['status']
        print(f"result: {result} - port: {port} - name: {name} - status: {status}\n")


def is_float_between_0_and_1(string):
    try:
        value = float(string)
        if 0.0 <= value <= 1.0:
            return True
        else:
            return False
    except ValueError:
        return False


#-------------------------------MAIN-------------------------------#

if __name__ == '__main__':
    #Setup threads responsible for elastic management of backend resources (1 for each backend
    elasticResouceManagementThreads['L'] = Thread(target=runERMThreads, args=('L', light_proxy_ip,))
    elasticResouceManagementThreads['M'] = Thread(target=runERMThreads, args=('M', medium_proxy_ip,))
    elasticResouceManagementThreads['H'] = Thread(target=runERMThreads, args=('H', heavy_proxy_ip,))

    for key in elasticResouceManagementThreads:
        elasticResouceManagementThreads[key].start()

    app.run(debug=True, host='0.0.0.0', port=4000)