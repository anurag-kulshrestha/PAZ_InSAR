# This files defines a class for metadata objects of sentinel images. Large part of the work depends on python readers
# from the tops toolbox.
import os
import warnings
import zipfile
import copy

#from doris.doris_stack.main_code.swath import SwathMeta
#from swath import SwathMeta


class ImageMeta(object):
    # Object for image files for sentinel data

    def __init__(self, path='' , pol='all'):
        # Initialize function variables
        self.cos_input_file=''
        self.cos_file=''
        self.xml_file=''
        
        self.date_path = ''
        
        # This will contain a list of swath objects
        self.swaths = []
        self.pol = pol
        #self.swath_no = swath_no

        # The following contain the path of xml and data files
        self.swaths_xml = []
        self.swaths_data = []
        self.image_kml = ''

        # This variable contains the convex hull of all swaths together
        self.metadata = []
        self.coverage = []

        # The following variables store data on which processing steps are performed and the results of these steps.
        self.steps = []
        self.steps_res = []

        # The following variable is to check the total number of bursts for this image. This is used to remove time
        # slots with less bursts.
        self.burst_no = 0

        # Check if the data is unzipped or not. If unzipped run the further initialization.
        self.zip_path = ''
        self.unzip_path = ''
        if path.endswith('.tar.gz'):
            self.zip_path = path
        else:
            self.unzip_path = path

        # orbit information for this image
        self.orbit = ''
