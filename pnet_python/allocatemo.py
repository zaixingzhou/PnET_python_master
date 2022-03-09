from math import sin, pi, fabs, tan, atan, sqrt, pow, exp

def allocatemo(veg, share, rstep, cn_mode):
    veg['plant_c'] += (share['net_psn_mo'] - share['fol_g_rsp_mo'])

    wood_m_rsp_mo = share['can_grs_psn_act_mo'] * veg['wood_maint_rsp_a']
    share['wood_maint_rsp_yr'] += wood_m_rsp_mo
    share['fol_prod_c_yr'] += share['fol_prod_c_mo']
    share['fol_g_rsp_yr'] += share['fol_g_rsp_mo']

    if share['tot_gdd'] >= veg['gdd_wood_start']:
        gdd_wood_eff = (share['tot_gdd'] - veg['gdd_wood_start']) / (veg['gdd_wood_end'] - veg['gdd_wood_start'])
        
        if gdd_wood_eff > 1.0:
            gdd_wood_eff = 1
        elif gdd_wood_eff < 0:
            gdd_wood_eff = 0
    
        del_gdd_wood_eff = gdd_wood_eff - share['old_gdd_wood_eff']
        wood_prod_c_mo = veg['wood_c'] * del_gdd_wood_eff
        wood_g_rsp_mo = wood_prod_c_mo * veg['g_rsp_frac']
        share['wood_prod_c_yr'] += wood_prod_c_mo
        share['wood_g_rsp_yr'] += wood_g_rsp_mo
        share['old_gdd_wood_eff'] = gdd_wood_eff

    else:
        wood_prod_c_mo = 0
        wood_g_rsp_mo = 0
    
    share['wood_prod_c_mo'] = wood_prod_c_mo

    t_mult = (exp(0.1*(share['t_ave'] - 7.1)) * 0.68) * 1.0

    root_c_add = veg['root_alloc_a'] * (share['dayspan'] / 365.0) + veg['root_alloc_b'] * share['fol_prod_c_mo']
    share['root_c'] += root_c_add
    root_alloc_c_mo = (share['dayspan'] / 365.0) * t_mult # modified from MATLAB version
    if root_alloc_c_mo > 1.0:
        root_alloc_c_mo = 1
    
    root_alloc_c_mo *= share['root_c']

    share['root_c'] -= root_alloc_c_mo
    root_prod_c_mo = root_alloc_c_mo / (1.0 + veg['root_maint_rsp_frac'] + veg['g_rsp_frac'])
    share['root_prod_c_yr'] += root_prod_c_mo
    root_maint_rsp_mo = root_prod_c_mo * veg['root_maint_rsp_frac']
    share['root_maint_rsp_yr'] += root_maint_rsp_mo
    root_g_rsp_mo = root_prod_c_mo * veg['g_rsp_frac']
    share['root_g_rsp_yr'] += root_g_rsp_mo
    veg['plant_c'] -= root_c_add - wood_m_rsp_mo - wood_g_rsp_mo
    share['net_c_bal'] = share['net_psn_mo'] - share['soil_rsp_mo'] - wood_m_rsp_mo - wood_g_rsp_mo - share['fol_g_rsp_mo']

    share['root_prod_c_mo'] = root_prod_c_mo 

    
    # PnET-CN Only, will complete later

    