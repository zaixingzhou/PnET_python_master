"""
Write out modeling results
"""

import pathlib
import pandas as pd

from pnet_input import share, veg, clim, site, clim_length, yearinit

'''No hardcode paths'''
path = pathlib.Path.cwd()
path_input = path.parent/'Input'



mon_var_names = ["year", "doy", "temp",
                "GrowthDD", "prec", "vpd",
                "snowpack", "ET", "Drain","Soilwater",
                "DWater", "DwaterIx","Dwatertot",
                "Foliage", "PlantC", "BudC", "WoodC","RootC","LAI",                  
                "NetPsnMo", "GrsPsnMo", "NEE",
                "WoodMR", "WoodGR", "FolGR","RootGR", "RootMR", "SoilResp",
                "FoliarN"              
                
                ]


output_month = pd.DataFrame(columns = mon_var_names,index=range(0, clim_length))

#print(output_month.head(5))

yr_var_names = ["year", "folm", "nppfol", "nppwood","npproot", 
                "psn", "nep","gpp",
                "prec", "evap", "trans", "drain", "wtrstress",         
                "decresp",
                "v1", "v2"          
                
                ]

nyrs = clim.year[clim_length-1]-clim.year[0]+1;

output_year = pd.DataFrame(columns = yr_var_names,index=range(0, nyrs))



def WriteoutMo(rstep):
   
    output_month.year[rstep] = clim.year[rstep] 
    output_month.doy[rstep] = clim.doy[rstep]     
    output_month.temp[rstep] = share['t_ave']
    
    output_month.GrowthDD[rstep] = share['tot_gdd'] 
    output_month.prec[rstep] = clim.precip[rstep]  
    output_month.vpd[rstep] = share['vpd'] 
    
    output_month.snowpack[rstep] = site['snow_pack']
    output_month.ET[rstep] = share['et'] 
    output_month.Drain[rstep] = share['drainage'] 
    output_month.Soilwater[rstep] = site['soil_water']
  
    output_month.DWater[rstep] = share['d_water'] 
    output_month.DwaterIx[rstep] = share['tot_d_water_ix'] 
    output_month.Dwatertot[rstep] = share['tot_d_water'] 
    
    output_month.Foliage[rstep] = veg['fol_ms']     
    output_month.PlantC[rstep] = veg['plant_c']
    output_month.BudC[rstep] = veg['bud_c']
    output_month.WoodC[rstep] = veg['wood_c']
    output_month.RootC[rstep] = share['root_c']    
    output_month.LAI[rstep] = share['lai'] 

    output_month.NetPsnMo[rstep] = share['net_psn_mo']
    output_month.GrsPsnMo[rstep] = share['grs_psn_mo'] 
    output_month.NEE[rstep] = share['net_c_bal'] 
    
    output_month.WoodMR[rstep] = share['wood_maint_rsp_yr'] 
    output_month.WoodGR[rstep] = share['wood_g_rsp_yr'] 
    output_month.FolGR[rstep] = share['fol_g_rsp_yr'] 
    output_month.RootGR[rstep] = share['root_g_rsp_yr'] 
    output_month.RootMR[rstep] = share['root_maint_rsp_yr']
    output_month.SoilResp[rstep] = share['soil_rsp_mo']  
    
    output_month.FoliarN[rstep] = veg['fol_n_con']
    

def WriteoutYr(rstep,ystep):
   
    
        
    output_year.year[ystep] = clim.year[rstep] 
    
    output_year.folm[ystep] = veg['fol_ms']
    
    output_year.nppfol[ystep] = share['npp_fol_yr']
    output_year.nppwood[ystep] = share['npp_wood_yr']
    output_year.npproot[ystep] = share['npp_root_yr']
    
    output_year.psn[ystep] = share['tot_psn']
    output_year.nep[ystep] = share['nep']
    output_year.gpp[ystep] = share['tot_grs_psn']
    
    output_year.prec[ystep] = share['tot_prec']
    output_year.evap[ystep] = share['tot_evap']
    output_year.trans[ystep] = share['tot_trans']
    output_year.drain[ystep] = share['tot_drain']
    output_year.wtrstress[ystep] = share['avg_d_water']
    
    output_year.decresp[ystep] = share['soil_dec_rsp_yr']
    output_year.v1[ystep] = 0
    output_year.v2[ystep] = 1
    
    
 
        
 