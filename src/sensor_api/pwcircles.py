from plugwise import *
from serial.serialutil import SerialException
import MySQLdb

DEFAULTDB = 'websensors'

'''
Created on May 11, 2011

The PWCircles class is used to connect and communicate with a network of Plugwise-devices.
The Plugwise Stick has to be attached to the computer the program is run on.

@author: rlaakkol
'''
class PWCircles():
    
    def __init__(self, dev='/dev/ttyUSB0', dbhost='localhost' ,db=DEFAULTDB):
        """Initialize the list of PW circles and connect to the Stick and database."""
        self.circles = {}
        self.dev = Stick(dev)
        self.connectdb(dbhost,db)
        
        
    def connectdb(self, dbhost, db):
        """Connect to the database."""
        self.db = MySQLdb.connect(host=dbhost, db=db)
        self.cursor = self.db.cursor()
        
    def update(self):
        """Add sensors that have previously been added to the database to the instance."""
        self.cursor.execute("""SELECT * FROM sensors_powersensor""")
        list = self.cursor.fetchall()
        for sensor in list:
            self.add(sensor[2], sensor[1])
        
    def add(self, mac, name):
        """Add a new sensor to the instance and the database."""
        try:
            self.circles[name] = Circle(mac, self.dev)
            state = self.relay_state(name)
            if (self.cursor.execute("""SELECT id FROM sensors_powersensor WHERE mac=%s""", (mac,)) == 0):
                self.cursor.execute("""INSERT INTO sensors_powersensor (target,mac,state) VALUE
                (%s,%s,%s)""", (name, mac, state))
            
            return len(self.circles)
        except (TimeoutException, SerialException, ValueError):
            return -1
        
    def remove(self, name):
        """Remove a sensor from the database and, if necessary, the instance."""
        if self.circles.has_key(name):
            del self.circles[name]
        self.cursor.execute("""DELETE FROM sensors_powersensor WHERE target=%s""", (name,))
    
    def amount(self):
        """Return the amount of circles."""
        return len(self.circles)
    
    def get_pow_nodb(self, name):
        """Return the power reading from a sensor without storing it into the database."""
        try:
            pow = self.circles[name].get_power_usage()
            return name, pow
        except (TimeoutException, SerialException):
            return name, -1
    
    def pow_to_db(self, name, pow):
        """Store a reading into the database."""
        if (self.cursor.execute("""SELECT id FROM sensors_powersensor WHERE target=%s""", (name,)) != 0):
                sensor_id = self.cursor.fetchone()[0]
                timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
                self.cursor.execute("""INSERT INTO sensors_powerreading (sensor_id,timestamp,reading) VALUE
                (%s,%s,%s)""", (sensor_id, timestamp, pow))
                return True
        else:
                return False

    def get_pow(self, name):
        """Aqcuire a power reading and store it into the database."""
        _, pow = self.get_pow_nodb(name)
        if pow > -1 and self.pow_to_db(name, pow):
            return name, pow
        else:
            return name, -1
        
    def get_pow_all(self):
        """Return power readings from all sensors in the instance and store them into the database."""
        return map(self.get_pow, self.circles.keys())
    
    def relay_state(self,name):
        """Return the relay state value of the sensor. Value 1 means the device is on, 0 means it is off."""
        state = self.circles[name].get_info()['relay_state']
        self.cursor.execute("""UPDATE sensors_powersensor SET state=%s WHERE target=%s""", (state, name))
        return state
    
    def switch_off(self,name):
        """Switch off the device."""
        self.circles[name].switch_off()
        self.cursor.execute("""UPDATE sensors_powersensor SET state=0 WHERE target=%s""", (name,))
        
    def switch_on(self,name):
        """Switch on the device."""
        self.circles[name].switch_on()
        self.cursor.execute("""UPDATE sensors_powersensor SET state=1 WHERE target=%s""", (name,))
        
    
    
        