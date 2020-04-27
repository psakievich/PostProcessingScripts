"""
========================================
BEGIN USER INPUT
========================================
"""
readFile=True
fileName = "/gscratch/ahsieh/Long_Turbine2/out/Mid_2turbineJ" """.e.768.000"""
outputBaseName = "/nscratch/psakiev/plane2"
sampleBounds = [1430.7080, 1430.7080, 1445, 1555, 0.0, 100]
sampleDimensions = [1,177,361]
resampleFullTimeSeries = True
timeIndexToOutput = [0]

"""
========================================
END USER INPUT
========================================
"""

from paraview.simple import *

if readFile:
    dataSet = OpenDataFile(fileName)
    mergedBlocks = MergeBlocks(dataSet)
else:
    dataSet = GetActiveSource()
    if isinstance(dataSet, ExodusIIReader):
        mergedBlocks = MergeBlocks(dataSet)
    else:
        mergedBlocks = dataSet

plane = ResampleToImage(Input=mergedBlocks)
plane.UseInputBounds=False
plane.SamplingBounds = sampleBounds
plane.SamplingDimensions = sampleDimensions

timeKeeper = GetTimeKeeper()
animationScene = GetAnimationScene()

HideAll()
Show(plane)
Render()

view = GetActiveView()
fileNameTemplate = outputBaseName + "_{timeStep}.pvti"

if resampleFullTimeSeries:
    timeList = [ t for t in dataSet.TimestepValues]
    for time in dataSet.TimestepValues:
        timeKeeper.Time=time
        animationScene.AnimationTime=time
        Render()
        writer = XMLPImageDataWriter(Input=plane)
        writer.FileName = fileNameTemplate.format(
                timeStep=timeList.index(time))
        writer.UpdatePipeline()

elif timeIndexToOutput != []:
    for index in timeIndexToOutput:
        time = dataSet.TimestepValues[index]
        timeKeeper.Time=time
        animationScene.AnimationTime=time
        Render()
        writer = XMLPImageDataWriter(Input=plane)
        writer.FileName = fileNameTemplate.format(
                timeStep=index)
        writer.UpdatePipeline()
else:
    writer = XMLPImageDataWriter(Input=plane)
    writer.FileName = fileNameTemplate.format(timeStep=0)
    writer.UpdatePipeline()

