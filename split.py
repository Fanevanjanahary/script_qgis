# -*- coding: utf-8 -*-

from qgis.PyQt.QtCore import QCoreApplication
from qgis.core import (QgsProcessing,
                       QgsFeatureSink,
                       QgsProcessingException,
                       QgsProcessingAlgorithm,
                       QgsProcessingParameterFeatureSource,
                       QgsProcessingParameterRasterLayer,
                       QgsProcessingParameterFeatureSink,
                       QgsProcessingParameterCrs)
import processing

class SliptRasterProcessing(QgsProcessingAlgorithm):
    
    INPUT = 'Image png'
    CRS = 'Crs'
    OUTPUT = 'Sortie'
    
    def createInstance(self):
        return SliptRasterProcessing()
    
    def name(self):
        return 'split_raster'
    
    def displayName(self):
        return 'Découpage Raster'
    
    def group(self):
        return 'Scripts de FuturMap'
    
    def initAlgorithm(self, config=None):
        """
        Here we define the inputs and output of the algorithm, along
        with some other properties.
        """

        # We add the input vector features source. It can have any kind of
        # geometry.
        self.addParameter(QgsProcessingParameterRasterLayer(self.INPUT,
                                                            'Raster'
                                                               ))

        # We add a feature sink in which to store our processed features (this
        # usually takes the form of a newly created vector layer when the
        # algorithm is run in QGIS).
        self.addParameter(
            QgsProcessingParameterFeatureSink(
                self.OUTPUT,
                'Sortie'
            )
        )
        
        self.addParameter(
            QgsProcessingParameterCrs(
            self.CRS, 'Projection', 
            optional=True)
        )
    
    def processAlgorithm(self, parameters, context, feedback):
        
        rester = self.parameterAsRasterLayer(
            parameters,
            self.INPUT,
            context
        )
        
        if raster is None:
            raise QgsProcessingException(self.invalidRasterError(
                parameters, 
                self.INPUT
            ))

        crs = self.parameterAsCrs(
            parameters, 
            self.CRS, 
            context
        )
        
        ext = raster.extent()
        xmin = ext.xMinimum()
        xmax = ext.xMaximum()
        ymin = ext.yMinimum()
        ymax = ext.yMaximum()
        coords = '{},{},{},{}'.format(xmin,xmax,ymin,ymax)
        
        for band in range(1, layer.bandCount() + 1):
            stats = provider.bandStatistics(band, QgsRasterBandStats.All, ext, 0)
            min = stats.minimumValue
            max = stats.maximumValue
            provider.setNoDataValue(band,max)
            layer.triggerRepaint()
        
        grid = processing.run("qgis:creategrid", param={
                'TYPE':2,
                'EXTENT':coords,
                'HSPACING':200,
                'VSPACING':200,
                'HOVERLAY':0,
                'VOVERLAY':0,
                'CRS':'EPSG:3946',
                'OUTPUT':'memory:'
                })


