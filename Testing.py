"""

Testing.py by John Dorsey.

Testing.py contains tools for testing compression of audio with PyCellElimRun.py's tools.
No other files require Testing.py

"""


import CERWaves
import Codes
import CodecTools
import PyCellElimRun as pcer
import IntArrMath

import QuickTimers


SAMPLE_VALUE_UPPER_BOUND = 256 #exclusive.

PEEK = 64 #these control how much information is shown in previews in the console.
PEEEK = 2048





def test(interpolationModesToTest=["hold", "nearest_neighbor", "linear", "linear&round", "sinusoidal", "finite_difference_cubic_hermite", "finite_difference_cubic_hermite&global_clip", "finite_difference_cubic_hermite&span_clip"], numberSeqCodec=Codes.codecs["inSeq_fibonacci"], soundSrcStr="CERWaves.sounds[\"samples/moo8bmono44100.txt\"][15000:]", soundLength=1024):
  #This method tests that the round trip from raw audio to coded (using a universal code) data and back does not change the data.
  
  print("Testing.test: make sure that the sample rate is correct.") #this is necessary because the sample rate of some files, like the moo file, might have been wrong at the time of their creation. moo8bmono44100.wav once had every sample appear twice in a row.
  VERBOSE = True

  QuickTimers.startTimer("test")
  testSound = eval(soundSrcStr)[:soundLength]
  print("Testing.test: the sound source string is " + str(soundSrcStr) + ".")
  testSoundSize = [None,SAMPLE_VALUE_UPPER_BOUND] #leaving the length in samples equal to None allows the codec to decide this for itself. @ This could go wrong if the codec is provided incomplete data that would otherwise lead to proper decompression.
  assert max(testSound) < testSoundSize[1]
  assert min(testSound) >= 0

  print("Testing.test: the input data is length " + str(len(testSound)) + " and has a value range of " + str((min(testSound),max(testSound))) + ((" and is equal to " + str(testSound)) if VERBOSE else (" and the start of it looks like " + str(testSound[:PEEK])[:PEEK])) + ".")

  for interpolationMode in interpolationModesToTest: #test all specified interpolation modes.
    print("\nTesting.test: interpolation mode " + interpolationMode + ": ")
    testCERCodec = pcer.cellElimRunBlockCodec.clone(extraArgs=[interpolationMode,testSoundSize])

    pressDataNums = testCERCodec.encode(testSound)
    print("Testing.test: The sum of the pressDataNums from the Cell Elimination Run codec is " + str(sum(pressDataNums)) + ". They include " + str(pressDataNums.count(0)) + " zeroes, of which " + str(CodecTools.countTrailingZeroes(pressDataNums)) + " are trailing. The median of the nonzero numbers is " + str(IntArrMath.median([item for item in pressDataNums if item != 0])) + " and the maximum is " + str(max(pressDataNums)) + " at index " + str(pressDataNums.index(max(pressDataNums))) + ". The start of the numbers looks like " + str(pressDataNums[:PEEK])[:PEEK] + ".")
    if VERBOSE:
      print("Testing.test: The pressDataNums are " + str(pressDataNums))
    pressDataCodeBitArr = [item for item in numberSeqCodec.encode(num+(0 if numberSeqCodec.zeroSafe else 1) for num in pressDataNums)]
    print("Testing.test: the length of the coded data is " + str(len(pressDataCodeBitArr)) + " and it begins with " + str(CodecTools.bitSeqToStrCodec.encode(pressDataCodeBitArr[:PEEK*2]))[:PEEK*2] + ".")

    CodecTools.printComparison(testSound,pressDataCodeBitArr)

    reconstPressDataNums = [num-(0 if numberSeqCodec.zeroSafe else 1) for num in numberSeqCodec.decode(pressDataCodeBitArr)]
    reconstPlainDataNums = testCERCodec.decode(reconstPressDataNums)
    if reconstPlainDataNums == testSound:
      print("Testing.test: test passed.\n")
      for i in range(len(testSound)):
        assert testSound[i] == reconstPlainDataNums[i]
    else:
      print("Testing.test: test failed. ~~~~~ FAIL ~~~~~ FAIL ~~~~~ FAIL ~~~~~ FAIL ~~~~~ FAIL ~~~~.\n")

  print("Testing.test: testing took " + str(QuickTimers.stopTimer("test")) + " seconds.")



def compressFull(soundName,destFileName,interpolationMode,blockWidth,numberSeqCodec):
  #access the entire sound based on its name, and use the functionalTest method to compress each block of audio, and delimit blocks with newlines in the output file.
  QuickTimers.startTimer("compressFull")
  sound = CERWaves.sounds[soundName]
  destFile = open(destFileName+" "+interpolationMode+" "+str(blockWidth),"w")
  offset = 0
  print("Testing.compressFull: starting compression on sound of length " + str(len(sound)) + "...")
  print("Testing.compressFull: the input data is length " + str(len(sound)) + " and has a range of " + str((min(sound),max(sound))) + " and the start of it looks like " + str(sound[:PEEEK])[:PEEEK] + ".")
  while offset + blockWidth + 1 < len(sound):
    print(str((100.0*offset)/float(len(sound)))[:6]+"%...")
    audioData = sound[offset:offset+blockWidth]
    offset += blockWidth
    pressDataNums = pcer.cellElimRunBlockTranscode(audioData,"encode",interpolationMode,[None,SAMPLE_VALUE_UPPER_BOUND])
    print("Testing.compressFull: there are " + str(len(pressDataNums)) + " pressDataNums to store.")
    pressDataBitStr = CodecTools.bitSeqToStrCodec.encode(numberSeqCodec.encode([item+(0 if numberSeqCodec.zeroSafe else 1) for item in pressDataNums])) + "\n"
    print("Testing.compressFull: the resulting pressDataBitStr has length " + str(len(pressDataBitStr)) + ".")
    destFile.write(pressDataBitStr)
  destFile.close()
  print("Testing.compressFull: compression took " + str(QuickTimers.stopTimer("compressFull")) + " seconds.")


def decompressFull(srcFileName,interpolationMode,blockWidth,numberSeqCodec):
  #inverse of compressFull.
  QuickTimers.startTimer("decompressFull")
  print("Testing.decompressFull: remember that this method returns a huge array which must be stored to a variable, not displayed. It will fill the console output history if shown on screen.")
  #sound = CERWaves.sounds[soundName]
  result = []
  srcFile = open(srcFileName,"r")
  offset = 0
  print("Testing.decompressFull: starting decompression on file named " + str(srcFileName) + "...")
  #print("the input data is length " + str(len(sound)) + " and has a range of " + str((min(sound),max(sound))) + " and the start of it looks like " + str(sound[:512]) + ".")
  while True:
    #print(str(100*offset/len(sound))[:5]+"%...")
    loadedLine = None
    try:
      loadedLine = srcFile.readlines(1)[0].replace("\n","")
    except:
      break
    print("Testing.decompressFull: loaded a line of length " + str(len(loadedLine)) + " which starts with " + loadedLine[:PEEK] + ".")
    pressDataBitArr = CodecTools.bitSeqToStrCodec.decode(loadedLine)
    pressDataNums = [item-(0 if numberSeqCodec.zeroSafe else 1) for item in numberSeqCodec.decode(pressDataBitArr)]
    assert min(pressDataNums) == 0
    if not len(pressDataNums) == blockWidth: #this happens when the provided UniversalCoding numberCoding incorrectly yields an extra zero when its input data is ending. It is less likely to happen now that the UniversalCoding class is no longer used.
      print("Testing.decompressFull: pressDataNums is the wrong length. Trimming will be attempted.") 
      pressDataNums = pressDataNums[:blockWidth]
    plainDataNums = pcer.cellElimRunBlockTranscode(pressDataNums,"decode",interpolationMode,[blockWidth,SAMPLE_VALUE_UPPER_BOUND])
    if not len(plainDataNums) == blockWidth:
      print("Testing.decompressFull: plainDataNums is the wrong length. Trimming will be attempted. This has never happened before.")
      plainDataNums = plainDataNums[:blockWidth]
    print("Testing.decompressFull: extending results by " + str(len(plainDataNums)) + " item array which starts with " + str(plainDataNums[:PEEK])[:PEEK] + ".")
    result.extend(plainDataNums)
  srcFile.close()
  print("Testing.decompressFull: result has length " + str(len(result)) + " and ends with " + str(result[-PEEK:])[-PEEK:] + ".")
  print("Testing.decompressFull: decompression took " + str(QuickTimers.stopTimer("decompressFull")) + " seconds.")
  return result


#tests performed on load.
assert len(CERWaves.sounds["samples/moo8bmono44100.txt"]) > 0

#old non-codec-tools-based test.
assert pcer.cellElimRunBlockTranscode([item-1 for item in Codes.fibcodeBitSeqToIntSeq(Codes.intSeqToFibcodeBitSeq([item+1 for item in pcer.cellElimRunBlockTranscode(CERWaves.sounds["samples/moo8bmono44100.txt"][:256],"encode","linear",[256,SAMPLE_VALUE_UPPER_BOUND])]))],"decode","linear",[256,SAMPLE_VALUE_UPPER_BOUND]) == CERWaves.sounds["samples/moo8bmono44100.txt"][:256]

