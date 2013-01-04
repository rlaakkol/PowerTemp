from sensor_api import *
import time

'''
Created on May 31, 2011

@author: rlaakkol
'''

MAC_PREFIX = '000D6F0000'
t = 60

pw = pwcircles.PWCircles()
print(pw.add(MAC_PREFIX + 'B1BCE9', 'pieni'))
print(pw.add(MAC_PREFIX + 'B1DB78', 'iso'))

pieni = []
iso = []

for i in range(0,10):
    pieni.append(pw.get_pow('pieni')[1])
    iso.append(pw.get_pow('iso')[1])
    time.sleep(1)
    
print(pieni)
print(iso)
    
print "%f, %f" % (sum(pieni)/len(pieni), sum(iso)/len(iso))
    