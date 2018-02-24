#!/usr/bin/python
# coding:utf8

import sys
import time
import telnetlib

from common_base import *
from symbol_terminal import SymbolTerminal


class DeviceManager:
	###################### parameters
	terminal = None
	CONN_TIMEOUT = 90.0
	HOST = "127.0.0.1"
	PORT = "23"
	LOGIN = "userg"
	PASS = "paswod"

	#dataModeSymb = "\033\001" # Esc, Ctrl+A
	sendSymb = '\r\n' # Enter

	lastMsg = ""
	lastCommonMsgMaxLen = 1000
	lastCommonMsg = ""

	###################### functions
	# constructor
	def __init__(self, host='127.0.0.1', port='23', login='', passw=''):
		global isDebug
		self.HOST = host
		self.PORT = port
		self.LOGIN = login
		self.PASS = passw
		self.terminal = SymbolTerminal(True, False)

	def isTerminalOpened(self):
		return (self.terminal is not None and self.terminal.isOpened())

	# blocking method: read terminal msg an and fill variable by it
	def readTerminalMsg(self, targetMsg, timeoutSecs=5, errMsg="Error. ", resLStr=None):
		global isDebug
		if resLStr is None: resLStr = [None]
		if len(resLStr) < 2:
			resLStr.append(None)
		resLStr[1] = None
		if not self.isTerminalOpened():
			resLStr[1] = "readTerminalMsg: terminal is not opened."
			writeLog(resLStr[1])
			return False
		resultText = self.terminal.readUntil(str(targetMsg).encode('ascii'), timeoutSecs)
		if resLStr is not None:
			resLStr[0] = str(resultText)
		if resultText is not None and len(resultText) > 0:
			self.lastMsg = str(resultText)
			self.lastCommonMsg += self.lastMsg
			if len(self.lastCommonMsg) > self.lastCommonMsgMaxLen:
				startInd = len(self.lastCommonMsg) - self.lastCommonMsgMaxLen
                                self.lastCommonMsg = self.lastCommonMsg[startInd:]
		if (len(resultText) == 0) or (not isSubstr(str(resultText), str(targetMsg))):
			resLStr[1] = errMsg
			if isDebug: 
				if len(resultText) > 0:
					print('<[readTerminalMsg]> '+ resultText + '<[end]> ')
				print(errMsg)
			return False
		else:
			if isDebug: 
				print('<[readTerminalMsg][needed]> '+ resultText + '<[needed][end]> ')
			return True

	# nonblocking method: read available terminal msg an and fill variable by it
	def readAvailableTermMsg(self):
		global isDebug
		if not self.isTerminalOpened():
			writeLog("readAvailableTerminalMsg: terminal is not opened.")
			return None
		resultText = self.terminal.readAvailable()
		if not (resultText is None) and len(resultText) > 0:
			self.lastMsg = str(resultText)
			self.lastCommonMsg += self.lastMsg
			if len(self.lastCommonMsg) > self.lastCommonMsgMaxLen:
				startInd = len(self.lastCommonMsg) - self.lastCommonMsgMaxLen
				self.lastCommonMsg = self.lastCommonMsg[startInd:]
			return resultText
		return None

	def initConnection(self, overAUC=False, overlastDevice=False):
		global isDebug
		self.terminal.close()
		time.sleep(0.2)
		self.terminal.open(self.HOST, self.PORT, None, None, self.CONN_TIMEOUT)
		if not self.isTerminalOpened():
			writeLog("initConnection: terminal is not opened.")
			return False
		resLStr = ['']
		termMsg = ['']
		maxTryings = 40
		tryings = 0

		bResult = self.readTerminalMsg( r'Login:', 3, "Error timeout: can't login to telnet-server.", termMsg)
		while 1:
			if isSubstr(termMsg[0], 'Login:'):
				# enter login
				self.terminal.write((self.LOGIN + self.sendSymb).encode('ascii'))
				
				bResult = self.readTerminalMsg( r'Password:', 10, "Error timeout: password prompt isn't received.")
				if not bResult:	
					return False
				time.sleep(1.0)
				# enter pas_word
				self.terminal.write((self.PASS + self.sendSymb).encode('ascii'))
				
				time.sleep(1.0)
				break
			else:
				time.sleep(0.2)
				#self.terminal.write((self.dataModeSymb).encode('ascii'))
				bResult = self.readTerminalMsg( r'Login:', 0.2, "Notice: waiting for login prompt. Step " + str(tryings + 1) + " of " + str(maxTryings), termMsg)
				if bResult:
					continue
				tryings += 1
				if tryings > maxTryings:
					return False
		return True

	def sendCommand(self, commandStr):
		global isDebug
		if not self.isTerminalOpened():
			writeLog("terminal is not opened.")
			return
		self.terminal.write(commandStr.encode('ascii'))	
		if isDebug: 
			print("Sent command: " + commandStr.encode('ascii'))

	def clearConnection(self, logout=True):
		# Завершение сеанса связи с HLR
		self.lastCommonMsg = ""
		self.lastMsg = ""
		if logout:
			pass
		self.terminal.close()

	def reinitTerminal(self):
		if self.isTerminalOpened():
			try:
				self.clearConnection()
				#time.sleep(2.1)
			except:
				pass
		del self.terminal
		self.terminal = None
		self.terminal = SymbolTerminal(True, False)
		writeLog("[Device manager] Terminal has been recreated.")

###################### Main code
if __name__ == '__main__':
	pass

