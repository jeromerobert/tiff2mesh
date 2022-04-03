#! /usr/bin/env python3

import glob
from vtkmodules.vtkFiltersGeneral import vtkPassArrays
from vtkmodules.vtkFiltersCore import vtkImageAppend, vtkFlyingEdges3D, vtkBinnedDecimation
from vtkmodules.vtkIOImage import vtkTIFFReader
from vtkmodules.vtkIOXML import vtkXMLImageDataWriter, vtkXMLPolyDataWriter
from vtkmodules.vtkImagingCore import vtkExtractVOI
from vtkmodules.vtkImagingGeneral import vtkImageMedian3D

PATTERN="XMT - 200 slices/Sample 1/*.tif"
VOI=[250,400,250,400]
ISO_VALUE=9200
DECIMATE_DIV=[100]*3

def load_image_data(pattern, voi=None):
    image_append = vtkImageAppend()
    image_append.SetAppendAxis(2) # Z axis
    files = sorted(glob.glob(PATTERN))
    for filename in files:
        tiff_reader = vtkTIFFReader()
        tiff_reader.SetFileName(filename)
        out = tiff_reader.GetOutputPort()
        if voi is not None:
            ev = vtkExtractVOI()
            ev.SetVOI(voi+[0,0])
            ev.SetInputConnection(out)
            out = ev.GetOutputPort()
        image_append.AddInputConnection(out)
    return image_append.GetOutputPort(), (image_append)

im_writer = vtkXMLImageDataWriter()
im_writer.SetFileName("output.vti")
im_writer.SetDataModeToAppended()
im_writer.EncodeAppendedDataOff()
imaged, _ = load_image_data(PATTERN, voi=VOI)
im_writer.SetInputConnection(imaged)
im_writer.Update()

median = vtkImageMedian3D()
median.SetInputConnection(imaged)
median.SetKernelSize(5, 5, 5)

contour = vtkFlyingEdges3D()
contour.SetInputConnection(median.GetOutputPort())
contour.SetValue(0, ISO_VALUE)

pass_array = vtkPassArrays()
pass_array.ClearArrays()
pass_array.AddPointDataArray("Normals")
pass_array.SetInputConnection(contour.GetOutputPort())

decimate = vtkBinnedDecimation()
decimate.SetInputConnection(pass_array.GetOutputPort())
decimate.AutoAdjustNumberOfDivisionsOn()
decimate.SetNumberOfDivisions(DECIMATE_DIV)

pd_writer = vtkXMLPolyDataWriter()
pd_writer.SetFileName("output.vtp")
pd_writer.SetInputConnection(decimate.GetOutputPort())
pd_writer.SetDataModeToAppended()
pd_writer.EncodeAppendedDataOff()
pd_writer.Update()
