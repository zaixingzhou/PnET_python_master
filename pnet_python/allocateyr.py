from pnet_input import disturbance

def allocateyr(site, veg, clim, rstep, share, cn_mode):
    share['npp_fol_yr'] = share['fol_prod_c_yr'] / veg['c_frac_biomass']
    share['npp_wood_yr'] = share['wood_prod_c_yr'] / veg['c_frac_biomass']
    share['npp_root_yr'] = share['root_prod_c_yr'] / veg['c_frac_biomass']

    if share['tot_d_water_ix']:
        share['avg_d_water'] = share['tot_d_water'] / share['tot_d_water_ix']
    else:
        share['avg_d_water'] = 1
    
    if share['tot_pos_c_bal_ms_ix'] > 0:
        share['avg_pcbm'] = (share['tot_pos_c_bal_ms'] / share['tot_pos_c_bal_ms_ix'])
    else:
        share['avg_pcbm'] = veg['fol_ms']
    
    share['can_d_o3_avg'] = share['tot_can_d_o3'] / share['tot_can_d_o3_day']

    if share['light_eff_c_bal_ix'] > 0:
        pot_light_eff = share['tot_light_eff_c_bal'] / share['light_eff_c_bal_ix']
    else:
        pot_light_eff = 1.0
    
    share['light_eff_minim'] = pot_light_eff

    env_max_fol = (share['avg_d_water'] * share['avg_pcbm']) * (1.0 + (veg['fol_rel_grow_max'] * share['light_eff_minim']))
    spp_max_fol = share['avg_pcbm'] * (1.0 + (veg['fol_rel_grow_max'] * share['light_eff_minim']))

    if env_max_fol < spp_max_fol:
        veg['fol_ms_max'] = env_max_fol
    else:
        veg['fol_ms_max'] = spp_max_fol

    fol_regen = 100
    biom_loss_frac = 0


    # check for disturbance years
    if disturbance['dist_yrs'] > 0:
        print('test')
    
    veg['fol_ms_min'] = (veg['fol_ms_max'] - veg['fol_ms_max'] * (1.0 / veg['fol_reten']))
    veg['bud_c'] = ((veg['fol_ms_max'] - veg['fol_ms']) * veg['c_frac_biomass'])

    if veg['bud_c'] < 0:
        veg['bud_c'] = 0
        if veg['fol_reten'] > 1:
            veg['bud_c'] = veg['fol_ms'] * 1 / (veg['fol_reten'] - 1) * veg['c_frac_biomass'] * 0.5
    
    veg['plant_c'] -= veg['bud_c']
    veg['wood_c'] = (1.0 - veg['plant_c_res_frac']) * veg['plant_c']
    veg['plant_c'] -= veg['wood_c']

    if veg['wood_c'] < (veg['min_wood_fol_ratio'] * veg['bud_c']):
        total_c = veg['wood_c'] + veg['bud_c']
        veg['wood_c'] = total_c * (veg['min_wood_fol_ratio'] / (1.0 + veg['min_wood_fol_ratio']))
        veg['bud_c'] = total_c - veg['wood_c']
        veg['fol_ms_max'] = veg['fol_ms'] + (veg['bud_c'] / veg['c_frac_biomass'])
        veg['fol_ms_min'] = (veg['fol_ms_max'] - veg['fol_ms_max'] * (1.0 / veg['fol_reten']))

    share['nep'] = share['tot_psn'] - share['wood_maint_rsp_yr'] - share['wood_g_rsp_yr'] - share['fol_g_rsp_yr'] - share['soil_rsp_yr']
    share['fol_n_con_old'] = veg['fol_n_con']

    if cn_mode == 1:
        print('cn mode')
