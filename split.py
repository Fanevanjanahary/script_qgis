# -*- coding: utf-8 -*-

from qgis.PyQt.QtCore import QCoreApplication
from qgis.core import (QgsProcessing,
                       QgsCoordinateReferenceSystem,
                       QgsFeatureSink,
                       QgsProcessingException,
                       QgsProcessingAlgorithm,
                       QgsProcessingParameterRasterLayer,
                       QgsProcessingParameterFolderDestination,
                       QgsProcessingParameterNumber,
                       QgsProcessingParameterCrs)
import processing

class SliptRasterProcessing(QgsProcessingAlgorithm):
    
    INPUT = 'INPUT'
    DIMENSIONS = 'DIMENSIONS'
    CRS = 'CRS'
    OUTPUT = 'OUTPUT'
   
   
    def createInstance(self):
        return SliptRasterProcessing()
    
    
    def name(self):
        return 'splitraster'
    
    
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
        
        self.addParameter(
            QgsProcessingParameterNumber(
            self.DIMENSIONS, 
            'Dimension', 
            type = QgsProcessingParameterNumber.Double,
            defaultValue = 25.00,
            minValue = 25.00,
            maxValue = 100.00
            )
        )
        
        self.addParameter(
            QgsProcessingParameterCrs(
            self.CRS, 'Projection', 
            )
        )
        
        # We add a feature sink in which to store our processed features (this
        # usually takes the form of a newly created vector layer when the
        # algorithm is run in QGIS).
        self.addParameter(
            QgsProcessingParameterFolderDestination(
                self.OUTPUT,
                'Sortie'
            )
        )
    
    
    def processAlgorithm(self, parameters, context, feedback):
        
        raster = self.parameterAsRasterLayer(
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

        folder = self.parameterAsFile(
            parameters, 
            self.OUTPUT, 
            context
        )
        
        dim = self.parameterAsDouble(
            parameters, 
            self.DIMENSIONS, 
            context
        )
        
        raster.setCrs(crs)
        
        feedback.pushInfo('Création de la grille')
        result = processing.run("qgis:creategrid", {
                        'TYPE':2,
                        'EXTENT': raster,
                        'HSPACING':dim,
                        'VSPACING':dim,
                        'HOVERLAY':0,
                        'VOVERLAY':0,
                        'CRS':crs.authid(),
                        'OUTPUT':'memory:'
                        },context=context, feedback=feedback)


        feedback.pushInfo('Calcul des stats zonales')
        processing.run("qgis:zonalstatistics", {
                        'INPUT_RASTER':raster,
                        'RASTER_BAND':1,
                        'INPUT_VECTOR':result['OUTPUT'],
                        'COLUMN_PREFIX':'_',
                        'STATS':[0]
                        },context=context, feedback=feedback)
        
        feedback.pushInfo('Extraction des cellules intersectant le raster')
        result = processing.run("native:extractbyexpression", {
                    'INPUT':result['OUTPUT'],
                    'EXPRESSION':'\"_count\" > 0',
                    'OUTPUT':'memory:'
                    },context=context, feedback=feedback)

        #grid = QgsProject.instance().layerStore().mapLayer(result['OUTPUT'])
        grid = result['OUTPUT']
        #print(result)

        feedback.pushInfo('Découpage')
        for i, item in enumerate(grid.getFeatures()):
            processing.runAndLoadResults("gdal:cliprasterbyextent", {
                        'INPUT':raster,
                        'PROJWIN':item.geometry().boundingBox(),
                        'NODATA':None,
                        'OPTIONS':'',
                        'DATA_TYPE':0,
                        'OUTPUT':'{}/{}_{}.tif'.format(folder, raster.name(), i)
                        },context=context)
        output = { self.OUTPUT:folder}
        return output