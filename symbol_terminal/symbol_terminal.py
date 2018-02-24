#!/usr/bin/python
# coding:utf8

import sys, traceback
import time
from datetime import datetime as dttm
from datetime import timedelta
import telnetlib
import paramiko
from socket import timeout as SocketTimeoutException

# Here is second variant of telnet client
# import pycurl
# from StringIO import StringIO

from common_base import *


class SymbolTerminal:
	###################### parameters
	tn = None

	ssh = None
	sshChanel = None

	###################### functions
	# constructor
	def __init__(self, enableTelnet=True, enableSSH=False):
		global isDebug

		if enableTelnet:
			self.tn = telnetlib.Telnet()
		elif enableSSH:
			self.ssh = paramiko.client.SSHClient()
			try:
				self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
			except:
				writeLog("Error: self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy()). __init__ of SymbolTerminal")

	def __isOpenedTelnet(self):
		filenoVar = None
		if (self.tn is not None
                        and (str(type(self.tn)).find(r'instance') != -1 or str(type(self.tn)).find(r'class') != -1)):
			try:
				filenoVar = self.tn.fileno()
			except:
				return False
			if filenoVar is not None and self.tn.get_socket() != 0 and self.tn.get_socket() is not None:
				return True
		return False

	def __isOpenedSSH(self):
		return (self.ssh is not None 
			and (str(type(self.ssh)).find(r'instance') != -1 or str(type(self.ssh)).find(r'class') != -1) 
			and self.ssh.get_transport() != None)

	def isOpened(self):
		if self.tn is not None:
			return self.__isOpenedTelnet()
		elif self.ssh is not None:
			return self.__isOpenedSSH()
		return False

	def readUntil(self, msg, timeout=13.0):
		global isDebug
		# telnet realization
		if self.__isOpenedTelnet():
			str1 = filterString(self.tn.read_until(msg, timeout), None)
			if isDebug:
				if str1 is None or len(str1) < 1: 
					writeLog("DEBUG [read]: " + str(type(str1)) + ". wait for: \"" + msg + "\"", True)
				else: writeLog("DEBUG [read]: " + filterString(str1), True)
			return str1
		# ssh realization
		elif self.__isOpenedSSH():
			# non-blocking mode
			#self.sshChanel.setblocking(0)
			#self.sshChanel.settimeout(0)
			resStr = b''
			msgLen = len(msg)
			TIME_STEP = 0.05

			startTime = dttm.now()
			curDeltaNum = 0.0
			timeDlt = None
			# выполняем цикл пока не вышло время timeout и пока не найдена искомая строка msg в конце принятого от терминала текста
			while curDeltaNum < timeout and (msgLen > len(resStr) or not resStr.encode('ascii').endswith(msg)):
				try:
					resStr += self.sshChanel.recv(1)
				except SocketTimeoutException:
					time.sleep(TIME_STEP)
				except:
					raise NameError("[terminal reading] ATTENTION!!! error type (edit code by this type): " + str(sys.exc_info()[0]) + "; text: " + str(sys.exc_info()[1]))
				timeDlt = dttm.now() - startTime
				if timeDlt.days < 0:
					raise NameError('TerminalSSH: Reading Timeout Incorrect')
				curDeltaNum = (timeDlt.days * 86400.0) + timeDlt.seconds + (timeDlt.microseconds / 1000000.0)
			return filterString(resStr, None) #.encode('ascii')
		else:
			raise NameError('TerminalTransportDoesntExistOrClosed: self.sshChanel: ' + str(type(self.sshChanel)) + ', self.ssh: ' + str(type(self.ssh)))

	def readAvailable(self):
		global isDebug
		# telnet realization
		if self.__isOpenedTelnet():
			#return filterString(self.tn.read_until(r'!!!<nothing12345>!!!', 0.2), None)
			str1 = filterString(self.tn.read_very_eager(),  None)
			if isDebug:
				if str1 is None or len(str1) < 1: pass
				else: writeLog("DEBUG [read_available]: " + filterString(str1), True)
			return str1
		# ssh realization
		elif self.__isOpenedSSH():
			raise NameError('TerminalTransportDoesntExistOrClosed: self.sshChanel: ' + str(type(self.sshChanel)) + ', self.ssh: ' + str(type(self.ssh)))
		else:
			raise NameError('TerminalTransportDoesntExistOrClosed!')

	def close(self):
		if self.__isOpenedTelnet():
			self.tn.close()
			writeLog("Terminal has been closed.")
		if self.__isOpenedSSH():
			if self.sshChanel is not None:
				self.sshChanel.close()
				self.sshChanel = None
			if self.ssh is not None:
				self.ssh.close()
				writeLog("Terminal has been closed.")

	def open(self, host, port, login='', password='', connTimeout=90):
		# Telnet
		if self.tn is not None:
			self.tn.open(host, str(port), connTimeout)
		# SSH
		elif self.ssh is not None:
			self.ssh.connect(host, int(port), login, password, None, None, connTimeout, True, True, False, None, False, False, True, None, connTimeout, connTimeout)
			if not self.ssh.get_transport().is_authenticated():
				raise NameError('TerminalSSHError: Is Not Opened Or Authenticated!')
			self.sshChanel = self.ssh.invoke_shell('vt100')
			self.sshChanel.setblocking(0)
			self.sshChanel.settimeout(0.0)
		writeLog("Terminal has been OPENED.")

	def write(self, msg, timeout=90.0):
		global isDebug
		if self.isOpened():
			# Telnet
			if self.__isOpenedTelnet():
				self.tn.write(msg)
				if isDebug: writeLog("DEBUG [WRITE]: " + filterString(msg), True)
			# SSH
			elif self.__isOpenedSSH():
				# sendall(msg) will change non-blocking mode to blocking mode! (then data will be readed from begining)
				totalLen = len(msg)
				wroteStrLen = 0
				# variables for timeout
				TIME_STEP = 0.05
				startTime = dttm.now()
				curDeltaNum = 0.0
				timeDlt = None
				while curDeltaNum < timeout and wroteStrLen < totalLen:
					try:
						wroteStrLen += self.sshChanel.send(msg)
					except SocketTimeoutException:
						time.sleep(TIME_STEP)
					except:
						raise NameError("[terminal writing] ATTENTION 2!!! error type (edit code by this type): " + str(sys.exc_info()[0]) + "; text: " + str(sys.exc_info()[1]))
					timeDlt = dttm.now() - startTime
					if timeDlt.days < 0:
						raise NameError('TerminalSSH: there is Incorrect a processing of writing timeout')
					curDeltaNum = (timeDlt.days * 86400.0) + timeDlt.seconds + (timeDlt.microseconds / 1000000.0)
				#self.sshChanel.sendall(msg)
		else:
			raise NameError('Error: There is none of an opened terminal.')


###################### Main code
if __name__ == '__main__':
	pass

