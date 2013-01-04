#!/usr/bin/env python

'''
Created on Jul 15, 2011

@author: rlaakkol
'''
from sensor_api import *
import time
import sys
import argparse
from socket import socket
import daemon

DEFDUR = 30
DEFINTV = 5

def parseavg(data):
    ret = []
    zipped = zip(*data)
    for row in zipped:
        name = row[0][0]
        points = zip(*row)[1]
        avg = sum(points, 0.0) / len(points)
        ret.append((name, avg))
    return ret

def monitor_loop(args, pw, tenki, f, sock):
    avgpdata = []
    avgtdata = []
    start = time.time()
    avgtime = start
    while (args.dur < 1 or start + args.dur > time.time()):
        temp = time.time()
        if pw:
            pres = map(pw.get_pow, args.pow)
            avgpdata.append(pres)
        if tenki:
            tres = map(tenki.get_temp, a.temp)
            avgtdata.append(tres)
    #    map)(tenki.get_temp, a.temp)
    #   f.write(str([time.strftime('%Y-%m-%d %H:%M:%S'), pres, tres])+'\n')

        lines = []
        if (time.time() - avgtime > args.avg):
            avgtime = time.time()
            avgp = parseavg(avgpdata)
            for line in avgp:
                lines.append("PW.%s_1min %s %d" % (line[0], str(line[1]),int( avgtime )))
            avgt = parseavg(avgtdata)
            for line in avgt:
                lines.append("Tenki.%s_1min %s %d" % (line[0], str(line[1]),int( avgtime )))
        if sock:
            for line in pres:
                lines.append("PW.%s %s %d" % (line[0], str(line[1]),int( temp )))
    #       print lines
            if (a.temp != None):
                for line in tres:
                                lines.append("Tenki.%s %s %d" % (line[0], str(line[1]),int( temp )))
            message = '\n'.join(lines) + '\n' #all lines must end in a newline
            try:
                sock.sendall(message)
            except IOError:
                f.write('Connection error')
                while (True):
                    try:
                        f.write('reconnecting')
                        if sock:
                            sock.close()
                        sock = socket()
                        sock.connect( (a.car, CARBON_PORT) )
                        f.write('success')
                        break
                    except IOError:
                        f.write('failure')
                        time.sleep(10)
    
                
                

        wait = args.intv - (time.time() - temp)
        if wait > 0:
            time.sleep(wait)
    

parser = argparse.ArgumentParser(description='Start monitoring sensors')

#parser.add_argument('--temp', '-t', metavar='tempsensor', nargs='+', help='The temperature sensors to be monitored', required=True)
parser.add_argument('--pow', '-p', metavar='powsensor', nargs='+', help='The power sensors to be monitored', required=True)
parser.add_argument('--temp', '-t', metavar='tempsensor', nargs='+', help='The temperature sensors to be monitored')
parser.add_argument('--dur', '-d', type=int, help='Duration of the monitoring period (in seconds)', default=DEFDUR)
parser.add_argument('--intv', '-i', type=int, help='Polling interval (in seconds)', default=DEFINTV)
parser.add_argument('--outf', '-o', help='Optional output file',  default='stdout')
parser.add_argument('--car', '-c', help='Address of carbon server')
parser.add_argument('--avg', '-a', type=int, help='Length of averaging period (for carbon only)', default=60)

a = parser.parse_args()

if a.pow:
    pw = pwcircles.PWCircles()
    pw.update()
else:
    pw = None

if a.temp:
    tenki = tenkisensors.TenkiSensors()
    tenki.update()
else:
    tenki = None
CARBON_PORT = 2003
print 'Address of carbon server: {0}'.format(a.car)

if (a.car != None):
    sock = socket()
    try:
        sock.connect( (a.car,CARBON_PORT) )
    except:
        print "Couldn't connect to %(server)s on port %(port)d, is carbon-agent.py running?" % { 'server':a.car, 'port':CARBON_PORT }
else:
    sock = None


if tenki:
    for name in a.temp:
        if not tenki.sensors.has_key(name):
            print 'No such sensor: {0}'.format(name)
            sys.exit(-1)

if pw:
    for name in a.pow:
        if not pw.circles.has_key(name):
            print 'No such sensor: {0}'.format(name)
            sys.exit(-1)

if (a.outf != 'stdout'):   
    f = open(a.outf, 'w')
else:
    f = sys.stdout
    monitor_loop(a, pw, tenki, f, sock)
print "Stopping"
f.close()
sock.close()
