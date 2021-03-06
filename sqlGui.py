import PySimpleGUI as sg
import sqlite3
import os
from shutil import copyfile
import sounddevice as sd
from scipy.io.wavfile import write

def getUserData(dbPath):
    sg.theme('DarkAmber') #color
    fs = 44100
    seconds = 5

    #window layout
    layout = [  [sg.Text('')],
                [sg.Text('Enter Username: '), sg.InputText()],
                [sg.Text('Enter Password:  '), sg.InputText()],
                [sg.ReadButton('Record')],
                [sg.Button('Ok')] ]

    # Create the Window
    window = sg.Window('Sign Up', layout)
    
    # Event Loop to process "events" and get the "values" of the inputs
    while True:
        event, values = window.read()
        #values are inputs from user
        if("@" not in values[0] or "." not in values[0] or len(values[0]) == 0 or len(values[1]) == 0):
            sg.Popup('Username is invalid')
            continue
        else:
            conn = sqlite3.connect(dbPath)
            c = conn.cursor()
            c.execute("SELECT COUNT(*) FROM User")
            number_of_entries = c.fetchone()[0]

            #check if username is not used.
            if number_of_entries != 0:
                c = conn.cursor()
                c.execute("SELECT userId FROM User WHERE userId=" + values[0])
                if not c.fetchall():
                    sg.Popup('Username is already used')
                else:
                    #add user
                    c = conn.cursor()
                    c.execute("INSERT INTO User VALUES (?, ?, ?, ?)", (number_of_entries + 1, values[0], values[1], 0))
                    conn.commit()
                    break
            else:
                #add user
                c = conn.cursor()
                c.execute("INSERT INTO User VALUES (?, ?, ?, ?)", (number_of_entries + 1, values[0], values[1], 0))
                conn.commit()
                break
            conn.close()

            if event == 'Record':
                sg.Popup("You have 5 seconds. Say your name and where you live")
                myrecording = sd.rec(int(seconds * fs), samplerate=fs, channels=2)
                sd.wait()  # Wait until recording is finished
                dest = "/opt/mycroft/skills/useridentification-skill/allUsers/" + str(number_of_entries + 1) + "-" + values[0] + "-1" + ".wav"
                write(dest, fs, myrecording)
    window.close()
    #source = "/tmp/mycroft_utterances/" + getCurrentUserAnswer()
    #copyfile(source, dest)

def getCurrentUserAnswer():
	#get current question sound file	
	#/tmp/mycroft_utterance(timestamp).wav
	allWaveFilePaths = []	
	for root, dirs, files in os.walk("/tmp/mycroft_utterances"):
		for file in files:
			allWaveFilePaths.append(file)
	return sorted(allWaveFilePaths)[0]
