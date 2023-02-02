'''
Created by: Anurag Kulshrestha
Date Created: 20-01-2021
Last modified: 25-07-2022
'''

import sys, os
from paz_parameters import PazParameters
from grs_profile import GRS_Profile
from stack import StackData

'''
TODO 1. del_unpacked_image
TODO 2. Check for new images

''' 

class PAZ_InSAR(object):
    def run(self, process_par_path, start_date, end_date, master_date):
        print('PAZ processing start')
        processing_Params = PazParameters(process_par_path)
        
        profile = GRS_Profile(processing_Params.profile_log + '_' + str(processing_Params.nr_of_jobs), processing_Params.verbose)
        
        # The shapefile to select the area of interest. You can easily find a shapefile countries or regions on the internet.
        # For example via diva-gis.org. Shapefile for the Netherlands can be found in the same folder under shapes.
        shape_dat = processing_Params.shape_dat 
        
        # The folder where SLC images from a specific track are stored. This data will be used as input for the script
        track_dir = processing_Params.archive_path

        # This is the output folder.
        stack_path = processing_Params.stack_path
        
        
        # Here the doris inputfiles are stored. (Comes with the python scripts)
        input_files = processing_Params.input_files  #'/......'
        
        profile.log_time_stamp('start')
        
        stack = StackData(track_dir, start_date, end_date, shape_dat, output_path = stack_path)
        
        stack.select_image()
        
        #TODO check new images
        stack.unpack_image()
        
        stack.dump_header2doris(write_path = stack_path, overwrite=False)
        
        stack.dump_paz_data()
        
        stack.create_master_link(master_date=master_date, stack_path= stack_path)
        
        profile.log_time_stamp('stack preparation finished')
        
        #TODO
        #stack.del_unpacked_image()
        if(processing_Params.do_oversample):
            stack.do_oversample(input_files_path = input_files, master_date=master_date, stack_path= stack_path)
            profile.log_time_stamp('do_oversample finished')
            stack.create_master_ovs_link(master_date=master_date, stack_path= stack_path)
            profile.log_time_stamp('master ovs linking finished')
        
        if(processing_Params.do_coarse_orbits):
            stack.coarse_orbits(input_files_path = input_files)
            profile.log_time_stamp('coarse_orbits finished')
        
        if(processing_Params.do_coarse_corr):
            stack.coarse_corr(input_files_path = input_files)
            profile.log_time_stamp('coarse_corr finished')
        
        if(processing_Params.do_fine_coreg):
            stack.fine_corr(input_files_path = input_files)
            profile.log_time_stamp('fine_coreg finished')
        
        if(processing_Params.do_fake_fine_coreg):
            stack.fake_fine_corr()
            profile.log_time_stamp('fake_fine_coreg finished')
        
        if(processing_Params.do_dac):
            stack.dem_assist(input_files_path= input_files)
            profile.log_time_stamp('do_dac finished')
            #stack.del_files(['dac_delta_demline.temp','dac_delta_dempixel.temp','dac_delta_line.raw', 'dac_delta_pixel.raw', 'dac_m_demline.temp','dac_m_dempixel.temp'])
        
        if(processing_Params.do_coregpm):
            stack.coregpm(input_files_path = input_files)
            profile.log_time_stamp('do_coregpm finished')
        
        if(processing_Params.do_fake_coreg):
            stack.fake_coregpm()
            profile.log_time_stamp('fake_coregpm finished')
        
        if(processing_Params.do_resample):
            stack.resample(input_files_path = input_files)
            #stack.del_ext_resample()
            profile.log_time_stamp('resample finished')
        
        if(processing_Params.do_del_ext_resample_files):
            #stack.del_ext_resample()
            stack.del_files(['slave.raw', 'dac_delta_demline.temp','dac_delta_dempixel.temp','dac_delta_line.raw', 'dac_delta_pixel.raw', 'dac_m_demline.temp','dac_m_dempixel.temp','rsmp_orig_slave_line.raw','rsmp_orig_slave_pixel.raw'])
            profile.log_time_stamp('deleted extra files finished')
        
        if(processing_Params.do_interferogram):
            stack.interferogram(input_files_path = input_files)
            profile.log_time_stamp('interferogram finished')
        #sys.exit()
        if(processing_Params.do_compref_phase):
            stack.comp_ref_phase(input_files_path = input_files)
            profile.log_time_stamp('comp_ref_phase finished')
        
        if(processing_Params.do_ref_phase):
            stack.subt_ref_phase(input_files_path = input_files)
            profile.log_time_stamp('subt_ref_phase finished')
        
        if(processing_Params.do_del_c_int):
            #stack.del_c_int()
            stack.del_files(['cint.raw'])
            profile.log_time_stamp('deleted c_int finished')
        
        if(processing_Params.do_compref_dem):
            stack.comp_ref_dem(input_files_path = input_files)
            profile.log_time_stamp('comp_ref_dem finished')
        
        if(processing_Params.do_ref_dem):
            stack.subt_ref_dem(input_files_path = input_files)
            profile.log_time_stamp('subt_ref_dem finished')
        
        if(processing_Params.do_coherence):
            stack.coherence(input_files_path = input_files)
            profile.log_time_stamp('coherence finished')



