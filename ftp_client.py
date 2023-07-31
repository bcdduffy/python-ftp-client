import argparse
from socket import *
import socket
import os
import sys
#I created a small tutorial to use my ftp client script just to make sure that you would be able to know how my script works

#How to invoke the script: python ftp.py <user>:<password>@<server> <command> <options>

# Firstly the script supports authenticaiton
# An incorrect username: python ftp.py wrongname:ece3564@38.68.237.219 ls bren.txt
# Will fail authenticaiton with the server exiting the program returning 1

# An incorrect password: python ftp.py anonymous:ece35@38.68.237.219 ls bren.txt
# Will fail authenticaiton with the server exiting the program returning 1

# An incorrect IP address: python ftp.py anonymous:ece3564@38.68.237.218 ls bren.txt
# Will cause a timeout

#LS command support
###########################################################################
#Calling ls: python ftp.py <user>:<password>@<server> <ls> <remote_dir>
#Example: python ftp.py anonymous:ece3564@38.68.237.219 ls bren.txt
#Will produce just the bren.txt dir

#Example: python ftp.py anonymous:ece3564@38.68.237.219 ls
#Will produce the directory of the FTP server were supposed to test with returning 0 for a succefful execution

#The ls command will return a 0 on a successful execution and 1 on a fail, failing can be triggered by passing a remote directory that doesnt exist on the FTP server
#python ftp.py anonymous:ece3564@38.68.237.219 ls br
#This will print nothing and will exit the program returning 1 due to it passing a remote directory that does not exist

#GET command support
############################################################################
###
#Calling ls: python ftp.py <user>:<password>@<server> <get> <remote_dir> <local_dir>
#Example: python ftp.py anonymous:ece3564@38.68.237.219 get bren.txt brenFile_pull.txt
#Will pull the contents of the file in the remote direcrtory into the file specified at the local directory, this will pull bren.txt into a file brenFile_pull.txt

#The get command will return a 0 on a successful execution and 1 on a fail, failing can be triggered by passing a remote directory that doesnt exist on the FTP server
# or if too few arguments are specified
#Example: python ftp.py anonymous:ece3564@38.68.237.219 get bren7000.txt brenFile_pull.txt
#This will exit the program returning 1
#If the local directory path is incorrect there will be no issue, the client will create a new file and get the contents into that

#PUT command support
#############################################################################
#Calling put: python ftp.py <user>:<password>@<server> <put> <remote_dir> <local_dir>
#Example: python ftp.py anonymous:ece3564@38.68.237.219 put bren.txt brenFile.txt
#Will put the contents of the local directory into the remote directory file specified

#The get command will return a 0 on a successful execution and 1 on a fail, failing can be triggered by passing a local directory that doesnt exist in your current local directory
# or if too few arguments are specified
#Example: python ftp.py anonymous:ece3564@38.68.237.219 put bren.txt brenNotFile.txt
#This will exit the program returning 1
#If the remote directory path is incorrect there will be no issue, the client will create a new file and put the contents into that one, this is intentional

#BYE command support
#############################################################################
#If the client ever does connect to the FTP server it will always before ending the script send the BYE command to the FTP server to close the connection
#This happens whether or not the command executions are successful or not and is handled by the callBYE() command


errorFlag = False
def callLS():
    newoption = ' '+option1
    if option1 == '':
        list_command = 'LIST\r\n'
    else:
        list_command = 'LIST'+ newoption +'\r\n'
    client_socket.send(list_command.encode())
    response = client_socket.recv(BUFFER_SIZE)
    directory_listing = b''
    count = 0
    while True:
        data = data_socket.recv(BUFFER_SIZE)
        if not data and count == 0:
            callBYE(True)
        if not data:
            break
        directory_listing += data
        count = count+1
    print(directory_listing.decode())


def callGET():
    newoption = ' '+option1
    if option1 == '' or option2 == '':
        callBYE(True)
        return
    get_command = 'RETR'+newoption+'\r\n'
    client_socket.send(get_command.encode())
    response = client_socket.recv(BUFFER_SIZE)
    if response.decode()[0:3] == '550':
        callBYE(True)
    file_contents = b''
    while True:
        data = data_socket.recv(1024)
        if not data:
            break
        file_contents += data
    file = open(option2, 'wb')
    file.write(file_contents)
    file.close()


def callPUT():
    if option1 =='' or option2 == '':
        callBYE(True)
        return
    put_command = 'STOR ' + option1+ '\r\n'
    client_socket.send(put_command.encode())
    #Checks if remote directory exists
    if not os.path.isfile(option2):
        callBYE(True)
    # Open the file to read the data
    with open(option2, 'rb') as file:
        while True:
            data = file.read(BUFFER_SIZE)
            if not data:
                break
            data_socket.send(data)

def callBYE(erro):
    bye_command = 'BYE\r\n'
    client_socket.send(bye_command.encode())


    client_socket.close()
    data_socket.close()
    if(erro == True):
        print("Exited with Error | Returning 1")
        exit(1)
    print("Exited without Error | Returning 0")
    exit(0)

#parser = argparse.ArgumentParser(description='specify login info')
#parser.add_argument('login', metavar='login', type=str, help='enter your login info')
#parser.add_argument('command', metavar='command', type=str, help='enter your command')
#parser.add_argument('option', action='append', default='', metavar='option', type=str, help='enter option')
args_list = sys.argv[3:]
#parser.add_argument('--nargs', nargs='+')
#args = parser.parse_args()
#login = args.login
login = sys.argv[1]
command = sys.argv[2]
options = args_list
if len(args_list) > 0:
    option1 = args_list[0]
    if len(args_list) > 1:
        option2 = args_list[1]
    else:
        option2 = ''
else:
    option1 = ''
    option2 = ''
colon_split = login.split(':')
if(len(colon_split) > 1):
    user = colon_split[0]
    password = colon_split[1]
    at_split = colon_split[1].split('@')
    if(len(at_split) > 1):
        password = at_split[0]
        server = at_split[1]


    else:
        print("Error: no '@' character in login info")
        print("Exited with Error | Returning 1")
        exit(1)
else:
    print("Error: no ':' character in login info")
    print("Exited with Error | Returning 1")
    exit(1)
SERVER_ADDRESS = server
SERVER_PORT = 21
BUFFER_SIZE = 1024
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((SERVER_ADDRESS, SERVER_PORT))
response = client_socket.recv(BUFFER_SIZE)
#print(response.decode())
user_command = 'USER ' + user +'\r\n'
client_socket.send(user_command.encode())
response = client_socket.recv(BUFFER_SIZE)
password_command = 'PASS ' + password + '\r\n'
client_socket.send(password_command.encode())
response = client_socket.recv(BUFFER_SIZE)
if response.decode()[0:3] == '530':
    print("Authentication Failed")
    print("Exited with Error | Returning 1")
    client_socket.close()
    exit(1)
type_command = 'TYPE I\r\n'
client_socket.send(type_command.encode())
response = client_socket.recv(BUFFER_SIZE)
pasv_command = 'PASV\r\n'
client_socket.send(pasv_command.encode())
response = client_socket.recv(BUFFER_SIZE)
decoded_resp = response.decode()
numfield = decoded_resp[decoded_resp.find('(')+1:decoded_resp.find(')')]
firstpor = int(numfield.split(',')[-1])

secondpor = int(numfield.split(',')[-2])
ip_address = response.decode().split(',')[0][-3:].replace(',', '')
port_number = secondpor*256 + firstpor
ip_address2 = numfield.split(',')[-6] + '.'+ numfield.split(',')[-5] + '.' + numfield.split(',')[-4] + '.' + numfield.split(',')[-3]
data_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
data_socket.connect((ip_address2, port_number))
if command == 'ls':
    callLS()
elif command == 'get':
    callGET()
elif command == 'put':
    callPUT()
#elif args.command == 'bye':
# callBYE()
callBYE(False)
