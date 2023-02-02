#!/usr/bin/python
# Author: Anurag, Adapted from Prabhu's code
# live code for parsing of XML Paz file into python data structures
# and from there into DORIS res file structure

# this is rather fair implementation and should be used as a structure
# for the future implementation of XML/GeoTIFF data readers

from lxml import etree
import string, time, sys
#import xml.etree.ElementTree as ElementTree
#import types

def usage():
    print('\nUsage: python paz_dump_header2doris.py paz_XML_product > outputfile')
    print('  where paz_XML_product is the input filename')
#    print '        outputfile      is the output DORIS resultfile'

try:
    inputFileName  = sys.argv[1]
    outputFileName = sys.argv[2]
    outStream      = open(outputFileName,'w')
except:
    print('Unrecognized input')
    usage()
    sys.exit(1)

# input file
#inputFileName  = '04091/04091.xml'
#
#outputFileName = 'inputFileName'


inTree = etree.parse(inputFileName)

# query syntax for every field
queryList = {\
             # mission info
             'mission'   : './/generalHeader/mission',\
             # imageData file
             'imageData'  : './/productComponents/imageData/file/location/filename',\
             'imageLines' : './/productInfo/imageDataInfo/imageRaster/numberOfRows',\
             'imagePixels': './/productInfo/imageDataInfo/imageRaster/numberOfColumns',\
              # volume info
             'volFile' : './/productComponents/annotation/file/location/filename',\
             'volID'   : './/generalHeader/itemName',\
             'volRef'  : './/generalHeader/referenceDocument',\
             # product info
             'productSpec'    : './/generalHeader/referenceDocument',\
             'productVolDate' : './/setup//IOCSAuxProductGenerationTimeUTC',\
             'productDate'    : './/generalHeader/generationTime',\
             'productFacility': './/productInfo/generationInfo/level1ProcessingFacility',\
             # scene info
             'scenePol'     : './/productInfo/acquisitionInfo//polLayer',\
             'sceneMode'    : './/setup/orderInfo/imagingMode',\
             'sceneCenLat'  : './/productInfo/sceneInfo/sceneCenterCoord/lat',\
             'sceneCenLon'  : './/productInfo/sceneInfo/sceneCenterCoord/lon',\
             'sceneRecords' : './/productInfo/imageDataInfo/imageRaster/numberOfRows',\
             # orbit info
             'orbitABS' : './/productInfo/missionInfo/absOrbit',\
             'orbitDir' : './/productInfo/missionInfo/orbitDirection',\
             'orbitTime': './/platform/orbit/stateVec/timeUTC',\
             'orbitX'   : './/platform/orbit/stateVec/posX',\
             'orbitY'   : './/platform/orbit/stateVec/posY',\
             'orbitZ'   : './/platform/orbit/stateVec/posZ',\
             # range
             'rangeRSR'     :'.//productSpecific/complexImageInfo/commonRSF',\
             'rangeBW'      :'.//processing/processingParameter/rangeLookBandwidth',\
             'rangeWind'    :'.//processing/processingParameter/rangeWindowID',\
             'rangeTimePix' :'.//productInfo/sceneInfo/rangeTime/firstPixel',\
             # azimuth
             'azimuthPRF'       :'.//productSpecific/complexImageInfo/commonPRF',\
             'azimuthBW'        :'.//processing/processingParameter/azimuthLookBandwidth',\
             'azimuthWind'      :'.//processing/processingParameter/azimuthWindowID',\
             'azimuthTimeStart' : './/productInfo/sceneInfo/start/timeUTC',\
             # doppler
             'dopplerTime'  :'.//dopplerEstimate/timeUTC',\
             'dopplerCoeff0':'.//combinedDoppler/coefficient[@exponent="0"]',\
             'dopplerCoeff1':'.//combinedDoppler/coefficient[@exponent="1"]',\
             'dopplerCoeff2':'.//combinedDoppler/coefficient[@exponent="2"]',\
             }

# temp variables and parameters
container     = {}
# containerTemp = {}
events        = ('end',)

# functions : not sure if needed
def fast_iter_string(context):
    for event,elem in context:
        return elem.text

# works with lists
def fast_iter_list(context,tag=''):
    for event,elem in context:
        return elem.iterchildren(tag=tag).next().text

def hms2sec(hmsString,convertFlag='int'):
    # input hmsString syntax: XX:XX:XX.xxxxxx
    secString = int(hmsString[0:2])*3600 + \
        int(hmsString[3:5])*60 + \
        float(hmsString[6:])
    if convertFlag == 'int' :
        return int(secString)
    elif convertFlag == 'float' :
        return float(secString)
    else:
        return int(secString)


for key in queryList.keys():

    try:
        vars()[key];
    except KeyError or NameError:
        vars()[key] = [];

    queryListKey = queryList[key]
    for nodes in inTree.findall(queryListKey):
#    for nodes in inTree.findall(queryList[key]):
        vars()[key].append(nodes.text)

    container[key] = vars()[key]


# ---------------------------------------------------------------------------------------------------------

dummyVar = 'DUMMY'

#print('MASTER RESULTFILE:        %s\n' % outputFileName)


outStream.write('\ntsx_dump_header2doris.py v1.0, doris software, 2009\n')
outStream.write('\n')
outStream.write('\n')
outStream.write('Start_process_control\n')
outStream.write('readfiles:		1\n')
outStream.write('precise_orbits:         1\n')
outStream.write('crop:			0\n')
outStream.write('sim_amplitude:		0\n')
outStream.write('master_timing:		0\n')
outStream.write('oversample:		0\n')
outStream.write('resample:		0\n')
outStream.write('filt_azi:		0\n')
outStream.write('filt_range:		0\n')
outStream.write('NOT_USED:		0\n')
outStream.write('End_process_control\n')
outStream.write('\n')
outStream.write('\n')

outStream.write('*******************************************************************\n')
outStream.write('*_Start_readfiles:\n')
outStream.write('*******************************************************************\n')
outStream.write('Volume file: 					%s\n' % container['volFile'][0])
outStream.write('Volume_ID: 					%s\n' % container['volID'][0])
outStream.write('Volume_identifier: 				%s\n' % container['volRef'][0])
outStream.write('Volume_set_identifier: 				%s\n' % dummyVar)
outStream.write('(Check)Number of records in ref. file: 		%s\n' % container['sceneRecords'][0])
outStream.write('SAR_PROCESSOR:                                  %s\n' % str.split(container['productSpec'][0])[0])
outStream.write('Product type specifier: 	                %s\n' % container['mission'][0])
outStream.write('Logical volume generating facility: 		%s\n' % container['productFacility'][0])
outStream.write('Logical volume creation date: 			%s\n' % container['productVolDate'][0])
outStream.write('Location and date/time of product creation: 	%s\n' % container['productDate'][0])
outStream.write('Scene identification: 				Orbit: %s %s Mode: %s\n' % (container['orbitABS'][0],container['orbitDir'][0],container['sceneMode'][0]))
outStream.write('Scene location: 		                lat: %.4f lon: %.4f\n' % (float(container['sceneCenLat'][0]),float(container['sceneCenLon'][0])))
outStream.write('Leader file:                                 	%s\n' % container['volFile'][0])
outStream.write('Sensor platform mission identifer:         	%s\n' % container['mission'][0])
outStream.write('Scene_centre_latitude:                     	%s\n' % container['sceneCenLat'][0])
outStream.write('Scene_centre_longitude:                    	%s\n' % container['sceneCenLon'][0])
outStream.write('Radar_wavelength (m):                      	0.031\n') #HARDCODED!!!
outStream.write('First_pixel_azimuth_time (UTC):			%s %s\n' % (time.strftime("%d-%b-%Y",time.strptime(container['azimuthTimeStart'][0].split('T')[0],"%Y-%m-%d")),container['azimuthTimeStart'][0].split('T')[1][:-1]))
outStream.write('Pulse_Repetition_Frequency (computed, Hz): 	%s\n' % container['azimuthPRF'][0])
outStream.write('Total_azimuth_band_width (Hz):             	%s\n' % container['azimuthBW'][0])
outStream.write('Weighting_azimuth:                         	%s\n' % str.upper(container['azimuthWind'][0]))
outStream.write('Xtrack_f_DC_constant (Hz, early edge):     	%s\n' % container['dopplerCoeff0'][0])
outStream.write('Xtrack_f_DC_linear (Hz/s, early edge):     	%s\n' % container['dopplerCoeff1'][0])
try:
  outStream.write('Xtrack_f_DC_quadratic (Hz/s/s, early edge): 	%s\n' % container['dopplerCoeff2'][0])
except:
  outStream.write('Xtrack_f_DC_quadratic (Hz/s/s, early edge):    %s\n' % [0][0])
outStream.write('Range_time_to_first_pixel (2way) (ms):     	%0.15f\n' % (float(container['rangeTimePix'][0])*1000))
outStream.write('Range_sampling_rate (computed, MHz):       	%0.6f\n' % (float(container['rangeRSR'][0])/1000000))
outStream.write('Total_range_band_width (MHz):               	%s\n' % (float(container['rangeBW'][0])/1000000))
outStream.write('Weighting_range:                            	%s\n' % str.upper(container['rangeWind'][0]))
outStream.write('\n')
outStream.write('*******************************************************************\n')
outStream.write('Datafile: 					%s\n' % container['imageData'][0])
outStream.write('Dataformat: 				%s\n' % 'TSX_COSAR')  # hardcoded!!!
outStream.write('Number_of_lines_original: 			%s\n' % container['imageLines'][0])
outStream.write('Number_of_pixels_original: 	                %s\n' % container['imagePixels'][0])
outStream.write('*******************************************************************\n')
outStream.write('* End_readfiles:_NORMAL\n')
outStream.write('*******************************************************************\n')
outStream.write('\n')
outStream.write('\n')
outStream.write('*******************************************************************\n')
outStream.write('*_Start_precise_orbits\n')
outStream.write('*******************************************************************\n')
outStream.write(' t(s)		X(m)		Y(m)		Z(m)\n')
outStream.write('NUMBER_OF_DATAPOINTS: 			%s\n' % len(container['orbitTime']))
outStream.write('\n')

for i in range(len(container['orbitTime'])):
    outStream.write(' %s %s %s %s\n' % (hms2sec(container['orbitTime'][i].split('T')[1]),\
                                  container['orbitX'][i],\
                                  container['orbitY'][i],\
                                  container['orbitZ'][i]))

outStream.write('')
outStream.write('*******************************************************************\n')
outStream.write('* End_precise_orbits:_NORMAL\n')
outStream.write('*******************************************************************\n')
outStream.write('\n')
outStream.write('    Current time: %s\n' % time.asctime())
outStream.write('\n')

# close output file
#outStream.close()

