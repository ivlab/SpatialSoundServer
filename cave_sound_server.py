#!/usr/bin/env python3

# import PyOpenAL (will require an OpenAL shared library)
from openal import * 
# for webserver
from flask import Flask, request
# for sleeping during playback
import time
# for catching Ctrl-C to shutdown openal
import signal
# for paths
import os
from os import walk


SOUNDS_PATH = "sounds/"
sound_sources = {}
all_sound_files = []
app = Flask(__name__)


@app.route("/")
def route_home():
    return basic_html()



# ------------------
# Simple API: no spatial audio, just play the sound
@app.route("/play", methods=['GET'])
def route_play():
    snd = request.args.get('snd')
    if snd is not None:
        play_snd(snd)
    else:
        print("Missing snd parameter")
    return basic_html()

@app.route("/stop", methods=['GET'])
def route_stop():
    snd = request.args.get('snd')
    if snd is not None:
        stop_snd(snd)
    else:
        print("Missing snd parameter")
    return basic_html()

@app.route("/stopall", methods=['GET'])
def route_stopall():
    stop_all()
    return basic_html()

# Simple API Routines
def get_or_load_source(snd):
    sfile = os.path.join(SOUNDS_PATH, snd)
    if os.path.isfile(sfile):
        if snd in sound_sources.keys():
            return sound_sources[snd]
        else:
            source = oalOpen(sfile)
            if source is not None:
                sound_sources[snd] = source;
                return sound_sources[snd]
    return None

def play_snd(snd):
    source = get_or_load_source(snd)
    if source is not None:
        print('Playing: ' + snd)
        source.play()
    else:
        print('Cannot play sound: ' + snd)

def stop_snd(snd):
    source = get_or_load_source(snd)
    if source is not None:
        if source.get_state() == AL_PLAYING:
            print('Stopping: ' + snd)
            source.stop()
        else:
            print('Cannot stop sound, it is not playing: ' + snd)
    else:
        print('Cannot stop sound, the file is not available: ' + snd)

def stop_all():
    print('Stopping all sounds')
    for snd in sound_sources:
        if sound_sources[snd].get_state() == AL_PLAYING:
            sound_sources[snd].stop()



# ------------------
# Spatial Audio API:

@app.route("/source", methods=['GET'])
def route_source():
    id = request.args.get('id')
    snd = request.args.get('snd')
    pos = request.args.get('pos')
    vel = request.args.get('vel')
    gain = request.args.get('gain')
    pitch = request.args.get('pitch')
    loop = request.args.get('loop')
    max_dist = request.args.get('max_dist')
    ref_dist = request.args.get('ref_dist')
    rolloff = request.args.get('rolloff')
    min_gain = request.args.get('min_gain')
    max_gain = request.args.get('max_gain')
    cone_inner_angle = request.args.get('cone_inner_angle')
    cone_outer_angle = request.args.get('cone_outer_angle')
    cone_outer_gain = request.args.get('cone_outer_gain')

    return basic_html()

@app.route("/listener", methods=['GET'])
def route_listener():
    pos = request.args.get('pos')
    vel = request.args.get('vel')
    ori = request.args.get('ori') # orientation
    gain = request.args.get('gain')
    return basic_html()


@app.route("/reset", methods=['GET'])
def route_reset():
    return basic_html()







# ------------------

def basic_html():
    return "<p>IV/LAB Cave Spatial Sound Server</p>"

def shutdown(signum, frame):
    print(" * Shutting down sound resources...")
    oalQuit()
    exit()

def main():
    print(" * Starting IV/LAB Cave Spatial Sound Server...")
    signal.signal(signal.SIGINT, shutdown)

    # get paths to all files in the sounds_path directory, including within subdirs of sounds_path
    all_sound_files = [os.path.join(dirpath,f) for (dirpath, dirnames, filenames) in os.walk(SOUNDS_PATH) for f in filenames]

    all_sound_files_bullet_list = "\n".join([ "    '" + s + "'" for s in all_sound_files])
    print(" * Available sound files:")
    print(all_sound_files_bullet_list)

    app.run(host="localhost", port=8000, debug=True)


if __name__ == "__main__":
    main()

