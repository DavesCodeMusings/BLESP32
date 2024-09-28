# BLESP32
BLESP32 is a portmanteau of BLE (for Bluetooth Low Energy) and ESP32, the venerable Espressif microcontroller. What you'll find here is a MicroPython program that runs on ESP32 to collect data from the popular DHT22 temperature and humidity sensor, sending it out not only as traditional GATT characteristics, but also in BLE advertising packets that can be captured in ESPHome's Bluetooth Tracker for relaying to Home Assistant.

## Why?
I wanted a device that could communicate periodic sensor data while spending most of its time in deep sleep. I wanted this data relayed to my home automation hub. GATT characteristics are the traditional way to make information available from BLE devices. But, it requires a connection. So the device providing the data has to be up and responding. Having a device that periodically goes into deep sleep does not fit well with connection oriented protocols. An alternative to GATT characteristics is required.

## How?
The solution adopted by many device manufacturers is to broadcast sensor information using data fields in the BLE advertisement. I'm doing the same thing here. Using the _Manufacturer Data_ field, I'm encoding the temperature and humidity readings from the DHT22 sensor into the BLE advertisement. ESPHome is able to receive this advertisement and decode the data with a lambda function. From there it's sent to Home Assistant.

## Show Me the Code!
The MicroPython code is all contained in `main.py`. Simply upload it to an ESP32 flashed with a recent version of MicroPython. You'll also need to install the `aioble` library package for Bluetooth. [mip](https://docs.micropython.org/en/latest/reference/packages.html) is a fabulous tool to do this.

Obviously, you'll need a DHT22 temperature /humidity sensor as well.

To communicate the temperature/humidity sensor readings to Home Assitant, you'll need another ESP32 flashed with [ESPHome](https://esphome.io/). The `esphome_ble_gateway.yml` file in this repository will help you get it configured.

## Configuration
There are a handful of parameters in `main.py` you can use to customize the behavior of the BLESP32 device, starting with DEVICE_NAME and ending with SLEEP_TIME_SECS. The names are pretty self-explanitory and there are comments as well.

## Troubleshooting
Attaching the ESP32 to a host computer over USB will show you debug information in the form of print statements. The LED (if you have one configured) will turn on when the DHT22 sensor is being accessed and turn off after a successful read. If the LED stays on, there's probably something wrong with the wiring of the DHT22.

## Customizing
You're not limited to only reading temperature and humidity. Any kind of sensor you can read with MicroPython should work. The biggest limitation will be the size of the _Manufacturer Data_ field used to broadcast the information. 24 bytes is the maximum amount of data you can send. 
https://stackoverflow.com/questions/33535404/whats-the-maximum-length-of-a-ble-manufacturer-specific-data-ad

Other things to keep in mind are BLE's convention of sending data in little endian format and often with a fixed-point decimal as well. This is really only important if you're using GATT characteristics in addition to the data broadcast in the _Manufacturer Data_ field of the BLE advertisement.

There is no standard for the _Manufacturer Data_ field other than the 16-bit company IDs available for use. Registration is required for these. But, the Company ID of 0xFFFF used in `main.py` is reserved for testing and should be safe to use in a small home environment.
