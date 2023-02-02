import os, sys
import tarfile
import shutil
import warnings
import xml.etree.cElementTree as etree
from shapely.geometry import Polygon, shape
import fiona
import numpy as np

def load_shape(shapefile, buffer=0.02):
    # This function creates a shape to make a selection of usable bursts later on. Buffer around shape is in
    # degrees.

    if not shapefile:
        warnings.warn('Please provide a shapefile or coordinates.')

    try:
        if isinstance(shapefile, list):  # If the coordinates are already loaded. (for example bounding box)
            shp = Polygon(shapefile)
        else:  # It should be a shape file. We always select the first shape.
            sh = next(iter(fiona.open(shapefile)))#.next()
            shp = shape(sh['geometry'])

        # Now we have the shape we add a buffer and simplify first to save computation time.
        shp = shp.simplify(buffer / 2)
        shp = shp.buffer(buffer)
    except:
        warnings.warn('Unrecognized shape')
        return

    return shp

def extract_kml_preview(tarred_folder, dir='', kml=True, png=True, overwrite=False):
    # Extracts quicklook and/or .kml files.

    if not dir:
        dir = os.path.dirname(tarred_folder)
    
    #base file names
    base_name = os.path.basename(tarred_folder)[:-7]
    first_folder_name = base_name[:13]+'_____'+base_name[18:-4]
    xml_file = first_folder_name+'/'+first_folder_name+'.xml'
    kml_file = first_folder_name+'/SUPPORT/GEARTH_POLY.kml'
    preview_file = first_folder_name+'/PREVIEW/BROWSE.tif'
    
    #new file names
    xml_name = os.path.join(dir, first_folder_name + '.xml')
    kml_name = os.path.join(dir, first_folder_name + '.kml')
    tif_name = os.path.join(dir, first_folder_name + '.tif')
    
    #unzipped file names
    unzipped_xml = os.path.join(dir, xml_file)
    unzipped_kml = os.path.join(dir, kml_file)
    unzipped_tif = os.path.join(dir, preview_file)
    
    #only extract if required
    if not os.path.exists(kml_name) or not os.path.exists(tif_name) or not os.path.exists(xml_name):
        #print('aay')
        my_tar = tarfile.open(tarred_folder)
        my_tar.extract(xml_file, dir)
        my_tar.extract(kml_file, dir)
        my_tar.extract(preview_file, dir)
        my_tar.close()
    
    if not os.path.exists(xml_name) or overwrite == True:
        os.system('cp '+ unzipped_xml +' '+ xml_name)
    if not os.path.exists(kml_name) or overwrite == True:
        os.system('cp '+ unzipped_kml +' '+ kml_name)
    if not os.path.exists(tif_name) or overwrite == True:
        os.system('cp '+ unzipped_tif +' '+ tif_name)
    if os.path.exists(os.path.join(dir, first_folder_name)):
        os.system('rm -rf ' + os.path.join(dir, first_folder_name))
    
    return xml_name, kml_name, tif_name


def shape_im_kml(shp, kml_file):
    # This script extracts a Fiona/polygon shape of the footprint given in the .xml file of the image and checks whether
    # it overlaps

    # First check is .kml file exist
    if not os.path.exists(kml_file):
        warnings.warn('.kml file does not exist.')
        return False

    try:
        in_kml = etree.parse(kml_file)
        in_kml = in_kml.getroot()
        coor = in_kml[0][3][3][0][0].text
        
        coor = [i.split(',')[:-1] for i in coor.split('\n')][1:-1]
        
        coverage = Polygon([[float(i[0]),float(i[1])] for i in coor])
    except:
        warnings.warn('.kml file is corrupt')
        return False

    if coverage.intersects(shp):
        return True
    else:
        return False



def unzip_folder(tarred_folder, dest_folder, overwrite=False, cos_file_name='IMAGE_VV_SRA_strip_009.cos'):
    # Extracts quicklook and/or .kml files.

    if not dest_folder:
        dest_folder = os.path.dirname(tarred_folder)

    png_name = ''
    kml_name = ''
    
    #base file names
    base_name = os.path.basename(tarred_folder)[:-7]
    first_folder_name = base_name[:13]+'_____'+base_name[18:-4]
    
    cos_file = first_folder_name+'/IMAGEDATA/'+cos_file_name
    xml_file = first_folder_name+'/'+first_folder_name+'.xml'
    #new file names
    cos_d_name = os.path.join(dest_folder, first_folder_name + '.cos')
    xml_file_name = os.path.join(dest_folder, first_folder_name+'.xml')
    
    #unzipped file names
    unzipped_cos = os.path.join(dest_folder, cos_file)
    unzipped_xml = os.path.join(dest_folder, xml_file)
    
    #only extract if required
    #TODO make changes for not xtracting once the data is dumped into stack folder
    if not os.path.exists(cos_d_name) and not os.path.exists(xml_file_name):
        my_tar = tarfile.open(tarred_folder)
        my_tar.extract(cos_file, dest_folder)
        my_tar.extract(xml_file, dest_folder)
        my_tar.close()
    
    if not os.path.exists(cos_d_name) or overwrite == True:
        os.system('cp '+ unzipped_cos +' '+ cos_d_name)
    if not os.path.exists(xml_file_name) or overwrite == True:
        os.system('cp '+ unzipped_xml +' '+ xml_file_name)
    if os.path.exists(os.path.join(dest_folder, first_folder_name)):
        os.system('rm -rf ' + os.path.join(dest_folder, first_folder_name))
    
    #return cos_d_name, xml_file_name


if __name__=='__main__':
    tarred_folder = sys.argv[1]
    dest_folder = sys.argv[2]
    overwrite = sys.argv[3]
    image_cos_file = sys.argv[4]
    
    if overwrite == 'False':
        overwrite = False
    else:
        overwrite = True
    
    print('tarred folder is ' + tarred_folder)
    print('destination folder is ' + dest_folder)
    
    unzip_folder(tarred_folder, dest_folder, overwrite=overwrite, cos_file_name=image_cos_file)
