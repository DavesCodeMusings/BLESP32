# BLESP32
BLESP32 is a portmanteau of BLE (for Bluetooth Low Energy) and ESP32, the venerable Espressif microcontroller. What you'll find here is a MicroPython program that runs on an ESP32 to collect data from the popular DHT22 temperature and humidity sensor, sending it out not only as traditional GATT characteristics, but also in BLE advertising packets that can be captured in ESPHome's Bluetooth Tracker for relaying to Home Assistant.

## Why?
I wanted a device that could communicate periodic sensor data while spending most of its time in deep sleep. I wanted this data relayed to my home automation hub.

GATT characteristics are the traditional way to make information available from BLE devices. But, it requires a fairly reliable connection. In other words, the device providing the data has to be up and responding. Having a device that periodically goes into deep sleep does not fit well with this connection oriented protocol.

An alternative to GATT characteristics is required.

## How?
The solution adopted by many device manufacturers is to broadcast sensor information using data fields in the BLE advertisement. I'm doing the same thing here. Using the _Manufacturer Data_ field, I'm encoding the temperature and humidity readings from the DHT22 sensor into the BLE advertisement. ESPHome is able to receive this advertisement and decode the data with lambda functions. From there it's sent to Home Assistant.

## Show Me the Code!
The MicroPython code is all contained in `main.py`. Simply upload it to an ESP32 flashed with a recent version of MicroPython. You'll also need to install the `aioble` library package for Bluetooth. [mip](https://docs.micropython.org/en/latest/reference/packages.html) is a fabulous tool to do this.

Obviously, you'll need a DHT22 temperature / humidity sensor as well.

To communicate the temperature/humidity sensor readings to Home Assitant, you'll need another ESP32 flashed with [ESPHome](https://esphome.io/). The `esphome_ble_gateway.yml` file in this repository is your guide to getting it configured.

## Configuration
There are a handful of parameters in `main.py` you can use to customize the behavior of the BLESP32 device, starting with DEVICE_NAME and ending with SLEEP_TIME_SECS. The names are pretty self-explanitory and there are comments as well.

## Troubleshooting
There are a number of steps to go from the DHT22 sensor to the home automation hub. Each one can be a potential problem.

The BLESP32 device's LED (if you have one configured) will turn on when the DHT22 sensor is being accessed and turn off after a successful read. If the LED stays on, there's probably something wrong with the wiring of the DHT22.

Attaching the ESP32 to a host computer over USB will show debug information in the form of print statements. Included in this is the Bluetooth MAC address for the device. The correct MAC is required for ESPHome to recognize the device's advertisements.

```
Outdoor_Weather
1D:EC:AF:C0:FF:EE
Initializing sensor.
Registering BLE services.
Reading from sensor.
Temperature: 21.6° C
Humidity: 72.1%
Writing sensor data to BLE characteristics.
Advertising availability of data.
```

When ESPHome is receiving, the log output will show the temperature and humidity readings being sent to Home Assistant. Check for the presence of these values. They should match the temperature and humidity in the debug output of the BLESP32 device.

```
[03:21:52][D][sensor:094]: 'DHT22 Temperature': Sending state 21.60000 ° C with 2 decimals of accuracy
[03:21:52][D][sensor:094]: 'DHT22 Humidity': Sending state 72.10000 % with 2 decimals of accuracy
```

Finally, check the entities in Home Assistant.

## Customizing
You're not limited to only reading temperature and humidity. Any kind of sensor you can read with MicroPython should work. The biggest limitation will be the size of the _Manufacturer Data_ field used to broadcast the information. 24 bytes is the maximum amount of data you can send. 
https://stackoverflow.com/questions/33535404/whats-the-maximum-length-of-a-ble-manufacturer-specific-data-ad

Other things to keep in mind are BLE's convention of sending data in little endian format and often with a fixed-point decimal as well. This is really only important if you're using GATT characteristics in addition to the data broadcast in the _Manufacturer Data_ field of the BLE advertisement.

There is no standard for the _Manufacturer Data_ field other than the 16-bit company IDs available for use. Registration is required for these. But, the Company ID of 0xFFFF used in `main.py` is reserved for testing and should be safe to use in a small home environment.

## Next Steps
My goal was to create a temperature / humidity sensor that could stand up to the extreme winter temperatures where I live. The DHT22 is well suited for that. I may also configure an ESP32 with a rechargeable Litium Polymer battery to use as vehicle presense sensor. What you do with yours is up to you. If you'd like to share your project, drop a line in the [Issues](https://github.com/DavesCodeMusings/BLESP32/issues) Use the [show &amp; tell](https://github.com/DavesCodeMusings/BLESP32/labels/show%20%26%20tell) label.
