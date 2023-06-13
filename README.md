# IV/LAB Spatial Sound Server

## Installing OpenAL (required)
The server requires OpenAL to be installed on the computer.

Tested on Windows:
* Download and run the Windows installer here: https://openal.org/downloads/

## Installing openal-soft (optional)
If using a special speaker configuration, like in the IV/LAB cave, you need to have the newer openal-soft library installed as well.  Note, this sits alongside the original OpenAL to provide additional functionality.

Tested on Windows:
* Download the latest pre-built binaries for openal-soft from here: https://openal-soft.org/
* Unzip somewhere; follow the hard-to-interpret instructions in the readme to install, specifically:
  - Copy bin/Win64/soft_oal.dll to C:/Windows/system32/OpenAL32.dll (overwriting the current file if there is one)
* Check the OpenAL installation by making sure you can run the openal-info64.exe provided with openal-soft without error.
* Run the alsoft-config/alsoft-config.exe utility that comes with openal-soft to configure openal for headphones or the particular speaker arrangement that you are using.  For the cave:
  - On the Playback tab, for channels, select 7.1 Surround
  - On the Renderer tab, for the 7.1 Surround config file, click Browse, and select the openal-config/hexagon.ambdec file in this repo.
  - Click Apply.

Note, the output labels in hexagon.ambdef do not seem to be totally correct.  This is what we see in practice:
Output 1 = LF
Output 2 = RF
Output 3 = not used
Output 4 = not used
Output 5 = LB
Output 6 = RB
Output 7 = LS
Output 8 = RS


Notes for future refinements:
* The hexagon arrangement ignores the vertical dimension.  The openal-config dir also includes configs for 3D7.1 and cube that, in theory, could work for other arrangements of the speakers; however, we haven't been able to make these work.  When trying to set them, we get the error: ```AL lib: (EE) alcOpenDevice: Unsupported channels: surround3d71```  For now, we'll just proceed with the hexagon arrangement until we have a specific need for sound that varies in the Y dimension.


## Installing Python dependencies PyOpenAL and Flask (required)
The project uses the [PyOpenAL](https://pypi.org/project/PyOpenAL/) python bindings for accessing OpenAL and the Flask library for creating the http server.  Both can be installed using pip:

```
pip3 install PyOpenAL
pip3 install flask
``` 


## Running and Installing the Server
To run in local dir for testing with sounds in the sounds/ directory:
```python3 cave_sound_server.py```

To run in local dir with sounds located in another directory:
```python3 cave_sound_server.py path/to/sounds/dir```

To install: if needed, edit the INSTALL_ROOT var in sound_server.py to point to the correct install root, then run:
```python3 cave_sound_server.py install```

To run once installed:
* go to the install root folder
* double-click cave_sound_server.bat or cave_sound_server.sh

To add more sounds:
test.wav, a few versions of beepXX.wav, and other common small .wav files are fine to 
add directly to the git repo in the sounds/ directory.  The sound server will then automatically install these.

For larger files or collections of app-specific sounds, just manually install them by 
copying the .wav files into the INSTALL_SHARE/sounds directory or a sub-dir there.

## Testing
Check out the test.py script and try making some noise by running
```python3 test.py```

## Using the Simple API
This is for non-spatial sound.  If all you want to do is play or loop a few simple .wav files, you can just use the simplified API with these commands, replacing test.wav and testloop.wav with the files of your choice:

* http://localhost:8000/play?snd=test.wav
* http://localhost:8000/loop?snd=testloop.wav
* http://localhost:8000/stop?snd=test.wav
* http://localhost:8000/stop_all


## Using the Spatial API
This provides an interface to calling OpenAL's API -- you need to look at the OpenAL docs to understand the details, but briefly:  OpenAL models a 3D environment in which there is one listener (you) and any number audio sources.  It is possible to set your own (i.e., the listener's) position, velocity, orientation, and gain.  And, likewise, it is possible to set all these properties and more for audio sources.  It is left up to you how to use this functionality.  Some programs will imagine that the listener stays at the origin and move the sources around the listener as needed.  Others will treat the sources as stationary and move the listener.  Others will move both.  Keep in mind, the server just provides the API for setting these parameters, it's left up to you how you want to model the 3D environment.

### Start a new spatial audio session and/or cleanup when done

http://localhost:8000/reset

Stops any sounds currently playing through either the spatial or simple API and resets the listener to the default values.
- Default listener position is: (0, 0, 0)
- Default listener velocity is: (0, 0, 0)
- Default listener orientation is: front: (0, 0, -1), up: (0, 1, 0)
- Default listener gain is: 1.0
### Update parameters for the listener

http://localhost:8000/listener_param?x=0&y=0&z=0

Possible parameters (all are optional, include as many as you like in a single call):
* x=float -- The listener's x position (default = 0)
* y=float -- The listener's y position (default = 0)
* z=float -- The listener's z position (default = 0)
* vx=float -- The listener's x velocity (default = 0)
* vy=float -- The listener's y velocity (default = 0)
* vz=float -- The listener's z velocity (default = 0)
* frontx=float -- Part of the listener's orientation, the x component of the front direction (default = 0)
* fronty=float -- Part of the listener's orientation, the y component of the front direction (default = 0)
* frontz=float -- Part of the listener's orientation, the z component of the front direction (default = -1)
* upx=float -- Part of the listener's orientation, the x component of the up vector (default = 0)
* upy=float -- Part of the listener's orientation, the y component of the up vector (default = 1)
* upz=float -- Part of the listener's orientation, the z component of the up vector (default = 0)
* gain=float -- The gain factor for the listener, a float value between 0 and 1 (default = 1)

### Create and play a new audio source

http://localhost:8000/create_source?id=1&snd=test.wav

Required parameters:
* id=int -- An integer id number for this source, pick whatever id you like to refer to this source; the value does not matter as long as you are consistent and always refer to this source using the same id number.
* snd=string -- The filename of the .wav file to use for this source.  The corresponding file must exist inside the server's sounds directory, and the filename should include the .wav extension and the relative path into a sub-directory of the sounds directory, if needed.

Optional parameters:
* Any of the parameters listed in the next section, can also be included in the create_source command.

### Update parameters for an existing audio source

http://localhost:8000/source_param?id=1&x=0&y=0&z=0

Required parameters:
* id=int -- The integer id number for this source that you used when creating the source.

Optional parameters:
* x=float -- The source's x position (default = 0)
* y=float -- The source's y position (default = 0)
* z=float -- The source's z position (default = 0)
* vx=float -- The source's x velocity (default = 0)
* vy=float -- The source's y velocity (default = 0)
* vz=float -- The source's z velocity (default = 0)
* frontx=float -- Part of the source's orientation, the x component of the front direction (default = 0)
* fronty=float -- Part of the source's orientation, the y component of the front direction (default = 0)
* frontz=float -- Part of the source's orientation, the z component of the front direction (default = -1)
* upx=float -- Part of the source's orientation, the x component of the up vector (default = 0)
* upy=float -- Part of the source's orientation, the y component of the up vector (default = 1)
* upz=float -- Part of the source's orientation, the z component of the up vector (default = 0)
* dx=float -- The x component of the source's direction vector
* dy=float -- The y component of the source's direction vector
* dz=float -- The z component of the source's direction vector
* gain=float -- The gain factor for the source, a float value between 0 and 1 (default = 1)
* pitch=float -- The source's pitch shift, where 1 (the initial value) equals identity. Each reduction by 50 percent equals a pitch shift of -12 semitones (one octave reduction). Each doubling equals a pitch shift of 12 semitones (one octave increase). 
* looping=bool -- Set to true if the sound should play in a loop (default = false)
* max_dist=float -- TODO
* ref_dist=float -- TODO
* rolloff=float -- TODO
* min_gain=float -- TODO
* max_gain=float -- TODO
* cone_inner_angle=float -- TODO
* cone_outer_angle=float -- TODO
* cone_outer_gain=float -- TODO
* relative=float -- TODO


### Stop/Start/Pause/Rewind an existing audio source

http://localhost:8000/stop_source?id=1
http://localhost:8000/play_source?id=1
http://localhost:8000/pause_source?id=1
http://localhost:8000/rewind_source?id=1

Required parameters:
* id=int -- The integer id number for this source that you used when creating the source.


### Delete an existing audio source

http://localhost:8000/del_source?id=1

Required parameters:
* id=int -- The integer id number for this source that you used when creating the source.


