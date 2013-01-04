from sensor_api import *




'''
Created on May 30, 2011

@author: rlaakkol
'''



MAC_PREFIX = '000D6F0000'

tenki = tenkisensors.TenkiSensors()
#tenki.add(('A09281'), 'eka')
tenki.add('armi', 'A0928A', '10.129.255.230')
print(tenki.amount())
#print(tenki.get_temp('eka'))
print(tenki.get_temp('toka'))
print(tenki.get_temp_all())

pw = pwcircles.PWCircles()
pw.add(MAC_PREFIX + 'B19D36', 'kakkonen')
pw.add(MAC_PREFIX + '99275B', 'ykkonen')
pw.add(MAC_PREFIX + 'B1BCE9', 'pieni')
pw.add(MAC_PREFIX + 'B1DB78', 'iso')
print(pw.amount())
print(pw.get_pow('ykkonen'))
print(pw.get_pow('kakkonen'))
print(pw.get_pow_all())
