#!/usr/bin/python3

import time
from subprocess import call

user_string = ''
output_string = ''
pos = 0
sleep = 0.1

while True:
    # Update the user string
    with open('/etc/lcd', 'r') as f:
        new_string = f.read().strip()
        if new_string != user_string:
            pos = 0
        user_string = new_string 

    # Scroll if the string is too long
    if len(user_string) > 14:
        if pos > len(user_string) - (14 - 1):
            pos = 0
        elif pos > len(user_string) - 14:
            sleep = 1
        else: 
            sleep = 0.1

        output_string = user_string[pos:pos+14]
        pos += 1

    else: 
        output_string = user_string
        sleep = 1
        

    # Send the string to the LCD
    hex_string = ' '.join([hex(ord(z)) for z in output_string])
    call('/usr/bin/ipmitool raw 0x6 0x58 0xC2 0 0 0 0 0 0 0 0 0 0 0 0', shell=True)
    call('/usr/bin/ipmitool raw 0x6 0x58 0xC1 0 0 {0} {1}'.format(str(min(len(output_string), 14)), hex_string), shell=True)

    time.sleep(sleep)