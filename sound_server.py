
### RUNNING ###
# To run in local dir for testing with sounds in the sounds/ directory:
#   python3 cave_sound_server.py
# To run in local dir with sounds located in another directory:
#   python3 cave_sound_server.py path/to/sounds/dir

# To install:
#   if needed, edit the INSTALL_ROOT below to point to the correct install root, then run:
#   python3 cave_sound_server.py install

# To run once installed:
#   go to the install root folder
#   double-click cave_sound_server.bat or cave_sound_server.sh

# To add more sounds:
#   test.wav, a few versions of beepXX.wav, and other common small .wav files are fine to 
#   add directly to the git repo in the sounds/ directory.  The sound server will then 
#   automatically install these.
#
#   For larger files or collections of app-specific sounds, just manually install them by 
#   copying the .wav files into the INSTALL_SHARE/sounds directory or a sub-dir there.


### CONFIGURATION / LOCAL INSTALLATION ###

# root of install tree
#INSTALL_ROOT = "c:/V"
#INSTALL_ROOT = "/usr/local"
INSTALL_ROOT = "install"

# sound_server run scripts are copied/created here
INSTALL_BIN = INSTALL_ROOT + "/bin"

# this script will be installed here
INSTALL_PY = INSTALL_ROOT + "/lib/python3"

# test.wav and anything else in the 'sounds' subdir of the git repo will be installed here
INSTALL_SHARE = INSTALL_ROOT + "/share"



import os
from os import walk
from openal import * 
from openal.al import *
from openal.alc import *
from flask import Flask, request
import signal
import sys
import shutil
import stat

BUILTIN_SOUNDS_PATH = "sounds"
sounds_path = BUILTIN_SOUNDS_PATH
buffers = {} # openal buffers indexed by snd (sound file name)
simple_sources = {} # openal sources indexed by snd (sound file name)
spatial_sources = {} # openal sources indexed by spatial id

app = Flask(__name__)


@app.route("/")
def route_home():
    return html_blurb()

# Removes all sources and buffers from memory -- good practice to call when done using the server or when
# first beginning to use the server to get a fresh start.
@app.route("/reset", methods=['GET'])
def route_reset():
    reset()
    return html_blurb()

# ------------------
# Flask-Based Simple API: no spatial audio, just play the sound

@app.route("/play", methods=['GET'])
def route_play():
    snd = request.args.get('snd', type=str)
    if snd is not None:
        play_simple(snd)
    else:
        print("Missing snd parameter")
    return html_blurb()

@app.route("/loop", methods=['GET'])
def route_loop():
    snd = request.args.get('snd', type=str)
    if snd is not None:
        play_simple(snd, True)
    else:
        print("Missing snd parameter")
    return html_blurb()

@app.route("/stop", methods=['GET'])
def route_stop():
    snd = request.args.get('snd', type=str)
    if snd is not None:
        stop_simple(snd)
    else:
        print("Missing snd parameter")
    return html_blurb()


@app.route("/stop_all", methods=['GET'])
def route_stop_all():
    stop_all_simple()
    return html_blurb()



# ------------------
# Flask-Based Spatial Audio API:

@app.route("/listener_param", methods=['GET'])
def route_listener_param():
    x = request.args.get('x', type=float)
    if x is not None:
        set_listener_x(x)
    y = request.args.get('y', type=float)
    if y is not None:
        set_listener_y(y)
    z = request.args.get('z', type=float)
    if z is not None:
        set_listener_z(z)

    vx = request.args.get('vx', type=float)
    if vx is not None:
        set_listener_vx(vx)
    vy = request.args.get('vy', type=float)
    if vy is not None:
        set_listener_vy(vy)
    vz = request.args.get('vz', type=float)
    if vz is not None:
        set_listener_vz(vz)

    frontx = request.args.get('frontx', type=float)
    if frontx is not None:
        set_listener_frontx(frontx)
    fronty = request.args.get('fronty', type=float)
    if fronty is not None:
        set_listener_fronty(fronty)
    frontz = request.args.get('frontz', type=float)
    if frontz is not None:
        set_listener_frontz(frontz)
    upx = request.args.get('upx', type=float)
    if upx is not None:
        set_listener_upx(upx)
    upy = request.args.get('upy', type=float)
    if upy is not None:
        set_listener_upy(upy)
    upz = request.args.get('upz', type=float)
    if upz is not None:
        set_listener_upz(upz)

    gain = request.args.get('gain', type=float)
    if gain is not None:
        set_listener_gain(gain)
    return html_blurb()


@app.route("/create_source", methods=['GET'])
def route_create_source():
    id = request.args.get('id', type=int)
    if id is None:
        print("Missing id parameter")
        return html_blurb()

    snd = request.args.get('snd', type=str)
    if snd is None:
        print("Missing snd parameter")
        return html_blurb()
    
    source = create_and_play_spatial(id, snd)
    if source is None:
        print("Cannot create spatial source id='" + str(id) + "' snd='" + str(snd) + "'")

    return route_source_param()


@app.route("/source_param", methods=['GET'])
def route_source_param():
    id = request.args.get('id', type=int)
    if id is None:
        print("Missing id parameter")
        return html_blurb()    
    if not id in spatial_sources.keys():
        print("Cannot locate a source with id='" + str(id) + "'")
        return html_blurb()
    
    x = request.args.get('x', type=float)
    if x is not None:
        set_source_x(id, x)
    y = request.args.get('y', type=float)
    if y is not None:
        set_source_y(id, y)
    z = request.args.get('z', type=float)
    if z is not None:
        set_source_z(id, z)

    vx = request.args.get('vx', type=float)
    if vx is not None:
        set_source_vx(id, vx)
    vy = request.args.get('vy', type=float)
    if vy is not None:
        set_source_vy(id, vy)
    vz = request.args.get('vz', type=float)
    if vz is not None:
        set_source_vz(id, vz)

    dx = request.args.get('dx', type=float)
    if dx is not None:
        set_source_dx(id, dx)
    dy = request.args.get('dy', type=float)
    if dy is not None:
        set_source_dy(id, dy)
    dz = request.args.get('dz', type=float)
    if dz is not None:
        set_source_dz(id, dz)

    gain = request.args.get('gain', type=float)
    if gain is not None:
        set_source_gain(id, gain)

    pitch = request.args.get('pitch', type=float)
    if pitch is not None:
        set_source_pitch(id, pitch)

    looping = request.args.get('looping', type=bool)
    if looping is not None:
        set_source_looping(id, looping)

    max_dist = request.args.get('max_dist', type=float)
    if max_dist is not None:
        set_source_max_dist(id, max_dist)

    ref_dist = request.args.get('ref_dist', type=float)
    if ref_dist is not None:
        set_source_ref_dist(ref_dist)

    rolloff = request.args.get('rolloff', type=float)
    if rolloff is not None:
        set_source_rolloff(id, rolloff)

    min_gain = request.args.get('min_gain', type=float)
    if min_gain is not None:
        set_source_min_gain(id, min_gain)

    max_gain = request.args.get('max_gain', type=float)
    if max_gain is not None:
        set_source_max_gain(id, max_gain)

    cone_inner_angle = request.args.get('cone_inner_angle', type=float)
    if cone_inner_angle is not None:
        set_souurce_cone_inner_angle(id, cone_inner_angle)

    cone_outer_angle = request.args.get('cone_outer_angle', type=float)
    if cone_outer_angle is not None:
        set_source_cone_outer_angle(id, cone_outer_angle)

    cone_outer_gain = request.args.get('cone_outer_gain', type=float)
    if cone_outer_gain is not None:
        set_source_cone_outer_gain(id, cone_outer_gain)

    relative = request.args.get('relative', type=bool)
    if relative is not None:
        set_source_relative(id, relative)

    return html_blurb()


@app.route("/play_source", methods=['GET'])
def route_play_source():
    id = request.args.get('id', type=int)
    if id is None:
        print("Missing id parameter")
        return html_blurb()
    if not id in spatial_sources.keys():
        print("Cannot locate a source with id='" + str(id) + "'")
        return html_blurb()

    spatial_sources[id].play()
    return html_blurb()


@app.route("/stop_source", methods=['GET'])
def route_stop_source():
    id = request.args.get('id', type=int)
    if id is None:
        print("Missing id parameter")
        return html_blurb()
    if not id in spatial_sources.keys():
        print("Cannot locate a source with id='" + str(id) + "'")
        return html_blurb()

    spatial_sources[id].play()
    return html_blurb()

@app.route("/del_source", methods=['GET'])
def route_del_source():
    id = request.args.get('id', type=int)
    if id is None:
        print("Missing id parameter")
        return html_blurb()
    if not id in spatial_sources.keys():
        print("Cannot locate a source with id='" + str(id) + "'")
        return html_blurb()

    spatial_sources[id].stop()
    del spatial_sources[id]
    return html_blurb()



# Simple API Support Routines
def play_simple(snd: str, looping: bool=False):
    buffer = get_or_load_buffer(snd)
    if buffer is not None:
        source = Source(buffer, True)
        if source is not None:
            source.set_looping(looping)
            simple_sources[snd] = source
            source.play()
            return True
    return False

def stop_simple(snd: str):
    if snd in simple_sources.keys():
        simple_sources[snd].stop()
        return True
    return False

def stop_all_sounds():
    if simple_sources:
        for snd in simple_sources.keys():
            simple_sources[snd].stop()
    if spatial_sources:
        for id in spatial_sources.keys():
            spatial_sources[id].stop()


# Spatial API Support Routines
def create_and_play_spatial(id: int, snd: str):
    buffer = get_or_load_buffer(snd)
    if buffer is not None:
        source = Source(buffer, True)
        if source is not None:
            spatial_sources[id] = source
            source.play()
            return True
    return False

def stop_spatial(id: int):
    if id in spatial_sources.keys():
        spatial_sources[id].stop()
        return True
    return False

def set_listener_x(x: float):
    tmp,y,z = oalGetListener().position
    oalGetListener().set_position((x,y,z))

def set_listener_y(y: float):
    x,tmp,z = oalGetListener().position
    oalGetListener().set_position((x,y,z))

def set_listener_z(z: float):
    x,y,tmp = oalGetListener().position
    oalGetListener().set_position((x,y,z))

def set_listener_vx(vx: float):
    tmp,vy,vz = oalGetListener().velocity
    oalGetListener().set_velocity((vx,vy,vz))

def set_listener_vy(vy: float):
    vx,tmp,vz = oalGetListener().velocity
    oalGetListener().set_velocity((vx,vy,vz))

def set_listener_vz(vz: float):
    vx,vy,tmp = oalGetListener().velocity
    oalGetListener().set_velocity((vx,vy,vz))

def set_listener_frontx(frontx: float):
    tmp,fronty,frontz,upx,upy,upz = oalGetListener().orientation
    oalGetListener().set_orientation((frontx,fronty,frontz,upx,upy,upz))

def set_listener_fronty(fronty: float):
    frontx,tmp,frontz,upx,upy,upz = oalGetListener().orientation
    oalGetListener().set_orientation((frontx,fronty,frontz,upx,upy,upz))

def set_listener_frontz(frontz: float):
    frontx,fronty,tmp,upx,upy,upz = oalGetListener().orientation
    oalGetListener().set_orientation((frontx,fronty,frontz,upx,upy,upz))

def set_listener_upx(upx: float):
    frontx,fronty,frontz,tmp,upy,upz = oalGetListener().orientation
    oalGetListener().set_orientation((frontx,fronty,frontz,upx,upy,upz))

def set_listener_upy(upy: float):
    frontx,fronty,frontz,upx,tmp,upz = oalGetListener().orientation
    oalGetListener().set_orientation((frontx,fronty,frontz,upx,upy,upz))

def set_listener_upz(upz: float):
    frontx,fronty,frontz,upx,upy,tmp = oalGetListener().orientation
    oalGetListener().set_orientation((frontx,fronty,frontz,upx,upy,upz))

def set_listener_gain(gain: float):
    oalGetListener().set_gain(gain)


def set_source_x(id: int, x: float):
    source = spatial_sources[id]
    tmp,y,z = source.position
    source.set_position((x,y,z))

def set_source_y(id: int, y: float):
    source = spatial_sources[id]
    x,tmp,z = source.position
    source.set_position((x,y,z))

def set_source_z(id: int, z: float):
    source = spatial_sources[id]
    x,y,tmp = source.position
    source.set_position((x,y,z))

def set_source_vx(id: int, vx: float):
    source = spatial_sources[id]
    tmp,vy,vz = source.velocity
    source.set_velocity((vx,vy,vz))

def set_source_vy(id: int, vy: float):
    source = spatial_sources[id]
    vx,tmp,vz = source.velocity
    source.set_velocity((vx,vy,vz))

def set_source_vz(id: int, vz: float):
    source = spatial_sources[id]
    vx,vy,tmp = source.velocity
    source.set_velocity((vx,vy,vz))

def set_source_dx(id: int, dx: float):
    source = spatial_sources[id]
    tmp,dy,dz = source.direction
    dir[0] = dx
    source.set_direction((dx,dy,dz))

def set_source_dy(id: int, dy: float):
    source = spatial_sources[id]
    dx,tmp,dz = source.direction
    source.set_direction((dx,dy,dz))

def set_source_dz(id: int, dz: float):
    source = spatial_sources[id]
    dx,dy,tmp = source.direction
    source.set_direction((dx,dy,dz))

def set_source_looping(id: int, looping: bool):
    source = spatial_sources[id]
    source.set_looping(looping)

def set_source_relative(id: int, relative: bool):
    source = spatial_sources[id]
    source.set_source_relative(relative)

def set_source_gain(id: int, gain: float):
    source = spatial_sources[id]
    source.set_gain(gain)

def set_source_pitch(id: int, pitch: float):
    source = spatial_sources[id]
    source.set_pitch(pitch)

def set_source_max_dist(id: int, max_dist: float):
    source = spatial_sources[id]
    source.set_max_distance(max_dist)

def set_source_rolloff(id: int, rolloff: float):
    source = spatial_sources[id]
    source.set_rolloff_factor(rolloff)

def set_source_ref_dist(id: int, ref_dist: float):
    source = spatial_sources[id]
    source.set_reference_distance(ref_dist)

def set_source_min_gain(id: int, gain: float):
    source = spatial_sources[id]
    source.set_min_gain(gain)

def set_source_max_gain(id: int, gain: float):
    source = spatial_sources[id]
    source.set_max_gain(gain)

def set_source_cone_outer_gain(id: int, gain: float):
    source = spatial_sources[id]
    source.set_cone_outer_gain(gain)

def set_source_cone_inner_angle(id: int, angle: float):
    source = spatial_sources[id]
    source.set_cone_inner_angle(angle)

def set_source_cone_outer_angle(id: int, angle: float):
    source = spatial_sources[id]
    source.set_cone_outer_angle(angle)

def reset():
    # stop and delete all sound sources
    for snd in simple_sources.keys():
        simple_sources[snd].stop()
    simple_sources.clear()
    for id in spatial_sources.keys():
        spatial_sources[id].stop()
    spatial_sources.clear()
    buffers.clear()

    # reset the listener state to default values
    set_listener_x(0)
    set_listener_y(0)
    set_listener_z(0)
    set_listener_vx(0)
    set_listener_vy(0)
    set_listener_vz(0)
    set_listener_frontx(0)
    set_listener_fronty(0)
    set_listener_frontz(-1)
    set_listener_upx(0)
    set_listener_upy(1)
    set_listener_upz(0)
    set_listener_gain(1)





# ------------------

def html_blurb(info_message: str=None):
    html = ""
    if status_message is not None:
        html += "<p>INFO: " + status_message + "</p>"
    html += "<h1>IV/LAB Cave Spatial Sound Server</h1>" 
    # TODO: return some info on usage
    return html


def shutdown(signum, frame):
    print(" * Shutting down sound resources...")
    oalQuit()
    exit()

# snd is the filename including the relative path from the sounds_dir to the wav file 
def get_or_load_buffer(snd: str):
    full_filename = os.path.join(sounds_path, snd)
    if os.path.isfile(full_filename):
        if snd in buffers.keys():
            return buffers[snd]
        else:
            wavefile = WaveFile(full_filename)
            if wavefile is not None:
                buffer = Buffer(wavefile)
                if buffer is not None:
                    buffers[snd] = buffer        
                    return buffer
    return None


def main():
    sounds_path = BUILTIN_SOUNDS_PATH
    if len(sys.argv) >= 2:
        if sys.argv[1] == "install":
            install()
            return
        else:
            sounds_path = sys.argv[1]

    print(" * Starting IV/LAB Cave Spatial Sound Server...")
    signal.signal(signal.SIGINT, shutdown)

    # get paths to all files in the sounds_path directory, including within subdirs of sounds_path
    all_sound_files = [os.path.join(dirpath,f) for (dirpath, dirnames, filenames) in os.walk(sounds_path) for f in filenames]

    all_sound_files_bullet_list = "\n".join([ "    '" + s + "'" for s in all_sound_files])
    print(" * Available sound files in '" + sounds_path + "'")
    print(all_sound_files_bullet_list)

    app.run(host="localhost", port=8000, debug=True)


def install():
    # install python source
    os.makedirs(INSTALL_PY, exist_ok=True)
    shutil.copyfile(__file__, os.path.join(INSTALL_PY, __file__))

    # install sounds dir
    os.makedirs(INSTALL_SHARE, exist_ok=True)
    shutil.copytree(BUILTIN_SOUNDS_PATH, os.path.join(INSTALL_SHARE, BUILTIN_SOUNDS_PATH), dirs_exist_ok=True)

    # generate run script(s)
    os.makedirs(INSTALL_BIN, exist_ok=True)
    if sys.platform == 'win32':
        # create a bat file
        cmd = "@echo off\n" + sys.executable + " " + os.path.abspath(os.path.join(INSTALL_PY, __file__)) + " " + os.path.abspath(os.path.join(INSTALL_SHARE, BUILTIN_SOUNDS_PATH)) + "\npause\n"
        sh_script_name = os.path.join(INSTALL_BIN, "cave_sound_server.bat")
        sh_script = open(sh_script_name, "w")
        sh_script.write(cmd)
        sh_script.close()
        os.chmod(sh_script_name, os.stat(sh_script_name).st_mode | stat.S_IEXEC)
    else:
        # create a shell script
        cmd = "#!/usr/bin/env " + sys.executable + " " + os.path.abspath(os.path.join(INSTALL_PY, __file__)) + " " + os.path.abspath(os.path.join(INSTALL_SHARE, BUILTIN_SOUNDS_PATH)) + "\n"
        sh_script_name = os.path.join(INSTALL_BIN, "cave_sound_server.sh")
        sh_script = open(sh_script_name, "w")
        sh_script.write(cmd)
        sh_script.close()
        os.chmod(sh_script_name, os.stat(sh_script_name).st_mode | stat.S_IEXEC)


if __name__ == "__main__":
    main()
