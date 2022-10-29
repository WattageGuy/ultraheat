# Ultraheat to HTTP request
Script to read information from Landis+Gyr Ultraheat (UH50, T550)

This modified script sends the kWh and m3 values to Home Assistant or any other platform with that can receive webhook. 

## Installation and usage:
This script uses a optical probe (IEC 62056-21) on an USB port to read the telegrams from the meter.

Add a custom sensor with kWh and m3 (Add through input_number sensor Home Assistant) and an automation that changes this value on webhook. Example:
```
alias: Fjärrvärme förbrukning
description: ""
trigger:
  - platform: webhook
    webhook_id: fjarrvarme
condition: []
action:
  - service: input_number.set_value
    data:
      value: "{{ trigger.json.kwh }}"
    target:
      entity_id: input_number.fjarrvarme_forbrukning
mode: single
```

The script will send the values to Home Assistant in kWh and liters (not m3).

## Warning:
It is said that every readout of the Ultraheat is shortening the livespan of the battery by 15 minutes. 
Usually these batteries last for many years, but please make sure you don't read the values too often. 
There is little added value in fetching the data very frequently. I fetch it a few times a day to get
an idea of the heat usage over a few parts of the day (every 6 hours). This might not apply to T550, not tested. 

## Requirements:
- An optical probe (IEC 62056-21 standard) to place on the meter, for example (tested): https://www.aliexpress.com/item/1005004351799379.html?spm=a2g0o.order_list.0.0.78b71802iHMif4
- Python3
- Home Assistant or other

## Source:
Original script from Magnat in https://gathering.tweakers.net/forum/list_messages/1535019 and https://github.com/aiolos/ultraheat
