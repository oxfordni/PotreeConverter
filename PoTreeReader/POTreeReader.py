import matplotlib.pyplot as plt
import csv
from laspy.file import File
import numpy as np
import glob, os
from shapely.geometry import Polygon
from descartes.patch import PolygonPatch

folder = '/home/bramalingam/src/PotreeConverter_oxfordni/build/potree_converted_locb_test/data/r/'

def get_bounding_box(inFile):
    header = inFile.header
    header_min = header.min
    header_max = header.max
    x_min = header_min[0]
    y_min = header_min[1]
    z_min = header_min[2]
    x_max = header_max[0]
    y_max = header_max[1]
    z_max = header_max[2]
    bounding_box = Polygon([(x_min, y_min), (x_min, y_max), (x_max, y_max), (x_max, y_min)])
    return bounding_box

class PoTree:
    def __init__(self, foldername):
        file_names = sorted(glob.glob(folder + '*.las'))
        point_counter = 0
        shapely_polygons = {}
        for file in file_names:
            inFile = File(file, mode='r')
            point_counter = point_counter + inFile.get_header().get_count()
            shapely_polygons[file] = get_bounding_box(inFile)

        self.num_points = point_counter 
        self.shapely_polygons = shapely_polygons


    def get_points(self, shapely_polygon):

        points = {}

        fig, ax = plt.subplots(1,1)
        for filename in self.shapely_polygons.keys():

            if self.shapely_polygons[filename].intersects(shapely_polygon):
                inFile = File(filename, mode='r')
                level = len(filename.rsplit('/', 1)[-1])
                
                if level not in points:
                    points[level] = []
                points[level].append(len(inFile.get_points()))
                bounding_box = get_bounding_box(inFile)
                ax.add_patch(PolygonPatch(bounding_box, alpha=0.3))
                # print(level, level not in points, points)

        ax.set_xlim([0, 1000])
        ax.set_ylim([0, 1000])
        plt.show()

        return points

potree = PoTree(folder)
bounding_box = Polygon([(725, 574) , (778, 574), (778, 520), (725, 520)]) 
points = potree.get_points(bounding_box)
print(points)


