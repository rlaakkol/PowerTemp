#!/usr/bin/env python

from sensor_api import *
import sys
import argparse
import time

parser = argparse.ArgumentParser(description='Control plugwise devices')

parser.add_argument('-f', '--funct', choices=['switch_on', 'switch_off', 'get_pow', 'get_state', 'get_temp', 'list_devs', 'add_pw'], help='Choice of action: switch_on and switch_off do what they say, get_pow returns the power consumption of the device, and get_state returns the relay state, list_devs lists the available devices.', required=True)
parser.add_argument('-d', '--dev', metavar='device', nargs='+', help='The devices the action is taken on.', default=['all'])
parser.add_argument('-m', '--mac', help='MAC of plugwise to add, only for add_pw function')
parser.add_argument('-n', '--name', help='Name of sensor to add, only for add_pw function')

a = parser.parse_args()

pw = pwcircles.PWCircles()
pw.update()
t = tenkisensors.TenkiSensors()
t.update()

if (a.funct == 'list_devs'):
	print '----PlugWises----:'
	for name in pw.circles.keys():
		print name
	print '\n----Temp sensors-----:'
	for name in t.sensors.keys():
		print name
	sys.exit(0)

if (a.funct == 'add_pw'):
	pw.add(a.mac, a.name)
	sys.exit(0)
	

if (a.funct != 'get_temp'):
	devs = pw.circles.keys() if a.dev == ['all'] else a.dev
	if devs != ['all']:
		for name in devs:
			if not pw.circles.has_key(name):
				print 'No such device: {0}'.format(name)
				sys.exit(-1)
	
	for name in devs:
		if a.funct == 'switch_on':
			pw.switch_on(name)
			print 'Switched ON {0}'.format(name)
		elif a.funct == 'switch_off':
			pw.switch_off(name)
			print 'Switched OFF {0}'.format(name)
		elif a.funct == 'get_pow':
			print '{0}: {1} W'.format(name, pw.get_pow_nodb(name)[1])
		else:
			print '{0} is turned {1}'.format(name, 'ON' if pw.relay_state(name) == 1 else 'OFF')
		time.sleep(1)

else:	
	devs = t.sensors.keys() if a.dev == ['all'] else a.dev
	if devs != ['all']:
		for name in devs:
			if not t.sensors.has_key(name):
				print 'No such device: {0}'.format(name)
				sys.exit(-1)
	
	for name in devs:
		if a.funct == 'get_temp':
			temp = t.get_temp_nodb(name)
			print '{0}: {1} W'.format(name, temp[1], temp[2])
		time.sleep(1)
	

