import pytest
import numpy as np
import time
from concurrent.futures import ThreadPoolExecutor
import cProfile

from ndstructs import Array5D, Slice5D, Shape5D
from ndstructs.datasource import DataSource
from ilastik.features.fastfilters import (
    GaussianSmoothing,
    HessianOfGaussianEigenvalues,
    GaussianGradientMagnitude,
    LaplacianOfGaussian,
    DifferenceOfGaussians,
    StructureTensorEigenvalues
)
from ilastik.annotations import Annotation
from ilastik.classifiers.pixel_classifier import PixelClassifier, StrictPixelClassifier

datasource = DataSource.create("/home/tomaz/SampleData/n5tests/317_8_CamKII_tTA_lacZ_Xgal_s123_1.4.n5/data")
#datasource = DataSource.create("/home/tomaz/SampleData/c_cells/cropped/huge/cropped1.png")
#print(datasource.full_shape)
print(datasource.tile_shape)

extractors = [
    GaussianSmoothing(sigma=0.3),
    HessianOfGaussianEigenvalues(scale=1.0),
    GaussianGradientMagnitude(sigma=0.3),
    LaplacianOfGaussian(scale=0.3),
    DifferenceOfGaussians(sigma0=0.3, sigma1=1.0 * 0.66),
    StructureTensorEigenvalues(innerScale=1.0, outerScale=1.0 * 0.5),
]

annotations = (
    Annotation.from_png("/home/tomaz/SampleData/c_cells/cropped/cropped1_10_annotations_offset_by_188_124.png",
                        raw_data=datasource),
)

classifier = PixelClassifier(feature_extractors=extractors, annotations=annotations)

print("Classifier created!!")


predictions = classifier.allocate_predictions(datasource)
with ThreadPoolExecutor(max_workers=8) as executor:
    tiles = list(datasource.get_tiles(Shape5D(x=1024, y=1024, c=3)))
    for raw_tile in tiles:
        def predict_tile(raw_tile):
            tile_prediction, tile_features = classifier.predict(raw_tile)
            #predictions.set(tile_prediction)
            print(f"Tile {raw_tile} done! {time.time()}")
        executor.submit(predict_tile, raw_tile)
