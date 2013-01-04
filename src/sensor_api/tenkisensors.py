import subprocess 
import time
import MySQLdb

'''
Created on May 11, 2011

The TenkiSensors class is used to connect and communicate to different usbtenki temperature sensors
that may be connected to different machines.

@author: rlaakkol
'''
DEFAULTDB = 'websensors'
TYPE = 'tenki'

class TenkiSensors():
    
    def __init__(self, dbhost='localhost', db=DEFAULTDB):
        """Initialize list of sensors and connect to database."""
        self.sensors = {}
        self.connectdb(dbhost, db)
        
        
    def connectdb(self,dbhost,db):
        """Connect to database."""
        self.db = MySQLdb.connect(host=dbhost,db=db)
        self.cursor = self.db.cursor()
            
    def update(self):
        """Add sensors that have previously been added to the database to the instance."""
        self.cursor.execute("""SELECT location,serial,ip,user,command FROM sensors_tempsensor WHERE type=%s""", (TYPE,))
        list = self.cursor.fetchall()
        for sensor in list:
            self.add_nodb(sensor[0], sensor[1], sensor[2], sensor[3], sensor[4])
        
    def remove(self, name):
        """Remove sensor from database and, if necessary, the instance."""
        if self.sensors.has_key(name):
            del self.sensors[name]
        self.cursor.execute("""DELETE FROM sensors_tempsensor WHERE location=%s""", (name,))

        
    def add(self, name, serial, ip='localhost', user='root', comm='/root/usbtenki-1.7/client/usbtenkiget'):
        """Add a sensor to the instance and, if necessary, the database."""
        if name in self.sensors:
            return -1
        self.sensors[name] = [serial, ip, comm, user]            
        self.cursor.execute("""INSERT INTO sensors_tempsensor (type,location,ip,serial,user,command) VALUE
                (%s,%s,%s,%s,%s,%s)""", (TYPE, name, ip, serial,user,comm))
        return len(self.sensors)
        
    def add_nodb(self, name, serial, ip='localhost', user='root', comm='/root/usbtenki-1.7/client/usbtenkiget'):
        """Add a sensor to the instance but not the database."""
        if name in self.sensors:
            return -1
        self.sensors[name] = [serial, ip, comm, user]
        return len(self.sensors)
        
    def amount(self):
        """Return the amount of sensors in the instance."""
        return len(self.sensors)
    
    def get_temp_nodb(self, name):
        """Return the temperature and humidity reading from a sensor without storing it into the database."""
        (serial, ip, comm, user) = self.sensors[name]
        if ip == 'localhost':
            p = subprocess.Popen([comm, '-s', serial, '-i0,1'], stdout=subprocess.PIPE)
        else: 
            p = subprocess.Popen(['ssh', '{0}@{1}'.format(user, ip), comm, '-s', serial, '-i0,1'], stdout=subprocess.PIPE)
        output, _ = p.communicate()
        tempstr, humstr = output.split(', ')
        temp, hum = float(tempstr.strip()), float(humstr.strip())
        return name, temp, hum
    
    def temp_to_db(self, name, temp, hum):
        """Store a temperature and humidity reading into the database."""
        if (self.cursor.execute("""SELECT id FROM sensors_tempsensor WHERE type=%s AND location=%s""", (TYPE, name,)) != 0):
            sensor_id = self.cursor.fetchone()[0]
            timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
            self.cursor.execute("""INSERT INTO sensors_tempreading (sensor_id,timestamp,tempreading,humreading) VALUE
                (%s,%s,%s,%s)""", (sensor_id, timestamp, temp, hum))
            return True
        else:
            return False
    
    def get_temp(self, name):
        """Retrieve temperature and humidity reading from sensor and store into database."""
        _, temp, hum = self.get_temp_nodb(name)
        if self.temp_to_db(name, temp, hum):
            return name, temp, hum
        else:
            return name, -1, -1
    
    def get_temp_all(self):
        """Apply get_temp() to all sensors in the instance."""
        return map(self.get_temp, self.sensors.keys())