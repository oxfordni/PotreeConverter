## example usage
# ---------------
# import POTreeReader
# from shapely.geometry import Polygon
# folder = '/home/bramalingam/src/PotreeConverter_oxfordni/build/potree_converted_locb_test/data/r/'
# potree = PoTree(folder)
# bounding_box = Polygon([(725, 574) , (778, 574), (778, 520), (725, 520)]) 
# points = potree.get_points(bounding_box)
# print(points)

import glob, os
import numpy as np
import struct
import time
import json
import math

#imports for plotting method
import matplotlib.pyplot as plt
from shapely.geometry import Polygon
from descartes import PolygonPatch

#import for reading lasfile 
import laspy
from laspy.file import File
#import for creating the rtree from the headers of the POTree nodes
from rtree.index import Index


# calculates bounding box (shapely polygon) for the octree node
def get_bounding_box(inFile):
    
    header = inFile.header
    header_min = header.min
    header_max = header.max
    bounding_box = []
    bounding_box[0] = header_min[0]
    bounding_box[1] = header_min[1]
    bounding_box[2] = header_max[0]
    bounding_box[3] = header_max[1]
    bounding_box = get_shapely_polygon(bounding_box)
    return bounding_box

def get_shapely_polygon(bounding_box):

    x_min = bounding_box[0]
    y_min = bounding_box[1]
    x_max = bounding_box[2]
    y_max = bounding_box[3]
    shapely_polygon = Polygon([(x_min, y_min), (x_min, y_max), (x_max, y_max), (x_max, y_min)])
    return shapely_polygon

class PoTree:
    # initializes the PoTree class and reads the PoTree las files from every node,
    # computes the bounding boxes for every node from the las headers for the node
    def __init__(self, foldername):
        
        inputFolder = os.path.abspath(foldername)
        print ('Starting  rtree extraction...')
        print(inputFolder+ '/rtree')
        t0 = time.time()
        idx = Index(inputFolder + '/rtree')
        print ('Finished loading %.2f seconds' % (time.time() - t0))
        
        cloudJSAbsPath = inputFolder + '/cloud.js'
        if not os.path.isfile(cloudJSAbsPath):
            raise Exception('Error: ' + cloudJSAbsPath + ' is not found!')
        cloudJSData = json.loads(open(cloudJSAbsPath, 'r').read()) 

        twod_bbox = cloudJSData['boundingBox']
        lx = twod_bbox['lx']
        ly = twod_bbox['ly']
        mx = twod_bbox['ux']
        my = twod_bbox['uy']

        self.octree_depth = cloudJSData['hierarchyStepSize']
        self.foldername = foldername
        self.rtree_idx = idx
        self.bounding_box = get_shapely_polygon((lx, ly, mx, my))
        print((lx, ly, mx, my))

    # returns a dictionary of points at multiple resolutions
    def get_points(self, bounding_box):

        # shapely based viewer resoltion calculation (==fraction of image requested)
        total_polygon = self.bounding_box
        viewport_polygon = get_shapely_polygon(bounding_box)
        intersect_polygon = total_polygon.intersection(viewport_polygon)
        resolution = intersect_polygon.area/total_polygon.area

        # hits = self.rtree_idx.intersection((bounding_box), objects=True)

        # request for 15 closest nodes to the query bounding box from the rtree
        hits = self.rtree_idx.nearest((bounding_box), 15, objects = True)

        # create absolute paths for the las files for the ids fetched from the rtree
        filenames = {}
        for i in list(hits):
            rtree_node_id = i.id
            filename = (self.foldername + '/data/r/' + str(rtree_node_id).replace('8','r') + '.las')
            if not os.path.isfile(filename):
                filename = (self.foldername + '/data/r/' + str(rtree_node_id).replace('8','') + '/' + str(rtree_node_id).replace('8','r') + '.las')
            filenames[filename] = len(str(rtree_node_id).replace('8','r'))

        # refilter for intelligent resolution picking (will need iterative rework)
        if resolution >=0.10:
            filenames = {k: v for k, v in filenames.items() if v<=math.ceil(self.octree_depth/2)}
        else:
            filenames = {k: v for k, v in filenames.items() if v>=math.ceil(self.octree_depth/2)}

        # loop through filtered files to get points (based on viewer resolution)
        points = []
        for filename in filenames.keys():   
            # read las file from the node
            inFile = File(filename, mode='r')
            header_old = inFile.header
            scale = header_old.scale
            # # read the extra bytes from the object (if present)
            # # this is where all the extra attributes part of the locb point schema live
            extra_attributes = inFile.extra_bytes

            # # 2 attributes added as extra bytes to the LAS schema:
            # # first two bytes: channelIndex, second two bytes: frameIndex
            attributes = np.empty([extra_attributes.size, 2], dtype=int)
            for point_index, point_attribute in enumerate(extra_attributes):
                attributes[point_index] = struct.unpack("=HH", extra_attributes[point_index])
            
            channel_index = attributes[:, 0]  # no offset or scaling added to this attribute
            frame_index = attributes[:, 1] # no offset or scaling added to this attribute

            # # resolution level estimation from the filename
            # # reference for documentation : 
            # # data and index files section of https://github.com/potree/potree/blob/develop/docs/potree-file-format.md
            # level = len(filename.rsplit('/', 1)[-1])
            
            coords = np.vstack((inFile.x, inFile.y, inFile.z, channel_index, frame_index, inFile.intensity)).transpose()
            print(inFile.intensity.dtype)
            # # append points for a certain resolution from the octree to the dictionary
            if points == []:
                points = coords
            else:
                points = np.vstack((points, coords))

            inFile.close()

        # filter points within the bounding box
        bx1 = bounding_box[0]
        by1 = bounding_box[1]
        bx2 = bounding_box[2]
        by2 = bounding_box[3]
        ll = np.array([bx1, by1])  # lower-left

        ur = np.array([bx2, by2])  # upper-right
        inidx = np.all(np.logical_and(ll <= points[:,1:2], points[:,1:2] <= ur), axis=1)
        points = points[inidx]

        return points

    # plot the bounding boxes of the multiple resolutions
    def plot_resolution_levels(self, bounding_box):

        hits = self.rtree_idx.intersection((bounding_box), objects=True)
        filenames = [print(foldername + str(i.id).replace('8','r') + '.las') for i in list(hits)]

        fig, ax = plt.subplots(1,1)
        for filename in filenames:

            inFile = File(filename, mode='r')
            bounding_box1 = get_bounding_box(inFile)
            ax.add_patch(PolygonPatch(bounding_box1, alpha=0.3))

        ax.set_xlim([0, 1000])
        ax.set_ylim([0, 1000])
        plt.show()

    def create_las_summary_file(points):

        #create header object
        header=laspy.header.Header()
        xmin = np.floor(np.min(points[:,0]))
        ymin = np.floor(np.min(points[:,1]))
        zmin = np.floor(np.min(points[:,2]))

        outfile = File('potree_points_tester.las', mode = "w", header=header)
        outfile.header.offset = [xmin,ymin,zmin]
        outfile.header.scale = scale
        outfile.x = points[:,0]
        outfile.y = points[:,1]
        outfile.z = points[:,2]
        outfile.close()