import argparse
import os
import xml.etree.ElementTree as ET
import sys
sys.path.append('/home/anurag/Documents/PhDProject/')
#sys.path
from Paz_InSAR import PAZ_InSAR
#from doris_sentinel_1 import DorisSentinel1 

"""Doris processing
argument:  --parameterfilepath, -p
"""

# parse arguments here
parser = argparse.ArgumentParser(description='Paz processing.')
parser.add_argument('--parameterfilepath', '-p', default='./',
                    help='Path to dorisParameter.py file, this file contains case specific parameters')

args = parser.parse_args()

xml_file = os.path.join(os.path.join(args.parameterfilepath, 'paz_input.xml'))
print('Reading ' + xml_file)
tree = ET.parse(xml_file)
settings = tree.getroot()[0]

start_date = settings.find('.start_date').text
end_date = settings.find('.end_date').text
master_date = settings.find('.master_date').text

#start doris sentinel1 run
paz_insar = PAZ_InSAR()
paz_insar.run(args.parameterfilepath, start_date, end_date, master_date)
