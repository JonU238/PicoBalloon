import busio
import board
import time
import digitalio
import analogio
import WSPRencode
from silicon5351 import SI5351_I2C

print("Imported libs")

BASE_FREQ = 14150000.0  # Hz, example WSPR dial frequency (adjust as needed)
#TONE_SPACING = 80
TONE_SPACING = 1.4648   # Hz between 4FSK tones
SYMBOL_PERIOD = 0.683  # seconds per WSPR symbol


callsign = u"KC1MOL"
print("Set callsign to:",callsign)



def latlon_to_grid(lat: float, lon: float) -> str:
    # Bounds checks
    if lat < -90.0:
        lat = -90.0
    if lat > 90.0:
        lat = 90.0
    if lon < -180.0:
        lon = -180.0
    if lon > 180.0:
        lon = 180.0

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

def set_wsper_tone(symbol):
    """Set Si5351 to the frequency for the given WSPR symbol (0–3)."""
    freq = BASE_FREQ + float(symbol) * TONE_SPACING
    print(type(freq))
    set_clock1_frequency(freq)

def transmit_sequence(symbols):
    si.enable_output(output=1)
    for s in symbols:
        print(s)
        set_wsper_tone(s)
        time.sleep(SYMBOL_PERIOD)
    si.disable_output(output=1)

def timeToWait(min, sec):
    if min%2 == 0:
        #return 120-sec
        return 1
    else:
        #return 60-sec
        return 1
    

def set_clock1_frequency(freq_hz):
    print(f"Changing freq to: {freq_hz:.2f}")
    #si.disable_output(output=1)
    si.set_freq_fixedpll(output=1, freq=freq_hz)
    #si.enable_output(output=1)


bvsetpoint = 1000
bvlowpoint = 100

#Turing the Power bus off by default
powerPin = digitalio.DigitalInOut(board.VCC_OFF)
powerPin.direction = digitalio.Direction.OUTPUT
powerPin.value = True


#Setting up the reading the bat voltage
bvolt = analogio.AnalogIn(board.BAT_VOLT)


#transmitter setup
crystal = 25e6     # crystal frequency
mul = 15           # 15 * 25e6 = 375 MHz PLL frequency
freq = 14.5e6       # output frequency with an upper limit 200MHz
quadrature = True  # lower limit for quadrature is 375MHz / 128
invert = False     # invert option ignored when quadrature is true

i2c = busio.I2C(board.SCL, board.SDA)
while not i2c.try_lock():
        pass
si = SI5351_I2C(i2c, crystal=crystal)
si.setup_pll(pll=0, mul=mul)
si.init_clock(output=1, pll=0, quadrature=quadrature, invert=invert)
si.set_freq_fixedpll(output=1, freq=freq) 
si.enable_output(output=1)

#powerPin.value = False

while True:
        location = latlon_to_grid(42,-77)
        sequence = WSPRencode.wspr_encode(callsign,location,10)
        print("Tis time to tx")
        print(sequence)
        transmit_sequence(sequence)


'''
My journy throught the air is destend to end in tragety... yet i go fourth into the great unknown because i can....
'''