#from __future__ import print_function as print
#from __future__ import print_function

import CERWaves
import Codes
import PyCellElimRun as pcer





def test(interpolationModesToTest=["hold","nearest-neighbor","linear","sinusoidal","finite difference cubic hermite","finite difference cubic hermite&clip"]):
  #testSound = CERWaves.sounds["sampleNoise"]
  #testSound = CERWaves.sounds["crickets8bmono44100.wav"][10000:10000+1024]
  testSound = CERWaves.sounds["crickets8bmono44100.wav"][10000:10000+1024*2][::2] #this is necessary because the sample rate of the file was wrong when it was created and samples are duplicated.
  print("the sample rate migh be wrong.")
  testSoundSize = [len(testSound),256]
  assert max(testSound) < testSoundSize[1]
  assert min(testSound) >= 0
  for interpolationMode in interpolationModesToTest:
    print("interpolation mode " + interpolationMode + ": ")
    print("the input data is length " + str(len(testSound)) + " and has a range of " + str((min(testSound),max(testSound))) + " and the start of it looks like " + str(testSound[:16]) + ".")
    pressDataNums = pcer.functionalTest(testSound,"encode",interpolationMode,testSoundSize)
    pressDataFibcodeSeqStr = Codes.intSeqToFibcodeSeqStr(num+1 for num in pressDataNums)
    print("the length of the fibcoded data is " + str(len(pressDataFibcodeSeqStr)) + ".")
    reconstPressDataNums = [num-1 for num in Codes.fibcodeSeqStrToIntArr(pressDataFibcodeSeqStr)]
    reconstPlainDataNums = pcer.functionalTest(reconstPressDataNums,"decode",interpolationMode,testSoundSize)
    if reconstPlainDataNums == testSound:
      print("test passed.")
    else:
      print("test failed.")


def compressFull(soundName,destFileName,interpolationMode,blockWidth):
  sound = CERWaves.sounds[soundName]
  destFile = open(destFileName+" "+interpolationMode+" "+str(blockWidth),"w")
  offset = 0
  print("starting compression on sound of length " + str(len(sound)) + "...")
  print("the input data is length " + str(len(sound)) + " and has a range of " + str((min(sound),max(sound))) + " and the start of it looks like " + str(sound[:16]) + ".")
  while offset + blockWidth + 1 < len(sound):
    print(str(100*offset/len(sound))[:5]+"%...")
    audioData = sound[offset:offset+blockWidth]
    offset += blockWidth
    pressDataNums = pcer.functionalTest(audioData,"encode",interpolationMode,[None,256])
    pressDataBitStr = Codes.intSeqToFibcodeSeqStr([item+1 for item in pressDataNums]) + "\n"
    destFile.write(pressDataBitStr)
  destFile.close()
