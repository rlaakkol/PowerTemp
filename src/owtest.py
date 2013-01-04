'''
Created on Jul 4, 2011

@author: rlaakkol
'''
from sensor_api import *

ow = onewiresensors.OneWire()

ow.add('ardu1', 0, 'localhost', '/dev/ttyUSB0', 'rlaakkol')

print(ow.get_temp('ardu1'))