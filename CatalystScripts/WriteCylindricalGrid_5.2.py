
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
      # setup views used in the visualization
      # ----------------------------------------------------------------

      # trace generated using paraview version 5.5.2

      #### disable automatic camera reset on 'Show'
      paraview.simple._DisableFirstRenderCameraReset()

      # get the material library
      materialLibrary1 = GetMaterialLibrary()

      # Create a new 'Render View'
      renderView1 = CreateView('RenderView')
      renderView1.ViewSize = [574, 555]
      renderView1.AnnotationColor = [0.0, 0.0, 0.0]
      renderView1.AxesGrid = 'GridAxes3DActor'
      renderView1.OrientationAxesLabelColor = [0.0, 0.0, 0.0]
      renderView1.StereoType = 0
      renderView1.CameraPosition = [1.0182114352829337, -6.509079319752067, 1.1624250006926302]
      renderView1.CameraViewUp = [-0.058870567807537244, 0.1665671324677498, 0.9842711245523204]
      renderView1.Background = [1.0, 1.0, 1.0]
      renderView1.OSPRayMaterialLibrary = materialLibrary1

      # init the 'GridAxes3DActor' selected for 'AxesGrid'
      renderView1.AxesGrid.XTitleColor = [0.0, 0.0, 0.0]
      renderView1.AxesGrid.XTitleFontFile = ''
      renderView1.AxesGrid.YTitleColor = [0.0, 0.0, 0.0]
      renderView1.AxesGrid.YTitleFontFile = ''
      renderView1.AxesGrid.ZTitleColor = [0.0, 0.0, 0.0]
      renderView1.AxesGrid.ZTitleFontFile = ''
      renderView1.AxesGrid.XLabelColor = [0.0, 0.0, 0.0]
      renderView1.AxesGrid.XLabelFontFile = ''
      renderView1.AxesGrid.YLabelColor = [0.0, 0.0, 0.0]
      renderView1.AxesGrid.YLabelFontFile = ''
      renderView1.AxesGrid.ZLabelColor = [0.0, 0.0, 0.0]
      renderView1.AxesGrid.ZLabelFontFile = ''

      # register the view with coprocessor
      # and provide it with information such as the filename to use,
      # how frequently to write the images, etc.
      coprocessor.RegisterView(renderView1,
          filename='image_%t.png', freq=1, fittoscreen=0, magnification=1, width=574, height=555, cinema={})
      renderView1.ViewTime = datadescription.GetTime()

      # ----------------------------------------------------------------
      # restore active view
      SetActiveView(renderView1)
      # ----------------------------------------------------------------

      # ----------------------------------------------------------------
      # setup the data processing pipelines
      # ----------------------------------------------------------------

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

      # ----------------------------------------------------------------
      # setup the visualization in view 'renderView1'
      # ----------------------------------------------------------------

      # show data from resampleWithDataset1
      resampleWithDataset1Display = Show(resampleWithDataset1, renderView1)

      # trace defaults for the display properties.
      resampleWithDataset1Display.Representation = 'Surface'
      resampleWithDataset1Display.ColorArrayName = [None, '']
      resampleWithDataset1Display.OSPRayScaleArray = 'ObjectId'
      resampleWithDataset1Display.OSPRayScaleFunction = 'PiecewiseFunction'
      resampleWithDataset1Display.SelectOrientationVectors = 'None'
      resampleWithDataset1Display.ScaleFactor = 0.1
      resampleWithDataset1Display.SelectScaleArray = 'None'
      resampleWithDataset1Display.GlyphType = 'Arrow'
      resampleWithDataset1Display.GlyphTableIndexArray = 'None'
      resampleWithDataset1Display.GaussianRadius = 0.005
      resampleWithDataset1Display.SetScaleArray = ['POINTS', 'ObjectId']
      resampleWithDataset1Display.ScaleTransferFunction = 'PiecewiseFunction'
      resampleWithDataset1Display.OpacityArray = ['POINTS', 'ObjectId']
      resampleWithDataset1Display.OpacityTransferFunction = 'PiecewiseFunction'
      resampleWithDataset1Display.DataAxesGrid = 'GridAxesRepresentation'
      resampleWithDataset1Display.SelectionCellLabelFontFile = ''
      resampleWithDataset1Display.SelectionPointLabelFontFile = ''
      resampleWithDataset1Display.PolarAxes = 'PolarAxesRepresentation'
      resampleWithDataset1Display.ScalarOpacityUnitDistance = 0.15001951396025187

      # init the 'PiecewiseFunction' selected for 'ScaleTransferFunction'
      resampleWithDataset1Display.ScaleTransferFunction.Points = [2.0, 0.0, 0.5, 0.0, 2.00048828125, 1.0, 0.5, 0.0]

      # init the 'PiecewiseFunction' selected for 'OpacityTransferFunction'
      resampleWithDataset1Display.OpacityTransferFunction.Points = [2.0, 0.0, 0.5, 0.0, 2.00048828125, 1.0, 0.5, 0.0]

      # init the 'GridAxesRepresentation' selected for 'DataAxesGrid'
      resampleWithDataset1Display.DataAxesGrid.XTitleColor = [0.0, 0.0, 0.0]
      resampleWithDataset1Display.DataAxesGrid.XTitleFontFile = ''
      resampleWithDataset1Display.DataAxesGrid.YTitleColor = [0.0, 0.0, 0.0]
      resampleWithDataset1Display.DataAxesGrid.YTitleFontFile = ''
      resampleWithDataset1Display.DataAxesGrid.ZTitleColor = [0.0, 0.0, 0.0]
      resampleWithDataset1Display.DataAxesGrid.ZTitleFontFile = ''
      resampleWithDataset1Display.DataAxesGrid.XLabelColor = [0.0, 0.0, 0.0]
      resampleWithDataset1Display.DataAxesGrid.XLabelFontFile = ''
      resampleWithDataset1Display.DataAxesGrid.YLabelColor = [0.0, 0.0, 0.0]
      resampleWithDataset1Display.DataAxesGrid.YLabelFontFile = ''
      resampleWithDataset1Display.DataAxesGrid.ZLabelColor = [0.0, 0.0, 0.0]
      resampleWithDataset1Display.DataAxesGrid.ZLabelFontFile = ''

      # init the 'PolarAxesRepresentation' selected for 'PolarAxes'
      resampleWithDataset1Display.PolarAxes.PolarAxisTitleColor = [0.0, 0.0, 0.0]
      resampleWithDataset1Display.PolarAxes.PolarAxisTitleFontFile = ''
      resampleWithDataset1Display.PolarAxes.PolarAxisLabelColor = [0.0, 0.0, 0.0]
      resampleWithDataset1Display.PolarAxes.PolarAxisLabelFontFile = ''
      resampleWithDataset1Display.PolarAxes.LastRadialAxisTextColor = [0.0, 0.0, 0.0]
      resampleWithDataset1Display.PolarAxes.LastRadialAxisTextFontFile = ''
      resampleWithDataset1Display.PolarAxes.SecondaryRadialAxesTextColor = [0.0, 0.0, 0.0]
      resampleWithDataset1Display.PolarAxes.SecondaryRadialAxesTextFontFile = ''

      # Generate Writer to dump resampled files
      writer = servermanager.writers.XMLPUnstructuredGridWriter(Input = resampleWithDataset1)
      coprocessor.RegisterWriter(writer, filename = "grid_%t.pvtu",freq=1)

      # ----------------------------------------------------------------
      # finally, restore active source
      SetActiveSource(resampleWithDataset1)
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
