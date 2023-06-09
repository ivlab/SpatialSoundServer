#!/usr/bin/python3

import os
import time


# EXAMPLE 1: TESTING THE SIMPLE API
print("\n\nExample 1")

# start a background sound on loop
os.system("curl -G -d snd=testloop.wav localhost:8000/loop")
time.sleep(2)

# play a few short sounds
os.system("curl -G -d snd=beep-01.wav localhost:8000/play")
time.sleep(1)
os.system("curl -G -d snd=beep-02.wav localhost:8000/play")
time.sleep(1)
os.system("curl -G -d snd=beep-03.wav localhost:8000/play")
time.sleep(1)
os.system("curl -G -d snd=beep-04.wav localhost:8000/play")
time.sleep(1)
os.system("curl -G -d snd=click-01.wav localhost:8000/play")
time.sleep(1)
os.system("curl -G -d snd=click-02.wav localhost:8000/play")
time.sleep(1)

# wait a bit more, then stop the background loop
time.sleep(2)
os.system("curl -G -d snd=testloop.wav localhost:8000/stop")



# EXAMPLE 2: USE THE SPATIAL API WITH A MOVING LISTENER AND STATIONARY SOURCE
print("\n\nExample 2")

# move listener to -10,0,0
os.system("curl -G -d x=-10 -d y=0 -d z=0 localhost:8000/listener_param")

# create a repeating beep at (0,0,0)
os.system("curl -G -d id=11 -d snd=beep-01.wav -d looping=1 -d x=0 localhost:8000/create_source")

# move listener from (-10,0,0) to (10,0,0)
for x in range(-10, 10):
    os.system("curl -G -d x=" + str(x) + " localhost:8000/listener_param")
    time.sleep(0.1)

# stop the source
os.system("curl -G -d id=11 localhost:8000/stop_source")
# deleting the source (will also stop it, so prev command is not technically necessary here)
os.system("curl -G -d id=11 localhost:8000/del_source")



# EXAMPLE 3: USE THE SPATIAL API WITH A MOVING SOURCE, SET VELOCITY TO GET DOPPLER EFFECT
print("\n\nExample 3")

# move listener to 0,0,0
os.system("curl -G -d x=0 -d y=0 -d z=0 localhost:8000/listener_param")

# create a repeating beep that moves from left to right with a velocity of 1 unit for every 0.1 seconds
speed = 1.0 / 0.1
os.system("curl -G -d id=10 -d snd=beep-01.wav -d looping=1 -d x=-10 -d vx=" + str(speed) + " localhost:8000/create_source")

# move it from left to right 
for x in range(-10, 10):
    os.system("curl -G -d id=10 -d x=" + str(x) + " localhost:8000/source_param")
    time.sleep(0.1)

# stop the source
os.system("curl -G -d id=10 localhost:8000/stop_source")
# delete the source (will also stop it, so prev command is not technically necessary here)
os.system("curl -G -d id=10 localhost:8000/del_source")



# EXAMPLE 4: CHANGE SOURCE PARAMETERS, LIKE PITCH
print("\n\nExample 4")

# create a repeating beep
os.system("curl -G -d id=12 -d snd=beep-01.wav -d looping=1 localhost:8000/create_source")

# change pitch
p = 0.5
for i in range(0, 10):
    p = p + 0.1
    os.system("curl -G -d id=12 -d pitch=" + str(p) + " localhost:8000/source_param")
    time.sleep(0.1)

# stop the source
os.system("curl -G -d id=12 localhost:8000/stop_source")
# delete the source (will also stop it, so prev command is not technically necessary here)
os.system("curl -G -d id=12 localhost:8000/del_source")




# DONE

# reset: clear openal sources and buffers
os.system("curl -G localhost:8000/reset")
