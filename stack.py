# This script gathers available sentinel files from the database and checks the coverage in space and time for this data
# stack.

import os, sys
import warnings
from collections import Counter, OrderedDict
from datetime import datetime
import shutil
import numpy as np
from load_shape_unzip import load_shape, extract_kml_preview, shape_im_kml, unzip_folder
import image
from paz_parameters import PazParameters
from doris.doris_stack.main_code.resdata import ResData
from doris.doris_stack.main_code.jobs import Jobs
import xml.etree.ElementTree as ET

class StackData(object):
    
    def __init__(self, track_dir, start_date, end_date, shape_dat, output_path, buffer=0.02):
        
        Jobs.id = 0
        
        self.dates = list()
        self.shape = ''
        self.shape_filename = shape_dat
        self.path = output_path
        self.image_dump = []
        self.images=[]
        self.image_dates=[]
        self.image_files = []
        #self.image_cos_files_in_xml = []
        self.buffer = buffer 
        self.datastack={}
        
        self.master_date = []
        
        paz_parameters = PazParameters(os.path.dirname(self.path))
        self.paz_parameters = paz_parameters
        self.paz_function_path = paz_parameters.paz_function_path
        self.polarization = paz_parameters.polarization
        
        self.nr_of_jobs = paz_parameters.nr_of_jobs
        self.parallel = paz_parameters.parallel
        
        #check if data path exists
        if not track_dir or not os.path.exists(track_dir):
            warnings.warn('This function needs an existing path as input!')
            return
        
        self.search_files(track_dir)
        #if shape:
        self.create_shape(shape_dat,buffer)
        
        #convert dates to datetime
        if end_date:
            self.end_date = np.datetime64(end_date).astype('datetime64[s]') + np.timedelta64(1, 'D').astype('timedelta64[s]')
        else:
            self.end_date = np.datetime64('now').astype('datetime64[s]')
        self.start_date = np.datetime64(start_date).astype('datetime64[s]')
        
        #output path
        if not output_path:
            warnings.warn('You did not specify an output path. Please do so later on using the add_path function')
        else:
            self.add_path(output_path)
            
    def add_path(self,path):
        # This function adds the output path.

        if os.path.isdir(path):
            self.path = path
        elif os.path.isdir(os.path.dirname(path[:-1])):
            os.mkdir(path)
            self.path = path
            
        else:
            warnings.warn('Neither the directory itself nor the parents directory exists. Choose another path.')
    
    def search_files(self, track_dir):
        # This function searches for files within a certain folder. This folder should contain images from the same
        # track. These images are added to the variable image dump.
        images = list()

        top_dir = next(os.walk(track_dir))
        
        for data in top_dir[2]:
            if data.endswith('.tar.gz'):
                images.append(os.path.join(track_dir, data))
        for data in top_dir[1]:
            if data[:3]=='PAZ':
                images.append(os.path.join(track_dir, data))
        
        if images:
            images = sorted(images)
        else:
            warnings.warn('No images found! Please choose another data folder. Track_dir = ' + str(track_dir))
        
            
        base = []  # Remove double hits because data is already unzipped.
        for i in images: # Drop all .zip files which are unpacked already.
            if i.endswith('.tar.gz'):
                base.append(os.path.basename(i[:-7]))
            elif i.split('/')[-1][:3]=='PAZ':
                base.append(os.path.basename(i))
        b, id = np.unique(base, return_index=True)
        
        rem = []
        for i in range(len(base)):
            if i in id:
                self.image_dump.append(images[i])
            else:
                rem.append(images[i])
        if rem:
            print('removed the following zip files from stack:')
            for r in rem:
                print(r)
            print('It is advised to work with zipfiles instead of unpacked data. This saves diskspace and will ')
    
    def create_shape(self,shape_dat,buffer=0.02):
        # This function creates a shape to make a selection of usable bursts later on. Buffer around shape is in
        # degrees.

        self.shape = load_shape(shape_dat, buffer)
        
    
    
    def select_image(self, start_date='',end_date='', dest_folder=''):
        if not dest_folder:
            dest_folder = os.path.join(self.path, 'kml')
        if not os.path.exists(dest_folder):
            os.makedirs(dest_folder)
        
        if not self.shape:
            warnings.warn('There is no shape loaded to select images. Please use the create_shape function to do so.')
        
        if start_date:
            self.start_date = np.datetime64(start_date).astype('datetime64[s]')
        if end_date:
            self.end_date = np.datetime64(end_date).astype('datetime64[s]') + np.timedelta64(1, 'D').astype('timedelta64[s]')
        
        # First select images based on dates and check if polygons intersect.
        for i in self.image_dump:
            d = os.path.basename(i)[28:43]
            
            acq_time = np.datetime64(d[0:4] + '-' + d[4:6] + '-' + d[6:11] + ':' + d[11:13] + ':' + d[13:] + '-0000')

            if acq_time >= self.start_date and acq_time <= self.end_date:
                im = image.ImageMeta(path=i)
                
                xml, kml, tif = extract_kml_preview(i, dir=dest_folder, png=False, overwrite=False)
                
                if shape_im_kml(self.shape, kml):
                    tree = ET.parse(xml)
                    root = tree.getroot()
                    
                    im.cos_input_file = [i.text for i in root.findall('productComponents/imageData/file/location/filename') if i.text[6:8]==self.polarization][0]
                    
                    self.images.append(im)
                    self.image_dates.append(acq_time)
                    self.image_files.append(os.path.basename(i))
                    
                    
                    
        self.dates = sorted(list(set([d.astype('datetime64[D]') for d in self.image_dates])))
        for date in self.dates:
            print(date)
    
    
    def unpack_image(self, dest_folder=''):

        if not dest_folder:
            dest_folder = os.path.join(self.path, 'slc_data_files')
            self.unzip_path = dest_folder
        if not os.path.exists(dest_folder):
            os.mkdir(dest_folder)
            
        jobList1 = []
        
        for imagefile in self.images:

            tarred_folder = imagefile.zip_path
            
            if tarred_folder.endswith('.tar.gz'):
                base_name = os.path.basename(tarred_folder)[:-7]
                first_folder_name = base_name[:13]+'_____'+base_name[18:-4]
                imagefile.unzip_path = os.path.join(dest_folder, first_folder_name)
                imagefile.cos_file = os.path.join(dest_folder, first_folder_name + '.cos')
                imagefile.xml_file = os.path.join(dest_folder, first_folder_name+'.xml')
                #cos_file_name, xml_file_name = unzip_folder(tarred_folder, dest_folder, overwrite=False)
                #imagefile.cos_file = cos_file_name
                #imagefile.xml_file = xml_file_name
            overwrite = False
            command1 = 'python3 ' +self.paz_function_path+ 'load_shape_unzip.py '+ tarred_folder + ' ' + dest_folder + ' ' + str(overwrite) + ' ' + imagefile.cos_input_file
            
            jobList1.append({"path": self.path, "command": command1})
            if not self.parallel:
                os.chdir(self.path)
                # Resample
                os.system(command1)
        if self.parallel:
            jobs = Jobs(self.nr_of_jobs, self.paz_parameters)
            jobs.run(jobList1)
                
        
            
    def dump_header2doris(self, write_path, overwrite=False):
        #create folders in the stack dir
        if write_path and os.path.exists(write_path):
            self.path = write_path
        if (not write_path or not os.path.exists(write_path)) and not self.path:
            warnings.warn('Please specify a path that exists to write the data')
            return
        
        for imagefile, date in zip(self.images, self.dates):
            date = date.astype(datetime).strftime('%Y-%m-%d')
            date_basic = date.replace('-','')
            date_path = os.path.join(self.path, date_basic)
            #imagefile
            if not os.path.exists(date_path):
                os.mkdir(date_path)
            
            imagefile.date_path = date_path
            self.datastack[date_basic] = {}
            self.datastack[date_basic]['path'] = date_path
            #self.datastack[date_basic]['path'] = date_path
            
        jobList1 = []
        for imagefile in self.images:
            res_name = os.path.join(imagefile.date_path, 'slave.res')
            if not os.path.isfile(res_name) or overwrite==True:
                command1 = 'python3 '+self.paz_function_path+ 'paz_dump_header2doris.py '+ imagefile.xml_file + ' ' + res_name
                jobList1.append({"path": self.path, "command": command1})
                #print('aaya')
        
            if not self.parallel:
                os.chdir(self.path)
                # Resample
                os.system(command1)
        if self.parallel:
            jobs = Jobs(self.nr_of_jobs, self.paz_parameters)
            jobs.run(jobList1)
            
    
    def dump_paz_data(self):
        #TODO add cropping option
        jobList1 = []
        for imagefile in self.images:
            cos_file = imagefile.cos_file
            res_name = os.path.join(imagefile.date_path, 'slave.res')
            output_filename = os.path.join(imagefile.date_path, 'slave.raw')
            if not os.path.isfile(output_filename):
                if self.paz_parameters.do_crop:
                    l0 = self.paz_parameters.crop_l0
                    lN = self.paz_parameters.crop_lN
                    p0 = self.paz_parameters.crop_p0
                    pN = self.paz_parameters.crop_pN
                    command1 = 'python3 '+self.paz_function_path+ 'paz_dump_data.py '+ cos_file +' '+ output_filename +' ' +str(l0) +' ' +str(lN) +' ' +str(p0) +' ' +str(pN) +' -res ' + res_name
                else:
                    command1 = 'python3 '+self.paz_function_path+ 'paz_dump_data.py '+ cos_file +' '+ output_filename + ' -res ' + res_name
                jobList1.append({"path": self.path, "command": command1})
                
            if not self.parallel:
                os.chdir(self.path)
                # Resample
                os.system(command1)
        if self.parallel:
            jobs = Jobs(self.nr_of_jobs, self.paz_parameters)
            jobs.run(jobList1)
            
    def create_master_link(self, master_date, stack_path):
        
        master_date_basic = master_date.replace('-','')
        master_path = os.path.join(stack_path, master_date_basic)
        #remove master from processing dirs
        self.datastack.pop(master_date_basic, None)
        #for symlink
        m_source = os.path.join(master_path, 'slave.raw')
        master_res = os.path.join(master_path, 'slave.res')
        
        for date in self.datastack.keys():
            #print(self.datastack[date]['path'])
            m_dest = os.path.join(self.datastack[date]['path'], 'master.raw')
            if not os.path.exists(m_dest):
                os.symlink(m_source, m_dest)
            
            slv_master_res = os.path.join(self.datastack[date]['path'], 'master.res')
            if not os.path.exists(slv_master_res):
                os.system('cp '+ master_res +' ' +slv_master_res)
                res = ResData(slv_master_res)
                res.processes['crop']['Data_output_file'] = 'master.raw'
                res.write(new_filename = slv_master_res)
    
    def del_unpacked_image(self):
        for imagefile in self.images:
            if os.path.exists(imagefile.cos_file):
                shutil.rmtree(imagefile.cos_file)
    
    
    def do_oversample(self, input_files_path, master_date, stack_path):
        jobList1 = []
        for date in self.datastack.keys():
            slv_res = os.path.join(self.datastack[date]['path'], 'slave.res')
            res = ResData(slv_res)
            
            if not res.process_control['oversample'] == '1':
                path = self.datastack[date]['path']
                command1 = 'doris '+ os.path.join(input_files_path, 'input.oversample')
                jobList1.append({"path": path, "command": command1})
                
            if not self.parallel:
                os.chdir(path)
                os.system(command1)
        #oversample master
        master_date_basic = master_date.replace('-','')
        master_path = os.path.join(stack_path, master_date_basic)
        master_slv_res = os.path.join(master_path, 'slave.res')
        res = ResData(master_slv_res)
        if not res.process_control['oversample'] == '1':
            path = master_path
            command1 = 'doris '+ os.path.join(input_files_path, 'input.oversample')
            jobList1.append({"path": path, "command": command1})
        if not self.parallel:
            os.chdir(path)
            os.system(command1)
            
            
        if self.parallel:
            jobs = Jobs(self.nr_of_jobs, self.paz_parameters)
            jobs.run(jobList1)
    
    def create_master_ovs_link(self, master_date, stack_path):
        
        master_date_basic = master_date.replace('-','')
        master_path = os.path.join(stack_path, master_date_basic)
        
        #for symlink
        m_ovs_source = os.path.join(master_path, 'slave_ovs.raw')
        master_res = os.path.join(master_path, 'slave.res')
        master_res_obj = ResData(master_res)
        for date in self.datastack.keys():
            #print(self.datastack[date]['path'])
            m_dest = os.path.join(self.datastack[date]['path'], 'master_ovs.raw')
            if not os.path.exists(m_dest):
                os.symlink(m_ovs_source, m_dest)
            
            slv_master_res = os.path.join(self.datastack[date]['path'], 'master.res')
            slv_master_res_obj = ResData(slv_master_res)
            
            if not slv_master_res_obj.process_control['oversample'] == '1':
                os.system('yes | cp -rf '+ master_res +' ' +slv_master_res)
                slv_master_res_obj = ResData(slv_master_res)
                #over_sample = master_res_obj.process_reader('oversample')
                #slv_master_res_obj.insert(over_sample, 'oversample')
                slv_master_res_obj.processes['crop']['Data_output_file'] = 'master.raw'
                slv_master_res_obj.processes['oversample']['Data_output_file'] = 'master_ovs.raw'
                slv_master_res_obj.write(new_filename = slv_master_res)
    
    def del_files(self, file_list):
        jobList1=[]
        for date in self.datastack.keys():
            path = self.datastack[date]['path']
            for del_file in file_list:
                if(os.path.exists(os.path.join(path, del_file))):
                    command = 'rm '+ os.path.join(path, del_file)
                    jobList1.append({"path": path, "command": command})
                if not self.parallel:
                    os.chdir(path)
                    # Resample
                    os.system(command1)
        if self.parallel:
            jobs = Jobs(self.nr_of_jobs, self.paz_parameters)
            jobs.run(jobList1)
    
    
    def coarse_orbits(self, input_files_path):
        #cmds=[]
        for date in self.datastack.keys():
            ifg_res = os.path.join(self.datastack[date]['path'], 'ifgs.res')
            res = ResData(ifg_res)
            if not os.path.exists(ifg_res):
                #print('aaya')
                os.chdir(self.datastack[date]['path'])
                os.system('doris '+ os.path.join(input_files_path, 'input.coarseorb'))
            elif not res.process_control['coarse_orbits'] == '1':
                #print('aaya')
                os.chdir(self.datastack[date]['path'])
                os.system('doris '+ os.path.join(input_files_path, 'input.coarseorb'))
            else:
                pass
    
    
    def coarse_corr(self, input_files_path):
        jobList1 = []
        for date in self.datastack.keys():
            ifg_res = os.path.join(self.datastack[date]['path'], 'ifgs.res')
            res = ResData(ifg_res)
            
            if not res.process_control['coarse_correl'] == '1':
                path = self.datastack[date]['path']
                command1 = 'doris '+ os.path.join(input_files_path, 'input.coarsecorr')
                jobList1.append({"path": path, "command": command1})
                
            if not self.parallel:
                os.chdir(path)
                # Resample
                os.system(command1)
        if self.parallel:
            jobs = Jobs(self.nr_of_jobs, self.paz_parameters)
            jobs.run(jobList1)
    
    def fine_corr(self, input_files_path):
        jobList1 = []
        for date in self.datastack.keys():
            ifg_res = os.path.join(self.datastack[date]['path'], 'ifgs.res')
            res = ResData(ifg_res)
            
            if not res.process_control['fine_coreg'] == '1':
                path = self.datastack[date]['path']
                command1 = 'doris '+ os.path.join(input_files_path, 'input.finecoreg')
                jobList1.append({"path": path, "command": command1})
                
            if not self.parallel:
                os.chdir(path)
                # Resample
                os.system(command1)
        if self.parallel:
            jobs = Jobs(self.nr_of_jobs, self.paz_parameters)
            jobs.run(jobList1)
    
    
    def fake_fine_corr(self):
        
        coreg = OrderedDict()
        coreg['Initial offsets (l,p)'] = '0, 0'
        coreg['Window_size_L_for_correlation'] = '64'
        coreg['Window_size_P_for_correlation'] = '64'
        coreg['Max. offset that can be estimated'] = '32'
        coreg['Peak search ovs window (l,p)'] = '16 , 16'
        coreg['Oversampling factor'] = '32'
        coreg['Number_of_correlation_windows'] = '0'
        
        for date in self.datastack.keys():
            ifg_res = os.path.join(self.datastack[date]['path'], 'ifgs.res')
            res = ResData(ifg_res)
            
            #os.chdir(self.datastack[date]['path'])
            #os.system('/home/anurag/Documents/PhDProject/doris/bin/doris.rmstep.sh fine_coreg ifgs.res')
            #continue
            if not res.process_control['fine_coreg'] == '1':
                res.insert(coreg,'fine_coreg')
                res.write(new_filename = ifg_res)
    
    def dem_assist(self, input_files_path):
        jobList1 = []
        for date in self.datastack.keys():
            ifg_res = os.path.join(self.datastack[date]['path'], 'ifgs.res')
            res = ResData(ifg_res)
            if not res.process_control['dem_assist'] == '1':
                path = self.datastack[date]['path']
                command1 = 'doris '+ os.path.join(input_files_path, 'input.dembased')
                jobList1.append({"path": path, "command": command1})
                
            if not self.parallel:
                os.chdir(path)
                # Resample
                os.system(command1)
        if self.parallel:
            jobs = Jobs(self.nr_of_jobs, self.paz_parameters)
            jobs.run(jobList1)
    
    def coregpm(self, input_files_path):
        jobList1 = []
        for date in self.datastack.keys():
            ifg_res = os.path.join(self.datastack[date]['path'], 'ifgs.res')
            res = ResData(ifg_res)
            
            if not res.process_control['comp_coregpm'] == '1':
                path = self.datastack[date]['path']
                command1 = 'doris '+ os.path.join(input_files_path, 'input.coregpm')
                jobList1.append({"path": path, "command": command1})
                
            if not self.parallel:
                os.chdir(path)
                # Resample
                os.system(command1)
        if self.parallel:
            jobs = Jobs(self.nr_of_jobs, self.paz_parameters)
            jobs.run(jobList1)
    
    
    
    def fake_coregpm(self):
        
        coreg = OrderedDict()
        coreg['Degree_cpm'] = '0'
        coreg['Normalization_Lines'] = ''
        coreg['Normalization_Pixels'] = ''
        coreg['Estimated_coefficientsL'] = ''
        coreg['row_0'] = ["{0:.8e}".format(0), '0', '0']
        coreg['Estimated_coefficientsP'] = ''
        coreg['row_1'] = ["{0:.8e}".format(0), '0', '0']

        coreg['Deltaline_slave00_poly'] = "{0:.8e}".format(0)
        coreg['Deltapixel_slave00_poly'] = "{0:.8e}".format(0)
        coreg['Deltaline_slave0N_poly'] = "{0:.8e}".format(0)
        coreg['Deltapixel_slave0N_poly'] = "{0:.8e}".format(0)
        coreg['Deltaline_slaveN0_poly'] = "{0:.8e}".format(0)
        coreg['Deltapixel_slaveN0_poly'] = "{0:.8e}".format(0)
        coreg['Deltaline_slaveNN_poly'] = "{0:.8e}".format(0)
        coreg['Deltapixel_slaveNN_poly'] = "{0:.8e}".format(0)
        
        for date in self.datastack.keys():
            ifg_res_file = os.path.join(self.datastack[date]['path'], 'ifgs.res')
            mas_res_file = os.path.join(self.datastack[date]['path'], 'master.res')
            
            ifg_res = ResData(ifg_res_file)
            mas_res = ResData(mas_res_file)
            
            lines = (int(mas_res.processes['crop']['Last_line (w.r.t. original_image)']) -
                         int(mas_res.processes['crop']['First_line (w.r.t. original_image)']))
            pixels = (int(mas_res.processes['crop']['Last_pixel (w.r.t. original_image)']) -
                        int(mas_res.processes['crop']['First_pixel (w.r.t. original_image)']))

            # Save pixels lines
            coreg['Normalization_Lines'] = "{0:.8e}".format(1) + ' ' + "{0:.8e}".format(lines)
            coreg['Normalization_Pixels'] = "{0:.8e}".format(1) + ' ' + "{0:.8e}".format(pixels)

            # Copy coregistration from full swath to burst
            if not ifg_res.process_control['comp_coregpm'] == '1':
                ifg_res.insert(coreg,'comp_coregpm')
                ifg_res.write(new_filename = ifg_res_file)
    
    
    def resample(self, input_files_path):
        jobList1=[]
        for date in self.datastack.keys():
            slv_res = os.path.join(self.datastack[date]['path'], 'slave.res')
            res = ResData(slv_res)
            
            #os.chdir(self.datastack[date]['path'])
            #os.system('/home/anurag/Documents/PhDProject/doris/bin/doris.rmstep.sh resample slave.res')
            
            if not res.process_control['resample'] == '1':
                path = self.datastack[date]['path']
                command1 = 'doris '+ os.path.join(input_files_path, 'input.resample')
                jobList1.append({"path": path, "command": command1})
                
            if not self.parallel:
                os.chdir(path)
                # Resample
                os.system(command1)
        if self.parallel:
            jobs = Jobs(self.nr_of_jobs, self.paz_parameters)
            jobs.run(jobList1)

    def interferogram(self, input_files_path):
        jobList1=[]
        for date in self.datastack.keys():
            ifg_res = os.path.join(self.datastack[date]['path'], 'ifgs.res')
            res = ResData(ifg_res)
            if not res.process_control['interfero'] == '1':
                path = self.datastack[date]['path']
                command1 = 'doris '+ os.path.join(input_files_path, 'input.interferogram')
                jobList1.append({"path": path, "command": command1})
                
            if not self.parallel:
                os.chdir(path)
                # Resample
                os.system(command1)
        if self.parallel:
            jobs = Jobs(self.nr_of_jobs, self.paz_parameters)
            jobs.run(jobList1)
            
    def comp_ref_phase(self, input_files_path):
        jobList1=[]
        for date in self.datastack.keys():
            ifg_res = os.path.join(self.datastack[date]['path'], 'ifgs.res')
            res = ResData(ifg_res)
            if not res.process_control['comp_refphase'] == '1':
                path = self.datastack[date]['path']
                command1 = 'doris '+ os.path.join(input_files_path, 'input.comprefpha')
                jobList1.append({"path": path, "command": command1})
                
            if not self.parallel:
                os.chdir(path)
                # Resample
                os.system(command1)
        if self.parallel:
            jobs = Jobs(self.nr_of_jobs, self.paz_parameters)
            jobs.run(jobList1)
            
    def subt_ref_phase(self, input_files_path):
        jobList1=[]
        for date in self.datastack.keys():
            ifg_res = os.path.join(self.datastack[date]['path'], 'ifgs.res')
            res = ResData(ifg_res)
            if not res.process_control['subtr_refphase'] == '1':
                path = self.datastack[date]['path']
                command1 = 'doris '+ os.path.join(input_files_path, 'input.subtrrefpha')
                jobList1.append({"path": path, "command": command1})
                
            if not self.parallel:
                os.chdir(path)
                # Resample
                os.system(command1)
        if self.parallel:
            jobs = Jobs(self.nr_of_jobs, self.paz_parameters)
            jobs.run(jobList1)
            
    def comp_ref_dem(self, input_files_path):
        jobList1=[]
        for date in self.datastack.keys():
            ifg_res = os.path.join(self.datastack[date]['path'], 'ifgs.res')
            res = ResData(ifg_res)
            if not res.process_control['comp_refdem'] == '1':
                path = self.datastack[date]['path']
                command1 = 'doris '+ os.path.join(input_files_path, 'input.comprefdem')
                jobList1.append({"path": path, "command": command1})
                
            if not self.parallel:
                os.chdir(path)
                # Resample
                os.system(command1)
        if self.parallel:
            jobs = Jobs(self.nr_of_jobs, self.paz_parameters)
            jobs.run(jobList1)
            
    def subt_ref_dem(self, input_files_path):
        jobList1=[]
        for date in self.datastack.keys():
            ifg_res = os.path.join(self.datastack[date]['path'], 'ifgs.res')
            res = ResData(ifg_res)
            if not res.process_control['subtr_refdem'] == '1':
                path = self.datastack[date]['path']
                command1 = 'doris '+ os.path.join(input_files_path, 'input.subtrrefdem')
                jobList1.append({"path": path, "command": command1})
                
            if not self.parallel:
                os.chdir(path)
                # Resample
                os.system(command1)
        if self.parallel:
            jobs = Jobs(self.nr_of_jobs, self.paz_parameters)
            jobs.run(jobList1)

    def coherence(self, input_files_path):
        jobList1=[]
        for date in self.datastack.keys():
            ifg_res = os.path.join(self.datastack[date]['path'], 'ifgs.res')
            res = ResData(ifg_res)
            if not res.process_control['coherence'] == '1':
                path = self.datastack[date]['path']
                command1 = 'doris '+ os.path.join(input_files_path, 'input.coherence')
                jobList1.append({"path": path, "command": command1})
                
            if not self.parallel:
                os.chdir(path)
                # Resample
                os.system(command1)
        if self.parallel:
            jobs = Jobs(self.nr_of_jobs, self.paz_parameters)
            jobs.run(jobList1)
