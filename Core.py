#Global Imports
from blackbox import blackbox_core
import time
from threading import Thread

#Local Imports
import Parser
import Allowed

class Bot():
	def __init__(self, nickname='', realname = '', ident = '', owner = [], ssl = True):
		'''Create our bots name, realname, and ident, and create our IRC object, Commands object, Parser object, and users dict'''
		self.irc = blackbox_core.Core(logging=True, logfile="blackbox.txt", ssl=ssl)
		
		self.allowed = Allowed.Users()
		
		if owner:
			self.owner = owner
			if self.owner[0] not in self.allowed.keys:
				self.allowed.addOwner(self.owner[0], self.owner[1])
			
		self.p = Parser.Parse(sock=self.irc, allowed=self.allowed, nick=nickname)	
				
		if nickname:
			self.nickname = nickname
		else:
			self.nickname = 'WhergBot2'
		if realname:
			self.realname = realname
		else:
			self.realname = 'WhergBot [Ferus]'
		if ident:
			self.ident = ident
		else:
			self.ident = 'Wherg'

		
	def Connect(self, server, port=6697):
		'''Connect to the server, default the port to 6697 because SSL'''
		self.irc.connect(server, port)
		print("Connecting to {0} on port {1}".format(server, port))
		time.sleep(.3)
		self.irc.username(self.ident, self.realname)
		print("Sending username: {0} and realname: {1}".format(self.ident, self.realname))
		time.sleep(.3)
		self.irc.nickname(self.nickname)
		print("Sending nickname: {0}".format(self.nickname))
		time.sleep(.3)
		
	def Parse(self, msg):
		self.msg = msg.strip('\r\n')
		#self.raw = self.msg
		
		if not self.msg:
			self.irc._isConnected = False
			self.irc.close()
			raise blackbox_core.IRCError('Killed from server.')
			quit()
			
		else:
			try:
				self.msg = self.p.Main(self.msg)
				# [ Name, Ident@Host, Action, Loc, Text, Cmd ]
				self.nick = self.msg[0]
				self.host = self.msg[1]
				self.action = self.msg[2]
				if self.nickname == self.msg[3]:
					self.location = self.nick
				else:
					self.location = self.msg[3]
				self.text = self.msg[4]
				self.cmd = self.msg[5]
			except:
				pass

#			try:	#Gonna move this all to the Parser, Just commiting stuff now before I break it. xD						
#				if self.cmd == '$print':
#					print(str(self.allowed.db))
					
#				if self.cmd == '$access':
#					if self.allowed.db[self.nick][1] == 0: #Check if person is owner.
#						try:
#							levels = {0: self.allowed.addOwner, 1: self.allowed.addAdmin}
#							tmp = self.text.split()[1:]
#							
#							if tmp[0] == 'add':
#								if tmp[2] == 'None':
#									tmp[2] = None
#									
#								if int(tmp[3]) in levels.keys():
#									levels[int(tmp[3])](tmp[1], tmp[2])								
#								else:
#									self.allowed.addOther(tmp[1], tmp[2], int(tmp[3]))
#									
#								self.SendMsg(self.location, "{0}, {1} added at level {2}".format(tmp[1], tmp[2], tmp[3]))
#									
#							elif tmp[0] == 'del':
#								if self.allowed.levelCheck(tmp[1]):
#									if tmp[1] != self.owner[0]:
#										del self.allowed.db[tmp[1]]
#										self.SendMsg(self.location, "Deleted access for {0}".format(tmp[1]))
#								else:
#									self.SendMsg(self.location, "No access level found for {0}".format(tmp[1]))
#							
#							elif tmp[0] == 'show':
#								try:								
#									self.SendMsg(self.location, str(self.allowed.db[tmp[1]]))
#								except Exception, e:
#									print(e)
#									
#							
#						except Exception, e:
#							self.SendNotice(self.nick, "Format for {0} is: {0} add/del Nick Ident@host Level".format(self.cmd))
#							print("* [Access] Error\n{0}".format(str(e)))				
#
#			except:
#				pass
			
			
