#!/usr/bin/env python
'''
Created on Jul 5, 2011

@author: rlaakkol
'''
import serial
import sys
import time

dev = sys.argv[1]

ser = serial.Serial(dev, 9600, timeout=1)

if len(sys.argv) > 2 and sys.argv[2] == 'n':
        ser.write('n')
        time.sleep(0.1)
        out = ser.readline()
else:
        ser.write('a')
        time.sleep(0.1)
        out = ser.readline()

print(out)

