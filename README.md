# Wavlib
A Python "library" that manipulates wave files in a variety of ways. It was written so I could teach myself how wave files work, and how to write object-oriented stuff in Python! It also exists so I can manipulate wave files in an extremely easy way. Furthermore, it doesn't use *any external libraries!* <sub><sup>(almost)*</sup></sub> All the maths and wave reading/saving is done manually. It doesn't account for metadata right now, so files can't contain any, otherwise it won't work at all! I'll work on it when I can be bothered.

Also bundled is a tool called "Wavelab" which demonstrates the functions of Wavlib. You can add as many sounds as you like, and process them in many different ways, layering and joining sounds, or adding effects! Wavelab, Wavlib. That won't get confusing at all.

<sub>*"plaster" does use the "random" library, but if you remove the command, no external libraries will be used</sub>

## Wozzit doo?
It supports both 8-bit unsigned and 16-bit signed wave files, both mono and stereo. With Wavlib, you can create a "Wave" object, which contains the sample rate, bit depth and number of channels, all in a convenient format. The object is useless unless you open or create a sound, which is detailed later.

The wave data itself is formatted in a way that enables trivial editing of sounds. Numbers are stored as signed values regardless of format, meaning that bytes can be added together easily. For stereo files, bytes are stored as pairs, so each channel can be changed individually.

Because the bytes are plain old arrays, joining sounds couldn't be easier (if they have the same amount of channels!); just concatenate them like any other array. Sounds can also be reversed and trimmed just like normal arrays. If there's a mixture of mono and stereo, use the internal functions instead!

A mixture of 8-bit and 16-bit will work just fine, and although they're converted to 16-bit values in the Wave object, the values are treated as 8-bit when saving.

Sounds can be loaded from a file, and all the relevant information is conveniently read into the Wave object. Alternatively, you can create a new, blank Wave object, for you to change manually.

Like everything I've ever written, execution can be quite slow, so please bear that in mind!

## Howzit used?
### Opening a wave file
```
from wavlib import Wave

wav=Wave()
wav.open("thing.wav")
```

### Creating a blank file
```
from wavlib import Wave

wav=Wave()
wav.new(sample_rate=44100,channels=2,bit_depth=16,length=10000)
```
This creates a 16-bit stereo file at the 44100 Hz, 10000 samples long.

Alternatively, you can use seconds:
```
wav.new(sample_rate=44100,channels=2,bit_depth=16,length=wav.seconds_abs(44100,10))
```
### Joining 2 wave files (with the same amount of channels), and saving the result
```
from wavlib import Wave

wav1=Wave()
wav1.open("thing1.wav")
wav2=Wave()
wav2.open("thing2.wav")
wav1.bytes+=wav2.bytes
wav1.save("thing3.wav")
```
### After opening/creating a file
A Wave object will contain the following properties:
* **bytes** - An array containing the wave bytes (or byte pairs)
* **channels** - Amount of channels in the file (1 for mono, 2 for stereo)
* **bit_depth** - Bit depth of the file (e.g. 8, 16)
* **sample_rate** - Sample rate of the file in Hz
* **length** - Amount of *formatted* bytes in the array
* **data_length** - Amount of *raw* bytes in the file
* **bytes** - Formatted wave bytes (mutable)

## List of functions
### Wave.**open**(*filename*)

Opens a wave file
### Wave.**save**(*filename*)

Saves a wave file
### Wave.**amplify** (*factor*)

Increases/reduces the volume by a certain amount (2 doubles the volume, 0.5 halves it, etc)
### Wave.**paste** (*source,dest_pos*)

Layers or joins the Wave defined in *source* to the targeted Wave at the *dest_pos* (measured in samples).
A number of optional parameters are available:
* **source_range** - Defines the start and length (in samples) for the source wave. If 0 is used for the length, the whole sound is used.
* **rate** - The sample rate of the source wave. By default it uses the native sample rate, but it can be changed, allowing for a sound to play at different speeds.
* **clip** - Defaults to True. If it's False, the volume will be halved for the pasted region, preventing clipping. If it's True, the volume is kept the same, and clipping occurs if things get loud.
* **join** - Defaults to False. If it's True, this appends the sample to the end of the wave, using all the same parameters above (though *clip* is ineffective)

### Wave.**new** (*sample_rate,channels,bit_depth,length*)

Creates a new sound with the specified sample rate, channels, bit depth and length (in samples)

### Wave.**flatten** ()

Used internally when saving, this function "flattens" a Wave object, converting it back to regular bytes. The flattened bytes are returned through this function, and the object itself is unaffected.

### Wave.**flattened_byte** (*byte*)

This function "flattens" a byte in a Wave's native format, and returns a regular byte (or pair of bytes for 16-bit sounds)

### Wave.**seconds_abs** (*sample_rate,seconds*)

Calculates how many samples will cover a certain amount of seconds, based on a sample rate. If a Wave object has been initialized, Wave.**seconds** can be used instead, which uses the sample rate of the Wave object.

### Wave.**seconds** (*seconds*)

Calculates how many samples will cover a certain amount of seconds, based on a Wave's existing sample rate.

### Wave.**get_nearest_zero_pos** (*pos*)

Supplied a position in the Wave, this will return the position representing the nearest zero crossing. This is where the waveform is completely centred, so using this when trimming waves will reduce clicks. If the file is stereo, the average between both channels is used. If the exact zero crossing can't be found, the optional parameter *sensitivity* reduces each byte until a zero crossing is found.

### Wave.**plaster** (*wave,amount,seconds*)

An extremely funny command that "plasters" a Wave (or a list of Waves) across a sound! If you want the sounds to warble in pitch, use the optional *warble* parameter to adjust how much the sample rate deviates. If things start to get loud, use the optional *amplify* parameter to adjust the volume (for example, 2 doubles the volume and 0.5 halves it). If you end up in hysterics, stop the sound immediately, and try to catch your breath.

### Wave.**normalize** ()

Brings a Wave's volume to its loudest without clipping.

### Wave.**resample** (*rate*)

Resamples a Wave, changing the sample rate without affecting pitch.

### Wave.**copy** ()

Returns an identical copy of the targeted Wave.

### Wave.**clear** ()

Silences an entire Wave by zeroing all the bytes.

### Wave.**timestretch** (*block_size,percent*)

A very crude time-stretch function, which changes the speed of a Wave without affecting its pitch. A percentage of 200% will double the speed, and 50% will halve it. A smaller block size will result in a more granular sound.

### Wave.**echo** (*length,decay*)

Repeats a Wave at the desired rate, slowly reducing in volume. The Wave can be extended by setting *extend* to True, allowing for the volume to fully die out. The pitch can also be bent by setting *bend* to a positive or negative value.

### Wave.**fade** (*region*)

Fades a Wave in/out, using the region specified (either a tuple or a list). It fades in from the beginning to the first region point, and out from the second region point to the end.

### Wave.**filter** (*passes*)

Applies a basic low-pass filter to a Wave. More passes will result in a steeper slope.