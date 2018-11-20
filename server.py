#importing all necessary modules
import socket
import logging
from time import time
from datetime import datetime

#creating the log file
logging.basicConfig(filename = 'server.log', level = logging.DEBUG, format='%(message)s')

#opening the text file
fname = "100worst.txt"
contents = []
with open(fname) as file:
    for i,line in enumerate(file):
        contents.append(line) #reading the text file line by line
    file.close()

#initialising variables and lists
song_end = []
songs = []
artist_end = []
artists = []
j = 1
next_line = 0

#function to find the positions of the song and artist in each line of the text file if it contains a song
def add_song(num):
    global contents #global variables
    global song_end
    global artist_end
    global next_line
    global j
    if num == str(j): #checking to see if line is expected number and so contains a song
            end = contents[i].find("  ") #find the end of the song name
            song_end.append(end)
            j+=1 #next song number
            if end == -1: #checking whether artist is on same line
                next_line = 1
            else:
                end = contents[i].find("  ",35) #finding the end of the artists' name
                artist_end.append(end)
    else:
        song_end.append("") #marking lines without songs so same length as lines in text file
        artist_end.append("")

#function to end the connection to the client
def final():
    global done #global variables
    global start
    if done == 0: #if not already checked
        end = connection.recv(64) #check message from client
        end = str(end)
        end = end[2:-1]
        if end == "quit": #carry on if the message is "quit"
            done = 1
    if done == 1:
        print("connection closed")
        last = time()
        diff = last - start #calculate time connected to client
        logging.info(str(diff)+" is connection time") #send time to log file
        connection.close() #end connection

#calling the add_song() function on every line of the text file
for i in range(len(contents)):
    if next_line == 1: #if the artist is on the line after the corresponding song
        end = contents[i].find("  ",35)
        artist_end.append(end) #note the end position of the artists' name
        next_line = 0
    if j<10: #take the first character in the line as the song number, checked in add_song() function
        num = contents[i][0]
        add_song(num) #checks if a song is there and marks the positions of the song and artist in the line
    elif j<100: #takes first 2 characters as song number
        num = contents[i][0:2]
        add_song(num) #call add_song() fucntion
    else:
        num = contents[i][0:3] #call add_song() on 100th song
        add_song(num)

#adding the song and artist names to lists
for i in range(len(song_end)):
    if song_end[i] == "": #if that line has no song
        pass
    elif song_end[i] == -1: #if the artist is on the next line
        songs.append(contents[i][4:-1]) #adding characters from start of song to end of line(and song)
        artists.append(contents[i+1][35:artist_end[i]]) #adding characters from start to end of artist
    else:
        if contents[i][34] == "-": #if a "-" separates the song and artist
            songs.append(contents[i][4:34]) #add the song to list of songs
        else:
            songs.append(contents[i][4:song_end[i]]) #add song to list of songs
        artists.append(contents[i][35:artist_end[i]])#add artist to list of artists

#create and fill dictionary of songs and artists
music = {}
for i in range(len(songs)):
    if "/" in artists[i]: #if multiple artists for one song
        split = artists[i].find("/")
        music.setdefault(artists[i][:split].lower(),{})[songs[i]]=1 #add each artist as a key and add the shared song as a value for both
        music.setdefault(artists[i][split+1:].lower(),{})[songs[i]]=1
    else:
        music.setdefault(artists[i].lower(),{})[songs[i]]=1 #add the artist and have the song as a key in a dictionary so it can't be repeated

#code below adapted from code from https://pymotw.com/3/socket/tcp.html#echo-server
sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM) #create socket
server_address = ('localhost',47600) #specify server name and port number
while True: #until an open port is found
    try:
        print('starting up on {} port {}'.format(*server_address)) #tell the user the server address
        sock.bind(server_address) #bind the socket to the server address
        sock.listen(1) #listen for a client trying to connect
        begin = str(datetime.now()) #mark the date and time the server was started
        logging.info(begin+' server started') #send information to log file
        break #open port has been found
    except:
        print("Port busy, try different port") #alerting user if port is busy
        port = int(input("Enter port number: ")) #allowing the user to enter a different port number
        server_address = ('localhost',port) #updating server address
        
while True: #keep waiting for connection
    done = 0 #initialise varibles
    print('waiting for a connection') #alert user waiting for connection
    artist = ""
    connection,client_address = sock.accept() #accept a connection when a request is made
    start = time() #mark the time at the start of the connection
    begin = datetime.now() #mark the date and time the client connection request was made
    logging.info(str(begin)+' client connection request') #send the information to the log file
    try:
        print('connection from', client_address) #report that a connection has been made
        logging.info('request successful') #log that the request was successful
        data = connection.recv(64) #recieve the artist from the client
        word = str(data)
        word = word[2:-1]
        artist += word #convert artist to string form for comparison to dictionary
        print('received {!r}'.format(data)) #report to user the artist name the server recived
        if data: #if an artist was given
            print('sending confirmation back to the client')
            connection.send(b'request recieved successfully') #confirm to client that the artist was recieved
            logging.info(artist) #log the artist in the log file
            if artist.lower() in music.keys(): #if the artist name in any form (lower or upper case) is in the dictionary
                artist_songs = music.get(artist.lower()) #get the dictionary holding the songs by that artist as keys
                if len(artist_songs.items()) == 0: #if the artist has no songs
                    message = "no songs"
                    print(message) #tell user
                    connection.sendall(bytes(message,'utf-8')) #tell client
                    connection.recv(64) #recieve a message "temp" to separate songs sent to client
                for k,v in artist_songs.items(): #for each song by the artist
                    print(k)
                    connection.sendall(bytes(k,'utf-8')) #send the song(the key)
                    connection.recv(64) #recieve a message "temp" to separate songs sent to client
                connection.sendall(bytes("end",'utf-8')) #send "end" to client so it knows no more songs are coming
            elif artist == "quit": #if there was no input for artist, "quit" was the first message sent so end the program
                done = 1
            else:
                message = "artist not found" #if artist not recognised, report back
                print(message)
                connection.sendall(bytes(message,'utf-8')) #tell client no artist found
                connection.recv(64) #recieve a message "temp" to separate songs sent to client
                connection.sendall(bytes("end",'utf-8')) #send "end" to client so it knows no more messsages are coming
            final() #close the connection with the final() function
        else:
            print('no data recieved from', client_address) #if no data at all recieved
            final() #close the connection with the final() function
    finally:
        final() #close the connection with the final() function
