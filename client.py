#some code adapted from code from https://pymotw.com/3/socket/tcp.html#echo-server
import socket #import necessary modules
import logging
from time import time
from datetime import datetime

#creating the log file and socket
logging.basicConfig(filename = 'client.log', level = logging.DEBUG, format='%(message)s')
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_address = ('localhost',47600) #specifying the server name and port number

#function to end connection to server
def end():
    while True: #until "quit" is entered as input
        choice = input("Enter 'quit' to disconnect from server: ") #prompt user to disconnect
        if choice == "quit": #if user chooses to disconnect
            sock.sendall(bytes(choice,'utf-8')) #send the quit command to the server
            sock.close() #close the socket
            print('connection closed')
            break
        
try: #try to connect to the server
    sock.connect(server_address)
    print('Successfully connected to {} port {}'.format(*server_address))
    #alerting the user that the client is connected to the server
    working = True #carry on with program
except: #if the client can't connect
    check = sock.connect_ex(server_address) #check if port is open
    if check != 0: #if an error has occurred, alert the user that the port is busy
        print("Port is not open")
    sock.close() #close the socket
    print("Server Unavailable") #tell the user that the server is unavailable
    working = False #don't carry on with program
    
if working == True: #if connected to server
    artist = str(input("Enter name of artist: ")) #ask user name of artist
    if artist == "": #if no artist given, alert user
        print("No artist given")
        working = False #end program
        end() #run end() fucntion to close program
        
if working == True: #if connected to server and artist input
    try:
        message = bytes(artist,'utf-8') #convert artist from string
        print('sending',artist) #alert user artist being sent
        sock.sendall(message) #send artist name to server
        start = time() #record time sent for measuring response time
        data = sock.recv(64) #recieve response
        if not data: #if response not sent
            print("Nothing recieved from server") #alert user no response given
            working = False #end program
        if working == True: #if no errors so far
            print(data.decode('utf-8')) #decode the response
            total_bytes = -3
            #start counting total number of bytes recieved (-3 as "end" sent to show done with responses doesn't count)
            while data: #while data has been recieved
                data = sock.recv(64) #recieve more data from socket
                response = datetime.now() #mark time and date of first response
                total_bytes += len(data) #add response to total number of bytes
                sock.sendall(bytes("temp",'utf-8'))
                #send a random string to be recieved by server so multiple songs don't merge to same line
                print() #separate songs so more readable
                if data.decode('utf-8') == "end": #if the final message "end" has been sent"
                    last = time() #mark the time the responses were all recieved
                    diff = last-start #calculate the overall response time
                    #send information to log file
                    logging.info('It took '+str(diff)+' s to recieve a response from the server to get songs by '+artist)
                    logging.info('The response length was '+str(total_bytes)+' bytes')
                    logging.info('Server response recieved on '+str(response))
                    break #stop looking for more songs
                elif data: #if another song
                    print(data.decode('utf-8')) #decode and show user the song
    finally:
        end() #call the end() function
