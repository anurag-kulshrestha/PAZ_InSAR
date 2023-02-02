from grs_config import GrsConfig
import xml.etree.ElementTree as ET
import os, sys

class PazParameters():
    '''
    Reads the parameters
    '''
    
    def __init__(self, processing_path):
        grs_config = GrsConfig()
        self.doris_path = grs_config.doris_path
        self.cpxfiddle_path = grs_config.cpxfiddle_path
        self.paz_function_path = grs_config.paz_function_path
        self.job_handler_script = grs_config.job_handler_script
        
        tree = ET.parse(os.path.join(processing_path, 'paz_input.xml'))
        self.settings = tree.getroot()
        
        self.shape_dat = self._settings_get('.shape_file_path')
        archive_path = self._settings_get('.sar_data_folder')
        self.archive_path = archive_path
        project_path = self._settings_get('.datastack_folder')
        
        self.polarization = self._settings_get('.polarization').upper()
        self.project_path = project_path
        
        self.verbose = True
        
        self.stack_path = os.path.join(project_path, 'stack')
        self.input_files = os.path.join(project_path, 'input_files')
        
        self.parallel = self._settings_compare('.parallel', 'yes')
        self.nr_of_jobs = int(self._settings_get('.cores'))
        
        self.profile_log = project_path + '/profile_log'
        self.doris_parallel_flag_dir = project_path + '/.Paz_parallel'
        self.between_sleep_time = 1
        self.end_sleep_time = 1
        self.source_path = grs_config.paz_function_path
        self.do_crop = self._settings_compare('.do_crop', 'yes')
        
        self.crop_l0 = int(self._settings_get('.crop_l0'))
        self.crop_lN = int(self._settings_get('.crop_lN'))
        self.crop_p0 = int(self._settings_get('.crop_p0'))
        self.crop_pN = int(self._settings_get('.crop_pN'))
        
        self.do_oversample = self._settings_compare('.do_oversample', 'yes')
        self.do_coarse_orbits = self._settings_compare('.do_coarse_orbits', 'yes')
        self.do_coarse_corr = self._settings_compare('.do_coarse_corr', 'yes')
        self.do_fake_fine_coreg = self._settings_compare('.do_fake_fine_coreg', 'yes')
        self.do_fine_coreg = self._settings_compare('.do_fine_coreg', 'yes')
        self.do_dac = self._settings_compare('.do_dac', 'yes')
        self.do_fake_coreg = self._settings_compare('.do_fake_coreg', 'yes')
        self.do_coregpm = self._settings_compare('.do_coregpm', 'yes')
        
        self.do_resample = self._settings_compare('.do_resample', 'yes')
        self.do_del_ext_resample_files = self._settings_compare('.do_del_ext_resample_files', 'yes')
        
        self.do_interferogram = self._settings_compare('.do_interferogram', 'yes')
        self.do_compref_phase = self._settings_compare('.do_compref_phase', 'yes')
        self.do_del_c_int = self._settings_compare('.do_del_c_int', 'yes')
        self.do_compref_dem = self._settings_compare('.do_compref_dem', 'yes')
        self.do_ref_phase = self._settings_compare('.do_ref_phase', 'yes')
        self.do_ref_dem = self._settings_compare('.do_ref_dem', 'yes')
        self.do_coherence = self._settings_compare('.do_coherence', 'yes')
    
    def _check_path_exists(self, path):
        if not(os.path.exists(path)):
            print('Error Doris_Parameters: path ' + path + ' does not exist')
            
    def _settings_get(self, string):
        return self.settings.find('*/' + string).text


    def _settings_compare(self, string, comp_string):
        if (self.settings.find('*/' + string).text.lower()==comp_string.lower()):
            return True
        return False
