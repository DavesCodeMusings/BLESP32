# BLESP32
BLESP32 is a portmanteau of Bluetooth Low Energy (BLE) and ESP32, the venerable Espressif microcontroller. What you'll find here is a MicroPython program that runs on ESP32 to collect data from the popular DHT22 temperature and humidity sensor, sending it out not only as traditional GATT characteristics, but also in BLE advertising packets that can be captured in ESPHome's Bluetooth Tracker for relaying to Home Assistant.

## Why?
I wanted a device that could communicate periodic sensor data while spending most of its time in deep sleep. I wanted this data relayed to Home Assistant, my home automation hub. GATT characteristics are the traditional way to make information available from BLE devices. But, it requires a connection. So the device has to be up and responding. Having a device that periodically goes into deep sleep does not fit well with connection oriented protocols. An alternative to GATT characteristics is required.

## How?
The solution adopted by many device manufacturers is to leverage data fields in the BLE advertisement to broadcast sensor information. I'm doing the same thing here. Using the Manufacturer data field, I'm encoding the temperature and humidity readings from the DHT22 sensor into the BLE advertisement. ESPHome is able to receive this advertisement and decode the data with a lambda function. From there it's sent to Home Assistant.

## Show Me the Code!

