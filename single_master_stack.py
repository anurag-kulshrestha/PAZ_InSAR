import os
import numpy as np
from datetime import datetime
from collections import OrderedDict
import copy
from copy import deepcopy
from doris.doris_stack.main_code.resdata import ResData
#from doris.doris_stack.main_code.dorisparameters import DorisParameters
import collections
#from jobs import Jobs
#from doris.doris_stack.functions.baselines import baselines

class SingleMaster(object):

    def __init__(self, start_date='', end_date='', master_date='', stack_folder='', processing_folder='',
                 input_files=''):
        # This function loads in a datastack to create a single master stack. Optional are the start date, end date and
        # master date. If they are not defined all dates will be loaded. The master date can be loaded later using the
        # master function. If you want a random master value, choose master_date='random'
        # Dates should be given as 'yyyy-mm-dd'. If stack_read is True information is read from the stack_folder. Otherwise
        # the datastack from an StackData object should be given as input.

        #Jobs.id = 0

        doris_parameters = DorisParameters(os.path.dirname(processing_folder)) # (assuming it is stored in the stackfolder
        self.doris_parameters = doris_parameters
        
        if not start_date:
            self.start_date = doris_parameters.start_date_default
        else:
            self.start_date = start_date
        if not end_date:
            self.end_date = doris_parameters.end_date_default
        else:
            self.end_date = end_date
            
        
