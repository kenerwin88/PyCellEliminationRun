"""

CERWaves.py by John Dorsey.

When loaded, CERWaves.py loads sample audio for easy use in testing the codec. Audio samples included in the project are
in the public domain.

"""

import sys
import wave

# don't use "samples/moo8bmono44100.wav":None "samples/crickets8bmono44100.wav":None,
sounds = {"samples/moo8bmono44100.txt": None}


def loadSound(filename):
    if filename.endswith(".wav"):
        soundFile = wave.open(filename, mode="rb")
        result = None
        if sys.version[0] == "3":
            result = [int(item) for item in soundFile.readframes(2 ** 32)]
        else:
            # result = [int(ord(item)) for item in soundFile.readframes(2**32)]
            # assert False
            print(".wav files won't be loaded in this version of python.")
        soundFile.close()
        return result
    elif filename.endswith(".raw"):
        with open(filename, mode="rb") as soundFile:
            result = [int(item) for item in soundFile.read(2 ** 32)][1:][::2]
        return result
    elif filename.endswith(".txt"):
        return deserializeSound(filename)
    else:
        assert False, "unsupported file type."


def serializeSound(filename, sound):
    assert filename.endswith(".txt")
    with open(filename, "w") as soundFile:
        # soundFile.write("".join(chr(item) for item in sound))
        soundFile.write(str(sound))


def deserializeSound(filename):
    assert filename.endswith(".txt")
    with open(filename, "r") as soundFile:
        # soundFile.write("".join(chr(item) for item in sound))
        result = soundFile.read(2 ** 32)
    return eval(result)


def saveSound(filename, sound):
    assert filename.endswith(".wav")
    soundFile = wave.open(filename, mode="wb")
    soundFile.setnchannels(1)
    soundFile.setsampwidth(1)
    soundFile.setframerate(44100)
    # soundFile.write("".join(chr(item) for item in sound))
    for item in sound:
        assert type(item) == int
        assert item < 256
        assert item >= 0
        # soundFile.write(eval("b'"+chr(item)+"'"))
        soundFile.writeframesraw(bytes([item]))
    soundFile.close()


def validateSound(sound):
    diffs = [0, 0, 0, 0]
    if type(sound) != list:
        return False
    for i in range(len(sound) - 1):
        diffs[i % len(diffs)] += sound[i] != sound[i + 1]
    # print("diff sets are " + str(diffs) + ". these numbers should all be similar.")
    if 0 in diffs:
        return False
    ratios = [float(diffs[i]) / float(diffs[ii]) for i in range(len(diffs)) for ii in range(i)]
    return min(ratios) >= 0.8


def loadSounds():
    for key in sounds.keys():
        sounds[key] = loadSound(key)

    sounds["sampleNoise"] = [
        128,
        128,
        127,
        126,
        124,
        113,
        112,
        89,
        32,
        16,
        17,
        14,
        0,
        1,
        9,
        8,
        77,
        78,
        97,
        201,
        210,
        203,
        185,
        183,
        144,
        101,
        99,
        96,
        99,
        124,
        129,
        156,
        146,
        149,
        177,
        181,
        185,
        184,
        170,
        160,
        140,
        110,
        50,
        55,
        75,
        125,
        11,
        123,
        245,
        254,
        255,
        255,
        255,
        254,
        251,
        236,
        249,
        237,
        234,
        221,
        201,
        145,
        103,
        96,
        91,
        115,
        119,
        144,
        144,
        145,
        147,
        149,
        155,
        165,
        175,
        185,
        188,
        193,
        250,
        230,
        210,
        205,
        160,
        50,
        40,
        35,
        31,
        31,
        32,
        39,
        47,
        88,
        86,
        82,
        41,
        13,
        9,
        8,
        6,
        5,
        4,
        4,
        3,
        3,
        3,
        4,
        3,
        2,
        0,
        1,
        2,
        4,
        7,
        17,
        45,
        23,
        46,
        36,
        49,
        62,
        61,
        65,
        98,
        127,
        128,
    ]
    sounds["sampleNoise"].extend([128 for _ in range(128 - len(sounds["sampleNoise"]))])
    assert len(sounds["sampleNoise"]) == 128
    for sound in sounds.values():
        if sound is not None:
            assert validateSound(sound)


loadSounds()
