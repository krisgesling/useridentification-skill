from mycroft import MycroftSkill, intent_file_handler
import os
from shutil import copyfile
import os
import sqlite3
import sys

sys.path.append("/opt/mycroft/skills/useridentification-skill")
from sqlGui import getUserData
from voiceRecognition import voiceFound, voiceMatched



class Useridentification(MycroftSkill):
	def __init__(self):
	        MycroftSkill.__init__(self)

	def converse(self, utterances):
		utt = utterances[0]
		block_utterance = None
		if self.voc_match(utt, 'useridentification.intent'):
			# mock the standard message object to pass it to a standard intent handler
			mock_message = {'data': {'utterance': utt}}

			is_authenticated = self.handle_useridentification(mock_message)
		else:
			return False
		self.log.info("is_authenticated: {}".format(is_authenticated))
		# If authenticated return False to continue processing utterance
		# Else return True to prevent further handling of utterance
		block_utterance = not is_authenticated
		return block_utterance



	#What to do when skill is triggered
	@intent_file_handler('useridentification.intent')
	def handle_useridentification(self, message):
		is_authenticated = False

		#connect to database
		conn = sqlite3.connect('/opt/mycroft/skills/useridentification-skill/allUsers/Users.db')
		c = conn.cursor()
		c.execute("SELECT * FROM User")

		if c.fetchone() == None:
			self.speak("No user is currently registered")
			is_authenticated = self.prompt_for_registration()
		else:
			currentUser = ""
			for row in c.execute("SELECT * FROM User"):
				self.speak(row[0])
				if row[3] == '1':
					currentUser = row[0]
			self.speak(currentUser)
			currentUserAnswer = getCurrentUserAnswer()

			if voiceMatched(currentUser, currentUserAnswer):
				is_authenticated = True
			elif voiceFound(currentUserAnswer):
				self.signIn("")
				is_authenticated = True
			else:
				is_authenticated = self.prompt_for_registration()

		conn.close()
		return is_authenticated


	def prompt_for_registration(self):
		registered = False
		answer = self.ask_yesno("Do you want to sign up?")
		if (answer == "yes"):
			self.signUp()
			registered = True
		elif (answer == "no"):
			self.speak("Goodbye")
		else:
			self.speak(answer)
			self.speak("Answer is invalid")
		return registered


	def signIn(self, userId):
		conn = sqlite3.connect('/opt/mycroft/skills/useridentification-skill/allUsers/Users.db')
		c = conn.cursor()
		if(userId == ""):
			c.execute("SELECT * FROM User")
			if not (c.fetchone() == None):
				for row in c.execute("SELECT * FROM User"):
					if (voiceMatched(row[1], getCurrentUserAnswer())):
						userId = row[0]
						username = row[1]
						password = row[2]
		else:
			for row in c.execute("SELECT * FROM User"):
				if (row[0] == userId):
					username = row[1]
					password = row[2]

		#set current user in database
		c.execute("UPDATE User SET CurrentUser = 0 WHERE CurrentUser = 1")
		c.execute("UPDATE User SET CurrentUser = 1 WHERE ID = " + str(userId))
		conn.commit()
		conn.close()


	def signUp(self):
		audioFile = getCurrentUserAnswer()
		getUserData('/opt/mycroft/skills/useridentification-skill/allUsers/Users.db')

		conn = sqlite3.connect('/opt/mycroft/skills/useridentification-skill/allUsers/Users.db')
		c = conn.cursor()
		c.execute("SELECT COUNT(*) FROM User")

		self.signIn(c.fetchone()[0])
		return True


def getCurrentUserAnswer():
	#get current question sound file
	#/tmp/mycroft_utterance(timestamp).wav
	allWaveFilePaths = []
	for root, dirs, files in os.walk("/tmp/mycroft_utterances"):
		for file in files:
			allWaveFilePaths.append(file)
	return "/tmp/mycroft_utterances/" + sorted(allWaveFilePaths)[0]

def create_skill():
	return Useridentification()
