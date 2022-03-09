#Climate clim file

import pathlib

from pnet_input import share, veg, clim, site, clim_length, yearinit
from AtmEnviron import atm_environ
from phenology import phenology
from photosyn import photosyn
from waterbal import waterbal
from soilresp import soilresp
from allocatemo import allocatemo
from allocateyr import allocateyr

from pnet_output import output_month, output_year,WriteoutMo,WriteoutYr

#for rstep in range(input.clim_length): # steps through each climate.clim input line
#   AtmEnviron.atm_environ(rstep)
    #Photo

#for testing purposes
#set up output path and files
path = pathlib.Path.cwd()
path_output = path.parent/'Result'/'Site'  


file_out_mon = "Output_monthly.csv"
file_out_yr = "Output_annual.csv"

file_out_mon = path_output/file_out_mon
file_out_yr = path_output/file_out_yr

ystep =0

o3_effect = [None] * 50

for i in range(50):
    o3_effect[i] = 0
    


print ('**********')
    
   
for rstep in range(clim_length):
        
        
    atm_environ(rstep, share, clim, site)
    phenology(rstep, veg, clim, share, growthphase = 1, timestep = 0)
    photosyn(clim, share, site, veg, rstep)
    waterbal(site, veg, clim, share, rstep, timestep = 0)
    soilresp(veg, share, site, rstep)
    allocatemo(veg, share, rstep, cn_mode = 0)
    phenology(rstep, veg, clim, share, growthphase = 2, timestep = 0)
    
    WriteoutMo(rstep)
    
    if (clim.loc[rstep, 'doy'] > 335):
        allocateyr(site, veg, clim, rstep+1, share, cn_mode = 0)
        WriteoutYr(rstep,ystep)
        yearinit(share, o3_effect)
        ystep=ystep+1

         
    #print("PnET II runs on:Year DOY ystep", clim['year'][rstep], clim['doy'][rstep], ystep)
    
    
output_month.to_csv(file_out_mon,index=False)
output_year.to_csv(file_out_yr,index=False)
        
print ('Model PnET II run ends!!!')
        

