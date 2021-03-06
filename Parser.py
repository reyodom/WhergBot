#!/usr/bin/python2
#Global Imports
from threading import Thread
#Local Imports
import Commands

class Parse():
	def __init__(self, sock=None, allowed=None, nick=None):
		self.sock = sock
		self.allowed = allowed	
		self.nickname = nick
		
		self.users = {} #Storage for Users of each channel. The Key is channel, users are a list.
		
		self.command = Commands.Commands(sock=self.sock, parser=self, nick=self.nickname, allowed=self.allowed)
		self._commands = self.command.cmds.keys()
		
	def Main(self, msg):
		'''Main Parser, Here we take raw data, split at \r\n, and add it to a buffer.'''
		tmp = msg.splitlines()

		if len(tmp) >1: #Somehow this handles the bunched up lists when connecting. Weird.
			for msg in tmp:
				msg = msg.split()
				print(msg)
				
				try:				
					if msg[1] == '353' and msg[2] == self.nickname: # Move this? \( ._.)/
						nameslist = []
						for x in msg[5:]:
							x = x.replace(":","").replace("~","").replace("&","").replace("@","").replace("%","").replace("+","")
							nameslist.append(x)
							
							if x not in self.allowed.db.keys():
								self.allowed.db[x] = [None, 5]
							
						self.users[msg[4]] = nameslist					
				except:
					pass
					
		else:
			for msg in tmp:
				tmp = msg #The full message as a string.
				msg = msg.split() #The message split, a list of strings.
				#print(msg) #Temporary printing here, until we define the rest of the parser.

				try:
					# Parts, Joins, Kicks, All IRC actions
					# CTCP: '\x01TIME\x01' ['Ferus', 'anonymous@the.interwebs', 'PRIVMSG', 'WhergBot2', '\x01TIME\x01', '\x01TIME\x01']

					if msg[1] == 'KICK' and msg[3] == self.nickname:
						'''Auto-rejoin if we are kicked.'''
						self.sock.send("JOIN {0}".format(msg[2]))
						
					if msg[1] == 'PRIVMSG':
						self.Privmsg(tmp)
				
					if msg[1] == 'NOTICE':
						self.Notice(tmp)
						
					if msg[1] == 'INVITE':
						self.Invited(msg)			

					if msg[1] == 'JOIN':
						self.Joined(msg)
						
					if msg[1] == 'PART':
						self.Parted(msg)
						
					if msg[1] == 'QUIT':
						self.Quitted(msg)
					
					else:
						pass #Havent finished defining everything.
	
				except:
					pass
					
	
	def Privmsg(self, msg):
		'''Parse for commands. Etc.'''
		try:
			Nick = self.Nick(msg)
			Host = self.Host(msg)
			Action = self.Action(msg)
			Location = self.Loc(msg)
			Text = self.Text(msg)
			Cmd = self.Cmd(msg)
			Msg = [Nick, Host, Action, Location, Text, Cmd]
			print("* [Privmsg] [{0}] <{1}> {2}".format(Location, Nick, Text))
			
			cmdVar = '$'
			'''If a command is called, check the hostname and access level of the person who called it, and if they have access, execute the command.'''				
			if Cmd.startswith(cmdVar) and Cmd[1:] in self._commands:
				check = self.allowed.levelCheck(Nick)[1]
				if check[1] <= self.command.cmds[Cmd[1:]][1]:
					if self.command.cmds[Cmd[1:]][2]:
						if Host == check[0]:
							t = Thread(target=(self.command.cmds[Cmd[1:]])[0](Msg))
							t.daemon = True
							t.start()
						else:
							self.SendNotice(Nick, "You do not have the required authority to use this command.")
					else:
						t = Thread(target=(self.command.cmds[Cmd[1:]])[0](Msg))
						t.daemon = True
						t.start()

		except Exception, e:
			print("* [Privmsg] Error")
			print(str(e))
			
	def Notice(self, msg):
		Nick = self.Nick(msg)
		Host = self.Host(msg)
		Action = self.Action(msg)
		Location = self.Loc(msg)
		Text = self.Text(msg)
		print("* [Notice] <{0}> {1}".format(Nick, Text))
	
	
	def Nick(self, msg):
		'''Parses the nick of a person who sent a message'''
		try:
			n = msg.split("!")[0].strip(":")
			return n
		except:
			return ''
			
	def Host(self, msg):
		'''Parses the Ident@Host of a person who sent a message'''
		try:
			h = msg.split("!")[1].split(" ")[0]
			return h
		except:
			return ''
		
	def Text(self, msg):
		'''Parses out the text in a message'''
		try:
			t = msg.split(" :")[1]
			return t
		except:
			return ''
		
	def Cmd(self, msg):
		'''Parses for a `command`'''
		try:
			c = msg.split(" :")[1].split()[0]	
			return c
		except:
			return ''
	
	def Loc(self, msg):
		'''Parses for the location from a PRIVMSG or NOTICE'''
		try:
			l = msg.split()[2]
			return l
		except:
			return ''
	
	def Action(self, msg):
		'''Parses for the type of action that is happening, IE: PRIVMSG, NOTICE'''
		try:
			a = msg.split()[1]
			return a
		except:
			return ''



	def Invited(self, msg):
		'''Join a channel we were invited to if the person's hostname is defined in allowed.'''
		try:
			person, host = msg[0].split(":")[1].split("!")
			if self.allowed.db[person][0] == host:
				chan = msg[3][1:]
				self.sock.join(chan)
			print("* [IRC] Invited to {0}, by {1}. Now joining.".format(chan, person))	
		except:
			pass

	def Joined(self, msg):
		'''Someone joined, add them to allowed, with level 5 access, no hostname, and add them to the channel users list.'''
		try:
			person, host = msg[0].split(":")[1].split("!")
			chan = msg[2].strip(":")
			if person not in self.allowed.keys:
				self.allowed.db[person] = [None, 5]
			self.users[chan].append(person)
			print("* [IRC] {0} ({1}) joined {2}.".format(person, host, chan))
		except:
			pass
		
		
	def Parted(self, msg):
		'''Someone parted a channel, remove them from the channel users list.'''
		try:
			person, host = msg[0].split(":")[1].split("!")
			self.users[msg[2]].remove(person)
			print("* [IRC] {0} ({1}) parted {2}.".format(person, host, msg[2]))
		except:
			pass
		
	def Quitted(self, msg):
		try:
			person, host = msg[0].split(":")[1].split("!")
			for chan in self.users.keys():
				if person in self.users[chan]:
					self.users[chan].remove(person)
			print("* [IRC] {0} ({1}) has quit.".format(person, host))
		except:
			pass
						
	def SendRaw(self, msg):
		self.sock.send(msg)

	def SendMsg(self, location, msg):
		self.sock.say(location, msg)
	
	def SendNotice(self, location, msg):
		self.SendRaw("NOTICE {0} :{1}".format(location, msg))
