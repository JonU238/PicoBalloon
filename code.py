import busio
import board
import adafruit_gps
import time
import digitalio
import analogio
import WSPRencode
import adafruit_si5351
import microcontroller

print("Imported libs")

WSPRTONESETTINGS = ([15,0,0,26,601405,1000000],[15,0,0,26,601402,1000000],[15,0,0,26,601399,1000000],[15,0,0,26,601396,1000000])
SYMBOL_PERIOD = 0.683  # seconds per WSPR symbol

callsign = u"KC1MOL"

def valtoBvolt(val):
    return val*0.00005082184881644613*2

def Bvolttoval(Bvolt):
    return (Bvolt/2)*19676.5765765765779002252

def latlon_to_grid(lat: float, lon: float) -> str:
    # Normalize lat and lon
    lon += 180.0
    lat += 90.0

    grid = [""] * 6

    # Derive first coordinate pair
    grid[0] = chr(int(lon // 20) + ord('A'))
    grid[1] = chr(int(lat // 10) + ord('A'))

    # Derive second coordinate pair
    lon = lon - (int(lon // 20) * 20)
    lat = lat - (int(lat // 10) * 10)
    grid[2] = chr(int(lon // 2) + ord('0'))
    grid[3] = chr(int(lat) + ord('0'))

    # Derive third coordinate pair
    lon = lon - (int(lon // 2) * 2)
    lat = lat - int(lat)
    #grid[4] = chr(int(lon * 12) + ord('a'))
    #grid[5] = chr(int(lat * 24) + ord('a'))

    return "".join(grid)

def transmit_sequence(symbols,radio):
    for s in symbols:
        print(s)
        radio.clock_1.configure_fractional(radio.pll_a, WSPRTONESETTINGS[s][3], WSPRTONESETTINGS[s][4], WSPRTONESETTINGS[s][5])
        time.sleep(SYMBOL_PERIOD)
        

def timeToWait(min, sec,lastgpstime):
    min = (((min*60+sec)+(time.monotonic()-lastgpstime))/60)%60

    sec = (min - int(min))*60.0

    min = int(min)
    if min%2 == 0:
        return 120-sec
        #return 120*2+(120-sec)
        #return 1
    else:
        return 60-sec
        #return 120*2+(60-sec)
        #return 1
    
def getState(v,gps):
    try:
        if gps.altitude_m is None:
            state0 = "0"
        if gps.altitude_m>3000:
            state0 = "1"
        if gps.altitude_m>5000:
            state0 = "2"
        if gps.altitude_m>8000:
            state0 = "3"
        if gps.altitude_m>12000:
            state0 = "4"
        if gps.altitude_m>15000:
            state0 = "5"
    except:
        state0 = "1"
    return int(state0+"0")


def aquireGPS(powerPin,gps,bvolt,bvlowpoint):
    powerPin.value = True
    time.sleep(1)
    #gps.send_command(b"PMTK314,0,1,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0")
    time.sleep(1)
    gps.update()
    has_fix = False
    while(bvolt.value>bvlowpoint and not has_fix):
        print(gps.update())
        cline = gps.readline().decode()
        if "$GNGGA" in cline:
            cline = cline.split(',')
            print(cline)
            gps.altitude_m = cline[9]
            print(gps.altitude_m)
            if cline[6] == '1':
                has_fix = True
        time.sleep(0.1)
    powerPin.value = False
    return gps.latitude,gps.longitude

def transmitTelem(powerPin,gps,bvolt,lastgpstime):
    state = getState(bvolt.value,gps)
    try:
        location = latlon_to_grid(gps.latitude,gps.longitude)
    except:
        location = latlon_to_grid(0.0,0.0)

    sequence = WSPRencode.wspr_encode(callsign,location,state)
    time.sleep(timeToWait(gps.timestamp_utc.tm_min,gps.timestamp_utc.tm_sec,lastgpstime)-4)
    powerPin.value = True
    time.sleep(4)
    i2c = busio.I2C(board.SCL, board.SDA)
    radio = adafruit_si5351.SI5351(i2c)
    radio.pll_a.configure_integer(15)
    radio.outputs_enabled = True
    transmit_sequence(sequence,radio)
    powerPin.value = False

    

#bvsetpoint = Bvolttoval(4.5)
bvsetpoint = Bvolttoval(4)
bvlowpoint = Bvolttoval(3)

#Turing the Power bus off by default
powerPin = digitalio.DigitalInOut(board.VCC_OFF)
powerPin.direction = digitalio.Direction.OUTPUT
powerPin.value = False

led = digitalio.DigitalInOut(board.LED)
led.direction = digitalio.Direction.OUTPUT



#Setting up the reading the bat voltage
bvolt = analogio.AnalogIn(board.P0_02)


#GPS setup
uart = busio.UART(board.TX, board.RX, baudrate=9600, timeout=10)
gps = adafruit_gps.GPS(uart, debug=False)


lastgpstime = -5*60*60

while True:
    led.value = True
    print("Loop Started")
    print(valtoBvolt(bvolt.value))
    try:
        if bvolt.value>bvsetpoint and time.monotonic()-lastgpstime>2*60*60:
            print("trying to aquire gps")
            aquireGPS(powerPin,gps,bvolt,bvlowpoint)
            
            if gps.latitude == None:
                print("didnt get gps:(")
            else:
                print("GotGPS!")
                lastgpstime = time.monotonic()
    except Exception as e:
        print(e)
    
    try:
        if bvolt.value>bvsetpoint:
            print("Sending wspr")
            transmitTelem(powerPin,gps,bvolt,lastgpstime)
                
    except Exception as e:
        print(e)
    led.value = False
    print("Im Going to sleep")
    time.sleep(15)


'''
My journy throught the air is destend to end in tragety... yet i go fourth into the great unknown because i can....
despite the fear i feel for the water of the sky or the water of the ground i trust my plastic will protect me and my gps will guide me
PLS if you find this... call me, ill pay you to send it back to me
Phone: 5086546807
Gmail: jamestfishes@gmail.com
'''