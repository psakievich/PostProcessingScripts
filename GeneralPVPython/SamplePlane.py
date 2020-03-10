"""
========================================
BEGIN USER INPUT
========================================
"""
readFile=True
fileName = "/Users/psakiev/Desktop/test.e"
outputBaseName = "/Users/psakiev/Desktop/outDumm"
sampleBounds = [0.0, 0.0, -5.0, 5.0, 0.0, 10.0]
sampleDimensions = [1,10,10]
resampleFullTimeSeries = False
timeIndexToOutput = []

"""
========================================
END USER INPUT
========================================
"""

from paraview.simple import *

if readFile:
    dataSet = OpenDataFile(fileName)
else:
    dataSet = GetActiveSource()

plane = ResampleToImage(Input=dataSet)
plane.UseInputBounds=False
plane.SamplingBounds = sampleBounds
plane.SamplingDimensions = sampleDimensions

HideAll()
Show(plane)

view = GetActiveView()
fileNameTemplate = outputBaseName + "_{timeStep}.pvti"
writer = XMLPImageDataWriter(Input=plane)

if resampleFullTimeSeries:
    for time in dataSet.TimestepValues:
        view.ViewTime=time
        writer.FileName = fileNameTemplate.format(
                timeStep=dataSet.TimestepValues.index(time))
        writer.UpdatePipeline()

elif timeIndexToOutput != []:
    for index in timeIndexToOutput:
        view.ViewTime = dataSet.TimestepValues[index]
        writer.FileName = fileNameTemplate.format(
                timeStep=index)
        writer.UpdatePipeline()
else:
    writer.FileName = fileNameTemplate.format(timeStep=0)
    writer.UpdatePipeline()

