import asyncio
import aioble
from binascii import hexlify
from bluetooth import UUID
from dht import DHT22
from machine import deepsleep, Pin, unique_id
from struct import pack

### Configurable parameters follow ###

DEVICE_NAME = "Outdoor_Weather"
LED_GPIO = 2  # GPIO of status LED.
DHT_GPIO = 4  # GPIO attached to DHT data line. 
AWAKE_TIME_SECS = 60   # How long to spend advertising and servicing clients.
SLEEP_TIME_SECS = 120  # How long to spend in deep sleep.

### No need to change anything below this line ###

# See also: https://www.bluetooth.com/specifications/assigned-numbers/
ADV_APPEARANCE_GENERIC_SENSOR = 0x0540
ENV_SENSE_UUID = UUID(0x181A)
ENV_SENSE_TEMP_UUID = UUID(0x2A6E)
ENV_SENSE_HUM_UUID = UUID(0x2A6F)

BLE_ADV_INTERVAL_uS = 250_000

# Initializing to zero makes it obvious when there is a faulty sensor.
temp_Celsius = 0
humidity_pct = 0

led = Pin(LED_GPIO, Pin.OUT)
led.off()

base_mac = unique_id()  # WiFi MAC
bluetooth_mac = bytearray(base_mac)
bluetooth_mac[5] += 2   # ESP32 Bluetooth MAC is always WiFi MAC + 2

print(DEVICE_NAME)
print(hexlify(bluetooth_mac, ':').decode().upper())

print("Initializing sensor.")
dht = DHT22(Pin(DHT_GPIO))

print("Registering BLE services.")
env_sensing_service = aioble.Service(ENV_SENSE_UUID)
temp_characteristic = aioble.Characteristic(
    env_sensing_service, ENV_SENSE_TEMP_UUID, read=True, notify=False
)
hum_characteristic = aioble.Characteristic(
    env_sensing_service, ENV_SENSE_HUM_UUID, read=True, notify=False
)
aioble.register_services(env_sensing_service)


# BLE characteristics use little-endian format, often with fixed-point decimals.
def encode_temperature(t_deg_c):
    return pack("<h", int(t_deg_c * 100))

def encode_humidity(h_pct):
    return pack("<h", int(h_pct * 100))

# Read sensor values only once, because upon after deep sleep the device will
# reboot and all of this will happen again.
async def read_sensor():
    global temp_Celsius, humidity_pct

    print("Reading from sensor.")
    led.on()
    try:
        dht.measure()
        temp_Celsius = dht.temperature()
        print(f"Temperature: {temp_Celsius}° C")
        humidity_pct = dht.humidity()
        print(f"Humidity: {humidity_pct}%")
    except OSError:
        print(f"Sensor malfunction! Check wiring to GPIO {DHT_GPIO}")
    else:
        led.off()
    print("Writing sensor data to BLE characteristics.")
    temp_characteristic.write(encode_temperature(temp_Celsius), send_update=True)
    hum_characteristic.write(encode_temperature(humidity_pct), send_update=True)
    await asyncio.sleep(AWAKE_TIME_SECS)
    print("Going to sleep.")
    deepsleep(SLEEP_TIME_SECS * 1000)  # Helps mitigate sensor self-heating.

# Serially wait for connections. Don't advertise while central is connected.
async def communicate_readings():
    print("Advertising availability of data.")
    while True:
        async with await aioble.advertise(
            BLE_ADV_INTERVAL_uS,
            name=DEVICE_NAME,
            services=[ENV_SENSE_UUID],
            appearance=ADV_APPEARANCE_GENERIC_SENSOR,
            manufacturer=(0xffff, encode_temperature(temp_Celsius) + encode_humidity(humidity_pct))
        ) as connection:
            print("Client connect:", connection.device)
            await connection.disconnected(timeout_ms=None)
            print("Client disconnect.")


async def main():
    task1 = asyncio.create_task(read_sensor())
    task2 = asyncio.create_task(communicate_readings())
    await asyncio.gather(task1, task2)

asyncio.run(main())
