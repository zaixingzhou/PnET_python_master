

# make timestep an input var in modelset dict?
def waterbal(site, veg, clim, share, rstep, timestep):
    '''PnET Ecosystem Water Balance Routine'''

    '''Potential transpiration'''
    can_grs_psn_mg = share['can_grs_psn'] * \
        1000.0 * (44.0 / 12.0)  # mg co2/m2.day
    wue = (veg['wue_const'] / share['vpd']) * share['d_wue']  # g co2/kg water
    # d_amax added to prevent increased transpiration at high co2
    pot_trans_d = (can_grs_psn_mg / share['d_amax'] / wue) / 10000.0 # cm water/day

    '''Precip input and snow/rain partitioning '''
    evap = clim.loc[rstep, 'precip'] * \
        veg['prec_int_frac']  # all intercepted rain evaporated
    precip_rem = clim.loc[rstep, 'precip'] - evap

    if share['t_ave'] > 2.0:
        snow_frac = 0
    elif share['t_ave'] < -5.0:
        snow_frac = 1.0
    elif share['t_ave'] >= -5.0 and share['t_ave'] <= 2.0:
        snow_frac = (share['t_ave'] - 2.0) / 7.0

    if timestep == 1:       # Daily Version
        snow_t_crit = -6.0
        snow_melt = 0.0

        t_ave_w = share['t_ave']
        if share['t_ave'] < 1.0:
            t_ave_w = 1.0

        if clim.loc[rstep, 't_min'] > snow_t_crit:
            snow_frac = 0
            snow_melt = 0.15 * t_ave_w
        else:
            snow_frac = 1.0

    '''Snowmelt'''
    site['snow_pack'] = site['snow_pack'] + precip_rem * snow_frac
    if site['snow_pack'] > 0:

        if timestep == 0:       # monthly version
            t_ave_w = share['t_ave']

            if share['t_ave'] < 1.0:
                t_ave_w = 1.0
            
            snow_melt = 0.15 * t_ave_w * share['dayspan']

        if snow_melt > site['snow_pack']:
            snow_melt = site['snow_pack']

    else:
        snow_melt = 0


    site['snow_pack'] = site['snow_pack'] - snow_melt

    '''Fast Flow'''
    water_in = snow_melt + precip_rem * (1.0 - snow_frac)
    fast_flow = site['fast_flow_frac'] * water_in
    water_in -= fast_flow
    water_in_d = water_in / share['dayspan'] # daily water in

    '''Transpiration'''
    trans = 0 
    if pot_trans_d > 0:

        tot_soil_moist_eff = 0
        '''replace c++ for loop with python while loop'''
        
        for wday in range(share['dayspan']):
            site['soil_water'] += water_in_d
            # c++ assigned fastflowfrac to veg -> f. I didn't
            if site['soil_water'] >= pot_trans_d / site['fast_flow_frac']:
                trans_d = pot_trans_d
            else:
                trans_d = site['soil_water'] * site['fast_flow_frac']

            site['soil_water'] -= trans_d
            trans += trans_d

            if site['soil_water'] < site['whc']:
                d_temp = site['soil_water'] 
            else: 
                d_temp = site['whc']

            tot_soil_moist_eff += \
                pow((d_temp / site['whc']), (1.0 + site['soil_moist_fact']))

            wday += 1 
            # end of daily loop


        share['mean_soil_moist_eff'] = \
            tot_soil_moist_eff / share['dayspan'] #// bug correct, zzx
        if share['mean_soil_moist_eff'] > 1:
            share['mean_soil_most_eff'] = 1

        '''Water stress'''
        share['d_water'] = trans / (pot_trans_d * share['dayspan'])

        '''Manually turn water stress off '''
        if site['water_stress'] == 0:
            share['d_water'] = 1
        if share['d_water'] > 1.0:
            share['d_water'] = 1.0

        share['tot_d_water'] += (share['d_water'] * share['dayspan'])
        share['tot_d_water_ix'] += share['dayspan']

    else: 
        share['d_water'] = 1.0
        site['soil_water'] += water_in
        share['mean_soil_moist_eff'] = 1.0

    '''Calculate actual ozone effect on NetPsn with drought stress'''
    if share['o3_effect_on_psn'] == 1 and share['can_grs_psn'] > 0:

        if site['wue_o3_eff'] == 0:
            # no o3 effect on wue (assumes no stomatal impairment)
            share['can_d_o3'] = share['can_d_o3_pot'] + (1 - share['can_d_o3_pot']) * (1 - share['d_water']) # drough offset to 03 effect
        else:
            # reduce the degree to which drought offsets o3 (assume stomatal impairment in porportion to effect on psn)
            share['can_d_o3'] = share['can_d_o3_pot'] + (1 - share['can_d_o3_pot']) * (1 - share['d_water'] / share['can_d_o3_pot'])

        # relative drought offset
        share['drought_o3_frac'] = share['can_d_o3_pot'] / share['can_d_o3']

    else:
        share['can_d_o3'] = 1
        share['drought_o3_frac'] = 1

    if share['can_d_o3'] > 1:
        share['can_d_o3'] = 1
    
    if (share['can_grs_psn'] > 0):
        share['tot_can_d_o3'] += (share['can_d_o3'] * share['dayspan'])
        share['tot_can_d_o3_day'] += share['dayspan']


    can_grs_psn_act = share['can_grs_psn'] * share['d_water'] # g C/m2.day
    share['can_grs_psn_act_mo'] = can_grs_psn_act * share['dayspan'] # g C/m2.day
    share['grs_psn_mo'] = share['can_grs_psn_act_mo']
    share['net_psn_mo'] = (can_grs_psn_act - (share['day_rsp'] + share['night_rsp']) * veg['fol_ms']) * share['dayspan'] * share['can_d_o3']

    if site['soil_water'] > site['whc']:
        share['drainage'] = site['soil_water'] - site['whc']
        site['soil_water'] = site['whc']
    else:
        share['draingage'] = 0

    share['drainage'] = share['drainage'] + fast_flow
    share['frac_drain'] = share['drainage'] / (site['soil_water'] + clim.loc[rstep, 'precip'])
    share['tot_trans'] += trans
    share['tot_water'] += site['soil_water']
    share['tot_psn'] += share['net_psn_mo']
    share['tot_drain'] += share['drainage']
    share['tot_prec'] += clim.loc[rstep, 'precip']
    share['tot_evap'] += evap
    share['tot_grs_psn'] += share['grs_psn_mo']
    share['et'] = trans + evap


