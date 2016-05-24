#!/usr/bin/python -u

import time
import threading
from pylibftdi import Device as TellStick
from rf433.Protocol import Protocol, Device

class Application(object):

	def __init__(self, tellstick, baudrate=9600):
		self.tellstick = tellstick
		self.tellstick.baudrate = baudrate

		self.target = []
		self.wait_signal = threading.Event()
		self.running = threading.Event()

	def reader(self):
		# Tell writer we're ready to start reading
		self.wait_signal.set()

		while True:
			data = self.tellstick.read(1024)
			if data != '':
				print '<< %s' % data

	def writer(self):
		self.running.set()
		self.wait_signal.wait()

		# Send command to get firmware version
		toSend = 'V+'
		print '>> %s' % toSend
		self.tellstick.write(toSend)

		time.sleep(0.5)

		# You can repeat this block to send different commands etc
		myDevice = Protocol.protocolInstance('arctech')
		myDevice.setModel('selflearning-bell')
		myDevice.setParameters({'house': '15708170', 'unit': '1'})
		msg = myDevice.stringForMethod(Device.BELL, 0)
		if 'S' in msg:
			toSend = 'S%s+' % msg['S']
			print '>> %s' % toSend.encode('string_escape')
			self.tellstick.write(toSend)
		time.sleep(2) # Make sure you sleep or else it won't like getting another command so soon!

	def go(self):
		self.threatellStick = threading.Thread(target=self.writer)
		self.threatellStick.daemon = True
		self.threatellStick.start()

		# We wait for the writer to be actually running (but not yet
		# writing anything) before we start the reader.
		self.running.wait()
		self.thread2 = threading.Thread(target=self.reader)
		self.thread2.daemon = True
		self.thread2.start()

	def join(self):
		# Use of a timeout allows Ctrl-C interruption
		self.threatellStick.join(timeout=1e6)
		self.thread2.join(timeout=1e6)

if __name__ == '__main__':

	tellStick = TellStick(mode='t')
	tellStick.flush()
	app = Application(tellStick)
	app.go()
	app.join()
	tellStick.flush()
