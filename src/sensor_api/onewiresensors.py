import serial
import MySQLdb
import time
import subprocess

'''
Created on Jun 30, 2011

@author: rlaakkol
'''

DEFAULTDB = 'websensors'
TYPE = 'onewire'

class OneWire:
    
    def __init__(self, db=DEFAULTDB):
        self.sensors = {}
        self.db = MySQLdb.Connect(db=db)
        self.cursor = self.db.cursor()
        
        # Add sensors previously in the database
        self.cursor.execute("""SELECT location,num,ip,dev,user,command FROM sensors_tempsensor WHERE type=%s""", (TYPE,))
        list = self.cursor.fetchall()
        for sensor in list:
            self.add_nodb(sensor[0], sensor[1], sensor[2], sensor[3], sensor[4], sensor[5])
        
        
    def add(self, name, idx, ip='localhost', dev='/dev/ttyUSB0', user='root', comm='arduread'):
        if name in self.sensors:
            return -1
        self.sensors[name] = [idx, dev, ip, user, comm]
        self.cursor.execute("""INSERT INTO sensors_tempsensor (type,location,ip,dev,num,user,command) VALUE
                (%s,%s,%s,%s,%s,%s,%s)""", (TYPE, name, ip, dev, idx, user, comm))
        return len(self.sensors)
    
    def add_nodb(self, name, idx, ip='localhost', dev='/dev/ttyUSB0', user='root', comm='arduread'):
        if name in self.sensors:
            return -1
        self.sensors[name] = [idx, dev, ip, user, comm]
        return len(self.sensors)
    
    def get_temp(self, name):


        if (self.cursor.execute("""SELECT id FROM sensors_tempsensor WHERE type=%s AND location=%s""", (TYPE, name)) != 0):
            _, temp = self.call_ardu(name)
            timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
            sensor_id = self.cursor.fetchone()[0]
            self.cursor.execute("""INSERT INTO sensors_tempreading (sensor_id,timestamp,reading) VALUE
                (%s,%s,%s)""", (sensor_id, timestamp, temp))
            
        return name,temp
        
        
        
    def call_ardu(self, name):
        [idx,dev,ip,user,comm] = self.sensors[name]
        if ip == 'localhost':
            p = subprocess.Popen([comm, dev], stdout=subprocess.PIPE)
        else:
            p = subprocess.Popen(['ssh', '{0}@{1}'.format(user, ip), comm, dev], stdout=subprocess.PIPE)
        output, _ = p.communicate()
#        ser = serial.Serial(dev, 9600, timeout=1)
#        ser.write('a')
#        time.sleep(0.1)
#        output = ser.readline();
        output = output.strip('\n').split();
        for res in output:
            temp = res.split(':')
            if int(temp[0]) == idx:
                return idx, temp[1]
        return idx,-1
        
               
        