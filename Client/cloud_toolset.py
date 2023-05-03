import pycurl
import json
from io import BytesIO

#Get the URL of the Ressource Manager
cURL = pycurl.Curl()

rm_url = '10.140.17.105:3000'
lb_url_light = '10.140.17.105:5000'
lb_url_medium = '10.140.17.105:5001'
lb_url_heavy = '10.140.17.105:5002'

#Pod elasticity Identifiers
PodElasticityIdentifierDict = {'L': False,
                               'M': False, 
                               'H': False}

def error_msg(msg):
    print(msg)
    print("Please check out 'cloud help' for our list of available commands")
    
#Prints all commands to the console
def cloud_help():
    cmd_lst = {"cloud init" : "Initializes main resource cluster", 
               "cloud pod register POD_NAME" : "Not Implemented", 
               "cloud pod rm POD_NAME" : "Not Implemented", 
               "cloud register NODE_NAME POD_ID" : "Register node with specified name, port in specified pod", 
               "cloud rm NODE_NAME POD_ID" : "Remove node with specified name from pod", 
               "cloud launch POD_ID" : "Launches a job from specified Job", 
               "cloud resume POD_ID" : "Resume specified pod activity",
               "cloud pause POD_ID" : "Pause specified pod activity",
               "cloud node ls POD_ID" : "Lists all nodes & their infos",
               "cloud elasticity enable POD_NAME lower_size upper_size": "Enables elasticity for given pod. Specifies pod size in terms of node size range.",
               "cloud elasticity disable POD_NAME": "Disables elasticity manager for given pod",
               "cloud elasticity lower_threshold POD_NAME VALUE": "Defines lower_threshold for given pod",
               "cloud elasticity upper_threshold POD_NAME VALUE": "Defines upper_threshold for given pod"}
    print("---------------------------------------- HELP ----------------------------------------")
    print("Welcome to Help, here you will find a list of useful commands")
    
    for cmd in cmd_lst:
        print(cmd, "\n\t", cmd_lst[cmd])


#1. Initialize cloud : default pod & 50 default nodes
def cloud_init(url):
    data = BytesIO()
    cURL.setopt(cURL.URL, url + '/cloud/init')
    cURL.setopt(cURL.WRITEFUNCTION, data.write)
    cURL.perform()
    dct = json.loads(data.getvalue())
    print(dct['result'])

#2. Register new pod, must give pod name
#Syntax : $ cloud pod register <pod name>
def cloud_pod_register(url, command):
    error_msg(f"The current cloud system cannot register new pods.")
        

#3. Remove pod, must five pod name
#Syntax : $ cloud pod rm <pod name>
def cloud_pod_rm(url, command):
    error_msg(f"The current cloud system does not allow users to remove pods.")


#4. Register new node. Must specify name, port and pod
#Syntax : $ cloud register <node_name> <pod_ID>
def cloud_register(url, command):
    command_list = command.split()

    #Check if Elastic Manager is enabled for this pod, if so, this function is hidden from the cloud user and therefore not available
    if((command_list[3] in 'LMH') and PodElasticityIdentifierDict[command_list[3]] == True):
        print(f"This command: '{command}' is currently unavailable, as the Elastic Manager has been enabled for this specific pod: ({command_list[3]})\n")
        return

    #If pod name given
    if len(command_list) == 4:
        data = BytesIO()
        cURL.setopt(cURL.URL, url + '/cloud/nodes/' + command_list[2] + '/' + command_list[3])
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

    else:
        error_msg(f"Command:'{command}' Missing Argument <pod_name>")


#5. Remove existing node. Must specify name and pod
#Syntax : $ cloud rm <node_name> <pod_ID>
def cloud_rm(url, command):
    command_list = command.split()

    #Check if Elastic Manager is enabled for this pod, if so, this function is hidden to the cloud user and therefore not available
    if((command_list[3] in 'LMH') and PodElasticityIdentifierDict[command_list[3]] == True):
        print(f"This command: '{command}' is currently unavailable, as the Elastic Manager has been enabled for this specific pod: ({command_list[3]})\n")
        return

    if len(command_list) == 4:
        data = BytesIO()
        cURL.setopt(cURL.URL, url + '/cloud/nodes/remove/' + command_list[2] + '/' + command_list[3])
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


    else:
        error_msg(f"Command:'{command}' Missing Argument <pod_name>")


#6. Launch job on specified pod
#Syntax : $ cloud launch <pod_ID>
def cloud_launch(url, command):
    command_list = command.split()

    #Check if Elastic Manager is enabled for this pod, if so, this function is hidden from the cloud user and therefore not available
    if((command_list[2] in 'LMH') and PodElasticityIdentifierDict[command_list[2]] == True):
        print(f"This command: '{command}' is currently unavailable, as the Elastic Manager has been enabled for this specific pod: ({command_list[2]})\n")
        return

    if len(command_list) == 3:
        data = BytesIO()
        cURL.setopt(cURL.URL, url + '/cloud/launch/' + command_list[2])
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
                
    else:
        error_msg(f"Command:'{command}' Missing Argument <pod_name>")


#7. Resume specified pod activity
#Syntax : $ cloud resume <pod_ID>
def cloud_resume(url, command):
    command_list = command.split()

    if len(command_list) == 3:
        data = BytesIO()
        cURL.setopt(cURL.URL, url + '/cloud/resume/' + command_list[2])
        cURL.setopt(cURL.WRITEFUNCTION, data.write)
        cURL.perform()
        dct = json.loads(data.getvalue())
        result= dct['result']


        if result == 'Failure':
            reason = dct['reason']
            print(f"result: {result} - reason: {reason}\n")

        else: 
            nodes_launched = dct['nodes_launched']
            print(f"result: {result} - nodes launched: {nodes_launched}\n")

    else:
        error_msg(f"Command:'{command}' Missing Argument <pod_name>")


#8. Pause specified pod activity
#Syntax : $ cloud pause <pod_ID>
def cloud_pause(url, command):
    command_list = command.split()

    if len(command_list) == 3:
        data = BytesIO()
        cURL.setopt(cURL.URL, url + '/cloud/pause/' + command_list[2])
        cURL.setopt(cURL.WRITEFUNCTION, data.write)
        cURL.perform()
        dct = json.loads(data.getvalue())
        result= dct['result']

        if result == 'Failure':
            reason = dct['reason']
            print(f"result: {result} - reason: {reason}\n")

        else: 
            #------------ Pods or nodes double check
            nodes_removed_from_Load_Balancer = dct['nodes_removed_from_Load_Balancer']
            print(f"result: {result} - nodes removed: {nodes_removed_from_Load_Balancer}\n")



    else:
        error_msg(f"Command:'{command}' Missing Argument <pod_name>")


#--------------------- Monitoring -----------------------
#9. List all resource node in specified pod, or in main cluster
# Syntax: cloud node ls <pod_ID>
def cloud_node_ls(url, command):
    command_ls = command.split()
    
    if len(command_ls) == 4: 
        data = BytesIO()
        cURL.setopt(cURL.URL, url + '/cloud/node/ls/' + command_ls[3])
        cURL.setopt(cURL.WRITEFUNCTION, data.write)
        cURL.perform()
        dct = json.loads(data.getvalue())
        result= dct['result']

        if result == 'Failure':
            reason = dct['reason']
            print(f"result: {result} - reason: {reason}\n")

        else: 
            for key, value in dct.items():
                print(f"{key} {value}")
            print()

    else:
        error_msg(f"Command:'{command}' Not Correct")



#---------- Elasticity ----------#
# Syntax: cloud elasticity enable <pod_ID> <lower node limit> <upper node limit>
def cloud_elasticity_enable(url, command):
    command_ls = command.split()

    if len(command_ls) == 6:
        global PodElasticityIdentifierDict
        data = BytesIO()
        cURL.setopt(cURL.URL, url + '/cloud/elasticity/enable/' + command_ls[3] + '/' + command_ls[4] + '/' + command_ls[5])
        cURL.setopt(cURL.WRITEFUNCTION, data.write)
        cURL.perform()
        dct = json.loads(data.getvalue())
        result= dct['result']

        if result == 'Failure':
            reason = dct['reason']
            print(f"result: {result} - reason: {reason}\n")

        #result == 'Success'
        else:
            podID, elasticity = dct['pod_id'], dct['elasticity']
            print(f'result: {result} - pod: {podID} - elasticity: {elasticity}\n')
            PodElasticityIdentifierDict[command_ls[3]] = True

    else:
        error_msg(f"Command:'{command}' Not Correct")


# Syntax: cloud elasticiry disable <pod_ID>
def cloud_elasticity_disable(url, command):
    command_ls = command.split()

    if len(command_ls) == 4:
        global PodElasticityIdentifierDict
        data = BytesIO()
        cURL.setopt(cURL.URL, url + '/cloud/elasticity/disable/' + command_ls[3])
        cURL.setopt(cURL.WRITEFUNCTION, data.write)
        cURL.perform()
        dct = json.loads(data.getvalue())
        result= dct['result']

        if result == 'Failure':
            reason = dct['reason']
            print(f"result: {result} - reason: {reason}\n")

        #result == 'Success'
        else:
            podID, elasticity = dct['pod_id'], dct['elasticity']
            print(f'result: {result} - pod: {podID} - elasticity: {elasticity}\n')
            PodElasticityIdentifierDict[command_ls[3]] = False

    else:
        error_msg(f"Command:'{command}' Not Correct")


#Syntax: cloud elasticiry lower_threshold <pod_ID> <lower thr>
def cloud_elasticity_lower_threshold(url, command):
    command_ls = command.split()

    if len(command_ls) == 5:
        data = BytesIO()
        cURL.setopt(cURL.URL, url + '/cloud/elasticity/lowerthreshold/' + command_ls[3] + '/' + command_ls[4])
        cURL.setopt(cURL.WRITEFUNCTION, data.write)
        cURL.perform()
        dct = json.loads(data.getvalue())
        result= dct['result']

        if result == 'Failure':
            reason = dct['reason']
            print(f"result: {result} - reason: {reason}\n")

        #result == 'Success'
        else:
            podID, elasticity_LT = dct['pod_id'], dct['elasticity LT']
            print(f'result: {result} - pod: {podID} - elasticity Lower Threshold: {elasticity_LT}\n')

    else:
        error_msg(f"Command:'{command}' Not Correct")


# Syntax: cloud elasticiry upper_threshold <pod_ID> <upper_thr>
def cloud_elasticity_upper_threshold(url, command):
    command_ls = command.split()

    if len(command_ls) == 5:
        data = BytesIO()
        cURL.setopt(cURL.URL, url + '/cloud/elasticity/upperthreshold/' + command_ls[3] + '/' + command_ls[4])
        cURL.setopt(cURL.WRITEFUNCTION, data.write)
        cURL.perform()
        dct = json.loads(data.getvalue())
        result= dct['result']

        if result == 'Failure':
            reason = dct['reason']
            print(f"result: {result} - reason: {reason}\n")

        #result == 'Success'
        else:
            podID, elasticity_UT = dct['pod_id'], dct['elasticity UT']
            print(f'result: {result} - pod: {podID} - elasticity Upper Threshold: {elasticity_UT}\n')

    else:
        error_msg(f"Command:'{command}' Not Correct")



#---------- Main function ----------#
#This is where we put the different 
def main():
    while(1):
        
        try:
            command = input('$ ')
            
            #EXIT
            if command == 'exit':
                exit()

            #HELP
            elif command == 'cloud help':
                cloud_help()

            #1
            elif command == 'cloud init':
                cloud_init(rm_url)
            

            #POD MANAGEMENT
            #2
            elif command.startswith('cloud pod register'):
                cloud_pod_register(rm_url, command)

            #3
            elif command.startswith('cloud pod rm'):
                cloud_pod_rm(rm_url, command)

            #NODE MANAGEMENT
            #4
            elif command.startswith('cloud register'):
                cloud_register(rm_url, command)

            #5
            elif command.startswith('cloud rm'):
                cloud_rm(rm_url, command)

            #JOB MANAGEMENT
            #6
            elif command.startswith('cloud launch'):
                cloud_launch(rm_url, command)

            #RESUME & PAUSE
            #7
            elif command.startswith('cloud resume'):
                cloud_resume(rm_url, command)

            #8
            elif command.startswith('cloud pause'):
                cloud_pause(rm_url, command)

            #---------- MONOTORING COMMANDS ---------#
            #9
            elif command.startswith('cloud node ls'):
                cloud_node_ls(rm_url, command)
            
            #---------- REQUEST COMMANDS ---------#
            # #10
            # elif command.startswith('cloud request'):
            #     cloud_request(command)

            #---------- ELASTICITY COMMANDS ---------#
            elif command.startswith('cloud elasticity enable'):
                cloud_elasticity_enable(rm_url, command)

            elif command.startswith('cloud elasticity disable'):
                cloud_elasticity_disable(rm_url, command)

            elif command.startswith('cloud elasticity lower_threshold'):
                cloud_elasticity_lower_threshold(rm_url, command)


            elif command.startswith('cloud elasticity upper_threshold'):
                cloud_elasticity_upper_threshold(rm_url, command)



            else:
                error_msg(f"Command:'{command}' Not Recognized")
                
        except Exception as e:
            print(f"Error was raised\n{e}")

if __name__ == '__main__':
    main()