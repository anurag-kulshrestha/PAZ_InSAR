import numpy as np
import xml.etree.ElementTree as ET
import os, sys
import struct
import gdal
import matplotlib.pyplot as plt

def read_meta_data(meta_file_name):
    tree = ET.parse(meta_file_name)
    root = tree.getroot()
    #print([i for i in root])
    
def read_COSAR(file_name):
    return gdal.Open(file_name)
    
def plot_array(arr, clip_extremes=True, clip_min_percentile=1, clip_max_percentile=99):
    #clipping
    if clip_extremes==True:
        p_min, p_max = np.percentile(arr, [clip_min_percentile,clip_max_percentile])
        arr = np.clip(arr, p_min, p_max)
    #plotting
    plt.imshow(arr, cmap = 'gray')

    plt.colorbar()
    #plt.show()


if __name__=='__main__':
    #a=1
    base_dir = '/media/anurag/Data/Ubuntu_MSI_backup/Documents/PhDProject/PAZSatelliteData'
    master_base_dir = os.path.join(base_dir, 'PAZ1_SAR__SSC____3_SM_S_SRA_20191006T055119_20191006T055126_001/PAZ1_SAR__SSC______SM_S_SRA_20191006T055119_20191006T055126')
    slave_base_dir = os.path.join(base_dir, 'PAZ1_SAR__SSC____3_SM_S_SRA_20191028T055119_20191028T055126_001/PAZ1_SAR__SSC______SM_S_SRA_20191028T055119_20191028T055126')
    
    mas_paz_data_dir = os.path.join(master_base_dir, 'IMAGEDATA')
    slv_paz_data_dir = os.path.join(slave_base_dir, 'IMAGEDATA')

    data_file_name = 'IMAGE_VV_SRA_strip_009.cos'
    #meta_file_name = 'PAZ1_SAR__SSC______SM_S_SRA_20191006T055119_20191006T055126.xml'
    #rows, cols = 26370, 20460
    print(os.path.join(slv_paz_data_dir, data_file_name))
    slv_arr = read_COSAR(os.path.join(slv_paz_data_dir, data_file_name)).ReadAsArray()[8000:12000, 10000:20000] # Enschede
    mas_arr = read_COSAR(os.path.join(mas_paz_data_dir, data_file_name)).ReadAsArray()[8000:12000, 10000:20000] # Enschede
    
    #img_arr = np.flip(img_arr, axis=1)
    
    #plot_array(np.absolute(img_arr))
    plt.subplot(121)
    plt.imshow(10*np.log10(np.absolute(mas_arr)), cmap='gray')
    plt.title('Master (20191006)')

    plt.subplot(122)
    plt.imshow(10*np.log10(np.absolute(slv_arr)), cmap='gray')
    plt.title('Slave (20191028)')
    plt.colorbar()
    plt.show()

#def read_SLC(file_name, scan_lines, scan_pix, cropping_list=[.1,.55,.57,.72], is_List_Ratio=True):
    
    
    ##cropping_list=[extent_xmin,extent_xmax, extent_ymin, extent_ymax]
    
    ##scan_lines=88086
    ##scan_pix=9900
    
    
    
    #slc_rows=scan_lines# norway_00709_15091_012_150610_L090_CX_02
    #slc_cols=scan_pix
    #iota=1j
    #if (is_List_Ratio==True):
        #subset_rows_start=np.floor(cropping_list[2]*slc_rows) #ratios gotten from estimates
        #subset_rows_end=np.floor(cropping_list[3]*slc_rows)
        #subset_cols_start=np.floor(cropping_list[0]*slc_cols)
        #subset_cols_end=np.floor(cropping_list[1]*slc_cols)
    #else:
        #subset_rows_start=cropping_list[2]
        #subset_rows_end=cropping_list[3]
        #subset_cols_start=cropping_list[0]
        #subset_cols_end=cropping_list[1]
    
    #tot_subset_rows=int(subset_rows_end-subset_rows_start)
    #tot_subset_cols=int(subset_cols_end-subset_cols_start)
        
    ##tot_oil_rows=13000
    
    #slc_subset_array=np.empty((tot_subset_rows,tot_subset_cols), dtype=np.complex64)
    
    
    #with open(file_name, "rb") as f:
        ##jump_to_subset =999
        ##f.seek(int(jump_to_subset*4))
        #f.seek(2)
        #print(struct.unpack(">h", f.read(2))) #8
        
        #sys.exit()
        
        #jump_to_subset=slc_cols*(subset_rows_start-1)+subset_cols_start
        #row_jump=slc_cols-tot_osubset_cols
        ##print(row_jump)
        #f.seek(int(jump_to_subset*8)) #jumping to oil spill area
        ##while(1==1):
            ##a=struct.unpack("<f", f.read(4))[0]
            ##b=struct.unpack("<f", f.read(4))[0]
            ##print(np.sqrt(a**2+b**2))
        
        #for j in range(0,tot_subset_rows):
            #subset_list=[]
            #for i in range(0, tot_subset_cols):
                #DN_real=f.read(4)
                #DN_imag=f.read(4)
                #oil_list.append(struct.unpack("<f", DN_real)[0]+iota*struct.unpack("<f", DN_imag)[0])
            #f.read(int(row_jump*8))
            #slc_subset_array[j]=oil_list
    #return slc_subset_array
