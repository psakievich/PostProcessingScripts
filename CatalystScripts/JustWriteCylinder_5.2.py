
from paraview.simple import *
from paraview import coprocessing


#--------------------------------------------------------------
# Code generated from cpstate.py to create the CoProcessor.
# paraview version 5.5.2

#--------------------------------------------------------------
# Global screenshot output options
imageFileNamePadding=0
rescale_lookuptable=False


# ----------------------- CoProcessor definition -----------------------

def CreateCoProcessor():
  def _CreatePipeline(coprocessor, datadescription):
    class Pipeline:
      # state file generated using paraview version 5.5.2

      # ----------------------------------------------------------------
      # setup the data processing pipelines
      # ----------------------------------------------------------------

      # trace generated using paraview version 5.5.2

      #### disable automatic camera reset on 'Show'
      paraview.simple._DisableFirstRenderCameraReset()

      # create a new 'ExodusIIReader'
      # create a producer from a simulation input
      exodusIIReader1 = coprocessor.CreateProducer(datadescription, 'Input')

      # create a new 'Programmable Source'
      programmableSource1 = ProgrammableSource()
      programmableSource1.OutputDataSetType = 'vtkStructuredGrid'
      programmableSource1.Script = 'import AdvancedGridGeneration as cg\noutput.ShallowCopy(cg.CreateCylindricalGrid(0.5,1.0,(20, 10, 10)))'
      programmableSource1.ScriptRequestInformation = 'executive = self.GetExecutive()\noutInfo = executive.GetOutputInformation(0)\noutInfo.Set(executive.WHOLE_EXTENT(), 0, 19, 0, 9, 0, 9)'
      programmableSource1.PythonPath = "'/ascldap/users/psakiev/PostProcessingScripts/VTKBased'"

      # create a new 'Resample With Dataset'
      resampleWithDataset1 = ResampleWithDataset(Input=exodusIIReader1,
          Source=programmableSource1)
      resampleWithDataset1.CellLocator = 'Static Cell Locator'

      # create a new 'Parallel Structured Grid Writer'
      parallelStructuredGridWriter1 = servermanager.writers.XMLPStructuredGridWriter(Input=resampleWithDataset1)

      # register the writer with coprocessor
      # and provide it with information such as the filename to use,
      # how frequently to write the data, etc.
      coprocessor.RegisterWriter(parallelStructuredGridWriter1, filename='filename_%t.pvts', freq=1, paddingamount=0)

      # ----------------------------------------------------------------
      # finally, restore active source
      SetActiveSource(parallelStructuredGridWriter1)
      # ----------------------------------------------------------------
    return Pipeline()

  class CoProcessor(coprocessing.CoProcessor):
    def CreatePipeline(self, datadescription):
      self.Pipeline = _CreatePipeline(self, datadescription)

  coprocessor = CoProcessor()
  # these are the frequencies at which the coprocessor updates.
  freqs = {'Input': [1]}
  coprocessor.SetUpdateFrequencies(freqs)
  return coprocessor


#--------------------------------------------------------------
# Global variable that will hold the pipeline for each timestep
# Creating the CoProcessor object, doesn't actually create the ParaView pipeline.
# It will be automatically setup when coprocessor.UpdateProducers() is called the
# first time.
coprocessor = CreateCoProcessor()

#--------------------------------------------------------------
# Enable Live-Visualizaton with ParaView and the update frequency
coprocessor.EnableLiveVisualization(False, 1)

# ---------------------- Data Selection method ----------------------

def RequestDataDescription(datadescription):
    "Callback to populate the request for current timestep"
    global coprocessor
    if datadescription.GetForceOutput() == True:
        # We are just going to request all fields and meshes from the simulation
        # code/adaptor.
        for i in range(datadescription.GetNumberOfInputDescriptions()):
            datadescription.GetInputDescription(i).AllFieldsOn()
            datadescription.GetInputDescription(i).GenerateMeshOn()
        return

    # setup requests for all inputs based on the requirements of the
    # pipeline.
    coprocessor.LoadRequestedData(datadescription)

# ------------------------ Processing method ------------------------

def DoCoProcessing(datadescription):
    "Callback to do co-processing for current timestep"
    global coprocessor

    # Update the coprocessor by providing it the newly generated simulation data.
    # If the pipeline hasn't been setup yet, this will setup the pipeline.
    coprocessor.UpdateProducers(datadescription)

    # Write output data, if appropriate.
    coprocessor.WriteData(datadescription);

    # Write image capture (Last arg: rescale lookup table), if appropriate.
    coprocessor.WriteImages(datadescription, rescale_lookuptable=rescale_lookuptable,
        image_quality=0, padding_amount=imageFileNamePadding)

    # Live Visualization, if enabled.
    coprocessor.DoLiveVisualization(datadescription, "localhost", 22222)
