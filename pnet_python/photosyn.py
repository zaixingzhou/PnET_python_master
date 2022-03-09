from math import pow, log10, exp

def photosyn(clim, share, site, veg, rstep):
    '''Photosynthesis routine for the PnET model'''

    psn_t_max = veg['psn_t_opt'] + (veg['psn_t_opt'] - veg['psn_t_min'])
    d_temp = ((psn_t_max - share['t_day']) * (share['t_day'] -
                                              veg['psn_t_min'])) / (pow(((psn_t_max - veg['psn_t_min'])/2), 2))

    if clim.loc[rstep, 't_min'] < 6 and d_temp > 0 and share['tot_gdd'] >= veg['gdd_fol_end']:
        '''frost effect 
        --- comment says //need to verify zzx
        '''
        d_temp = d_temp * \
            (1.0 - ((6.0 - clim.loc[rstep, 't_min'])/6.0)
             * (share['dayspan'] / 30))

    if d_temp < 0:
        d_temp = 0

    share['dvpd'] = 1.0 - veg['dvpd1'] * (pow(share['vpd'], veg['dvpd2']))
    # ten9 = 1000000000.0 # this seems silly. I'm going to use pow(10,9)

    '''In c++
    Set atmospheric co2 concentration 
    ca = clim.loc[rstep, 'co2_atm']
    I'm just applying co2 directly
    '''

    '''Co2 effect on photosynthesis'''
    '''leaf internal/external co2'''
    ci_ca_ratio = (-0.075 * veg['fol_n_con']) + 0.875

    '''ci at (present) 350ppm co2'''
    ci_350 = 350 * ci_ca_ratio

    '''ci at real year co2 level'''
    ci_elev = clim.loc[rstep, 'co2_atm'] * ci_ca_ratio

    '''Areal - rate of photosynthesis at a given atmospheric co2
    ---was there an equation for Areal at one point?'''

    '''Co2_atm conc. relative to that which occurs at co2 saturation'''
    a_rel_350 = 1.22 * ((ci_350 - 68) / (ci_350 + 136))
    a_rel_elev = 1.22 * ((ci_elev - 68) / (ci_elev + 136))
    share['d_amax'] = 1 + ((a_rel_elev - a_rel_350) / a_rel_350)

    '''Looks like gamma, ca0 are only in here for commented out equations'''
    gamma = 40  # assume a mean leaf temp. during psn of 25 oC
    ca_0 = 350
    # share['d_amax'] = (clim.loc[rstep, 'co2_atm'] - gamma) / \
    #    (clim.loc[rstep, 'co2_atm'] + 2 * gamma) * (ca_0 + 2 * gamma) / \
    #        (ca_0 - gamma)
    # (Franks,2013, New Phytologist, 197:1077-1094)

    '''Calculate co2 effect on conductance 
    and set slope, intercept for A-gs relationship '''
    if site['co2_gs_eff'] == 1:
        d_gs = share['d_amax'] / \
            ((clim.loc[rstep, 'co2_atm'] - ci_elev) / (350 - ci_350))

        # used for effect on water use efficiency
        share['d_wue'] = 1 + (1 - d_gs)
        # used to determine conductance and then ozone uptake
        gs_slope = (-1.1309 * share['d_amax']) + 1.9762
        gs_int = (0.4656 * share['d_amax']) - 0.9701

        # d_gs = share['d_amax'] / (clim.loc[rstep, 'co2_atm'] / ca_0)
        # share['d_wue'] = 1 / d_gs
        # (Franks,2013, New Phytologist, 197:1077-1094) need to refine with the downregulation
    else:
        share['d_wue'] = 1
        gs_slope = (-0.6157 * share['d_amax']) + 1.4582
        gs_int = (0.4974 * share['d_amax']) - 0.9893

    f_amax = 1
    #f_amax = 1.46 //hw

    amax = (veg['amax_a'] + veg['amax_b'] * veg['fol_n_con']) * \
        share['d_amax'] * f_amax  # nmole CO2/g Fol.sec
    # amax = (veg['amax_a'] + veg['amax_b'] * 1.8) * share['d_amax'] * f_amax # nmole CO2/g Fol.sec
    # amax = pow(10.0, (0.74 * log10(veg['fol_n_con']) - 0.57 * log10(slw_layer) + 2.96)) * share['d_amax'] # nmole CO2/g Fol.sec
    # veg['base_fol_rsp_frac'] = 0.14 - 0.002 * share['t_ave'] # longterm leaf respiration acclimation (wythers, 2013, JGR, V118, 1?4)
    # veg['rsp_q10] = 3.22 - 0.046 * (share['t_ave'] + veg['psn_t_opt'])/2 # longterm leaf respiration acclimation (wythers, 2013, JGR, V118, 1?4)
    # veg['base_fol_rsp_frac'] = 0.09
    base_fol_rsp = veg['base_fol_rsp_frac'] * amax # * veg['fol_rsp_frac'] 
    amax = amax * veg['amax_frac']
    grs_amax = amax + base_fol_rsp
    # grs_amax: g C/g Fol/day, 12 for C atom
    grs_amax = (grs_amax * share['dvpd'] * d_temp *
                share['day_length'] * 12) / pow(10, 9)

    if grs_amax < 0:
        grs_amax = 0

    # g C/g Fol/day
    share['day_rsp'] = (base_fol_rsp * (pow(veg['rsp_q10'], ((share['t_day'] -
                                                              veg['psn_t_opt']) / 10))) * share['day_length'] * 12.0) / pow(10, 9)
    share['day_rsp'] = (base_fol_rsp * (pow(veg['rsp_q10'], ((share['t_night'] -
                                                              veg['psn_t_opt']) / 10))) * share['day_length'] * 12.0) / pow(10, 9)

    '''Initialize ozone effect'''
    can_net_psn_o3 = 0
    can_net_psn_pot = 0
    
    # Calculate canopy ozone extinction based on folmass
    o3_prof = 0.6163 + (0.00105 * veg['fol_ms'])
    if share['if_o3_effect_on_psn'] == 1:
        if clim.loc[rstep, 'year']>=site['year_start']:
            share['o3_effect_on_psn']=1
        else:
            share['o3_effect_on_psn']=1
    else:
        share['o3_effect_on_psn']=0
    
    share['light_eff_c_bal']=0
    n_layers = 50

    if (veg['fol_ms']) > 0:
        share['can_net_psn'] = 0
        share['can_grs_psn'] = 0
        share['lai'] = 0
        share['pos_c_bal_ms'] = veg['fol_ms']
        # Carry-over comment: posCBalMass: possible C Mass at balance point
        # o3_effect = 0
        layer = 0
        
        share['light_eff_c_bal'] = 0
        i_fol_ms = veg['fol_ms'] / n_layers
        ix = 0

        
        while 1:
            ix += 1
            i = ix * i_fol_ms
            slw_layer = veg['slw_max'] - (veg['slw_del'] * i)
            share['lai'] += i_fol_ms/slw_layer
            il = clim.loc[rstep, 'par'] * exp(-veg['k'] * share['lai'])
            light_eff = (1.0 - exp(-il * log10(2.0)/veg['half_sat']))
            layer_gross_psn_rate = grs_amax * light_eff
            layer_gross_psn = layer_gross_psn_rate * i_fol_ms
            layer_resp = (share['day_rsp'] + share['night_rsp']) * i_fol_ms
            layer_net_psn = layer_gross_psn - layer_resp

            if layer_net_psn < 0 and share['pos_c_bal_ms'] == veg['fol_ms']:
                share['pos_c_bal_ms'] = (ix - 1.0) * i_fol_ms
                share['light_eff_c_bal'] = light_eff
                

            if ix>n_layers:
                if ix > n_layers + 10:
                    break #the compensation point can not excess 30% of current foliar mass to avoid endless loop
                if layer_net_psn > 0 and d_temp > 0 and share['tot_gdd'] > veg['gdd_fol_end'] and clim.loc[rstep, 'doy'] < veg['senesce_start']:
                    continue
                else:
                    break

            if ix == n_layers:
                light_eff_bttm = light_eff
                lai_bttm = share['lai'] 

            share['can_net_psn'] += layer_net_psn
            share['can_grs_psn'] += layer_gross_psn


            
                #Ozone effects on Net psn
            
            if share['o3_effect_on_psn'] == 1 and share['tot_gdd'] > veg['gdd_fol_start']: 
                #Convert netpsn to micromoles for calculating conductance
                net_psn_umol = ((layer_net_psn * 1000000) / (share['daylength'] * 12)) / (i_fol_ms / slw_layer)
                #Calculate ozone extinction throughout the canopy
                layer += 1
                rel_layer = layer / n_layers
                rel_o3 = 1 - (rel_layer * o3_prof) * (rel_layer * o3_prof) * (rel_layer * o3_prof) #simplify by raising to the third
                if (rel_o3 < 0):
                    rel_o3 = 0
                    
                #Calculate Conductance (mm/s): Conductance down-regulates with prior O3 effects on Psn
                layer_g = (gs_int + (gs_slope * net_psn_umol)) * (1 - o3_effect[layer]) # might need to fix this - yes need to fix this

                if (layer_g < 0):
                    layer_g = 0
                    
                #Calculate cumulative ozone effect for each canopy layer with consideration that previous O3 effects were modified by drought
                o3_effect[layer] = (o3_effect[layer] * share['drought_o3_frac']) + (0.0026 * layer_g * clim.loc[rstep, 'o3'] * rel_o3)
                if o3_effect[layer] > 1.0:
                    o3_effect[layer] = 1.0
                layer_do3 = 1 - o3_effect[layer]

            else:
                layer_do3 = 1

            layer_net_psn_o3 = layer_net_psn * layer_do3
            can_net_psn_o3 = can_net_psn_o3 + layer_net_psn_o3
            

        if share['light_eff_c_bal'] < light_eff_bttm:
            share['light_eff_c_bal'] = light_eff_bttm - share['light_eff_c_bal']
        else:
            share['light_eff_c_bal'] = 0
        
        share['light_eff_c_bal'] = light_eff_bttm

        if d_temp > 0 and share['tot_gdd'] > veg['gdd_fol_end'] and clim.loc[rstep, 'doy'] < veg['senesce_start']:
            share['tot_pos_c_bal_ms'] = share['tot_pos_c_bal_ms'] + (share['pos_c_bal_ms'] * share['dayspan'])
            share['tot_pos_c_bal_ms_ix'] = share['tot_pos_c_bal_ms_ix'] + share['dayspan']

            share['tot_light_eff_c_bal'] = share['tot_light_eff_c_bal'] + (share['light_eff_c_bal'] * share['dayspan'])
            share['light_eff_c_bal_ix'] = share['light_eff_c_bal_ix'] + share['dayspan']

        if share['light_eff_minim'] > light_eff_bttm:
            share['light_eff_minim'] = light_eff_bttm
            
        share['lai'] = lai_bttm

    else:
        share['pos_c_bal_ms'] = 0
        share['can_net_psn'] = 0
        share['can_grs_psn'] = 0
        share['lai'] = 0
        share['day_rsp'] = 0
        share['night_rsp'] = 0
        
    if share['o3_effect_on_psn'] == 1 and share['tot_gdd'] > veg['gdd_fol_start'] and share['can_grs_psn'] > 0:
        can_net_psn_pot = share['can_grs_psn'] - (share['day_rsp'] * veg['fol_ms']) - (share['night_rsp'] * share['fol_mass'])
        share['can_d_o3_pot'] = can_net_psn_o3 / can_net_psn_pot

        share['tot_o3_dose'] = share['tot_o3_dose'] + clim.loc[rstep, 'o3']
    else:
        share['can_d_o3_pot'] = 1
    
    if share['can_d_o3_pot'] > 1:
        share['can_d_o3_pot'] = 1
    if share['can_d_o3_pot'] < 0:
        share['can_d_o3_pot'] = 1

            
        

