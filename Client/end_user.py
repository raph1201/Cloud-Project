import pycurl
from threading import Thread
import time

rm_url = '10.140.17.105:3000'
lb_url_light = '10.140.17.105:5000'
lb_url_medium = '10.140.17.105:5001'
lb_url_heavy = '10.140.17.105:5002'

#Prints all commands to the console
def client_help():
    cmd_lst = {"client request:" : "Sends client request to backend server through LB. Syntax: 'client request [L, M, H]'"}
    print("---------------------------------------- HELP ----------------------------------------")
    print("Welcome to Help, here you will find a list of useful commands\n")
    for cmd in cmd_lst:
        print(cmd, "\n\t", cmd_lst[cmd])


def error_msg(msg):
    print(msg)
    print("Please check out 'client help' for our list of valid commands")


def client_request(command):
    command_ls = command.split()

    if len(command_ls) == 3: 
        if command_ls[2] == 'L':
            print("Sending light request to lb: " + lb_url_light)
            t = Thread(target=runRequest, args=(lb_url_light,))
            t.start()

        elif command_ls[2] == 'M':
            print("Sending medium request to lb: " + lb_url_medium)
            t = Thread(target=runRequest, args=(lb_url_medium,))
            t.start()

        elif command_ls[2] == 'H':
            print("Sending heavy request to lb: " + lb_url_heavy)
            t = Thread(target=runRequest, args=(lb_url_heavy,))
            t.start()

        else:
            error_msg(f"Error: Please put L (light), M (medium) or H (heavy) as ID")

    else:
        error_msg(f"Command:'{command}' Not Correct")


def runRequest(lb_url):
    t_cURL = pycurl.Curl()
    t_cURL.setopt(t_cURL.URL, lb_url)
    start_time = time.time()
    t_cURL.perform()
    end_time = time.time()
    print("Total time : " + str(end_time-start_time) + " seconds. \n")



#---------- Main function ----------#
#This is where we put the different 
def main():
    print("\n**Welcome to our client service. Please feel free to run different workloads (L, M or H) on our provided servers and let us take care of managing resources. If you need help, you can enter 'client help' and we will provide you with clarifications. Thank you for using our service!**\n")
    while(1):
        command = input('$ ')
        
        #EXIT
        if command == 'exit':
            exit()

        #HELP
        elif command == 'client help':
            client_help()

        #---------- USED USER REQUEST COMMAND ---------#
        elif command.startswith('client request'):
            client_request(command)

        else:
            error_msg(f"Command:'{command}' Not Recognized")

if __name__ == '__main__':
    main()