"""
@author: Jack Hastings
Input data
"""

import pathlib
import pandas as pd

'''No hardcode paths'''
path = pathlib.Path.cwd()
path_input = path.parent/'Input'

'''Read in input and climate file.'''
# Input text file.
input = pd.read_csv(path_input / 'pynet_input.csv')

# Climate clim file

#clim = pd.read_csv(path_input / 'pynet_climate.csv')
clim = pd.read_csv(path_input / 'climate_python.csv')

'''assign a climate length to be used in the rstep looping'''
clim_length = len(clim)


'''Assign the input data to dictionaries

I've done this to mimic the transparency of the c++ structs.
This may or may not be a good idea. Can easily rip it out.
'''
# model options
modeloptions = input.iloc[0:2].set_index('variable')['value'].to_dict()
# site settings
site = input.iloc[2:23].set_index('variable')['value'].to_dict()
# tree/forest settings
veg = input.iloc[23:79].set_index('variable')['value'].to_dict()
# management settings '''this maybe should be in the site dictionary'''
disturbance = input.iloc[80:].set_index('variable')['value'].to_dict()
# Notice the index pattern here -- seems like [79:] is wrong -- but it works.

'''Import shared variables --  convert to dictionary

*Import csv holding all shared variables
*Convert to dictionary with initialization value of zero
*Modify...
'''
share = pd.read_csv(path_input / 'shared_variables.csv')

share = share.set_index('shared_variables')['init_val'].to_dict()


'''!!! Need to talk about what variables are lumped where...
e.g. in c++
FolMass,WoodMass, DeadWoodM, RootMass, BudC, WoodC, PlantC, PlantN, and NRatio
are read into the share struct, but in the input file they fall within the veg
parameters...why? 
and
in pnet_initvars.cpp,
several variables are initialized with non-zero values:
Dwater, LightEffmin,LightEffCBal, RootNSinkEff, NRatioNit, NetNMinLastYear
Shouldn't these be in the input file?

several variables are initialized based on some other input variable e.g.
WoodMassN, DeadWoodN, RootC

And then there are some input variables that take the place of others...
seems unnecessary? 
e.g. veg->SoilRespA=site->SoilRespA;
just keep it as original. 

but for now...modifiy...
'''
#the ones that should be in the input

share['d_water'] = 1
share['light_eff_minim'] = 1
share['root_n_sink_eff'] = 0.5
share['n_ratio_nit'] = 1
share['net_n_min_last_yr'] = 10
share['avg_pcbm'] = 1.0
share['avg_d_water'] = 1

#the ones based on equations
#these veg[] parameters are read into share[] in c++. That seems wrong
share['root_c'] = veg['wood_c'] / 3
share['tot_wood_ms_n'] = veg['wood_ms'] * veg['min_wood_lit_n'] * veg['n_ratio']
share['tot_dead_wood_n'] = veg['dead_wood_ms'] * veg['min_wood_lit_n'] * veg['n_ratio']

#skipping converting variables between structures.

'''there are some variables that don't exist in the CN code
but are present in the daily version...
won't add any more now -- this is reminder. 
'''
share['yr_spin'] = 1000 

o3_effect = []


def yearinit(share, o3_effect):
    '''reset certain values at the end of years year'''
    share['tot_gdd'] = 0
    share['wood_maint_rsp_yr'] = 0
    share['soil_rsp_yr'] = 0
    share['tot_trans'] = 0
    share['tot_psn'] = 0
    share['tot_grs_psn'] = 0
    share['tot_drain'] = 0
    share['tot_prec'] = 0
    share['tot_evap'] = 0
    share['tot_water'] = 0
    share['fol_prod_c_yr'] = 0
    share['wood_prod_c_yr'] = 0
    share['root_prod_c_yr'] = 0
    share['root_maint_rsp_yr'] = 0
    share['fol_g_rsp_yr'] = 0
    share['wood_g_rsp_yr'] = 0
    share['root_g_rsp_yr'] = 0
    share['old_gdd_fol_eff'] = 0
    share['old_gdd_wood_eff'] = 0
    share['tot_pos_c_bal_ms'] = 0
    share['tot_pos_c_bal_ms_ix'] = 0
    share['tot_d_water'] = 0
    share['tot_d_water_ix'] = 0
    share['n_drain_yr'] = 0
    share['net_n_min_yr'] = 0
    share['tot_grs_n_min_yr'] = 0
    share['plant_n_uptake_yr'] = 0
    share['tot_grs_n_immob_yr'] = 0
    share['tot_lit_ms_yr'] = 0
    share['tot_lit_n_yr'] = 0
    share['net_nitr_yr'] = 0
    share['light_eff_minim'] = 1
    share['soil_dec_rsp_yr'] = 0
    share['wood_dec_rsp_yr'] = 0
    share['net_n_min_last_yr'] = share['net_n_min_yr']  # Won't this be zero?
    share['tot_n_dep'] = 0.0  # //ZZX
    share['tot_light_eff_c_bal'] = 0
    share['light_eff_c_bal_ix'] = 0
    share['t_ave_yr'] = 0
    share['par_yr'] = 0

    #fluxn2o etc.

    #share['tot_can_grs_psn_max']... gotta look into this one
    share['tot_can_d_o3'] = 0
    share['tot_can_d_o3_day'] = 0
    ''' reset all 50 layers '''
    
    for i in range(50):
        o3_effect[i] = 0
        

    share['tot_o3_dose'] = 0