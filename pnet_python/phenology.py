from AtmEnviron import getdays

def phenology(rstep, veg, clim, share, growthphase, timestep):
    '''Phenology calculations for the PnET ecosystem model '''

    if growthphase == 1:

        ''' ---------------PnET-Daily--------------------
        PnET-CN only has code snippet for monthly timestep. Run w/timestep = 0

        elif instead of c++ switch case
        '''
        if timestep == 0:  # monthly timestep
            share['dayspan'] = getdays(
                clim.loc[rstep, 'doy'], clim.loc[rstep, 'year'])
        elif timestep == 1:  # daily
            share['dayspan'] = 1
        else:
            share['dayspan'] = getdays(
                clim.loc[rstep, 'doy'], clim.loc[rstep, 'year'])

        ''' -------------------------------------------------------'''        

        gdd = share['t_ave'] * share['dayspan']

        share['t_ave_yr'] += gdd / 365.0
        share['par_yr'] += clim.loc[rstep, 'par'] * share['dayspan'] / 365.0

        ''' ---------------PnET-Daily--------------------
        Pnet-CN does not have the doy logical
        '''
        if gdd < 0: # or clim.loc[rstep, 'doy'] < 60:
            gdd = 0  # Need to modify for tropical regions
        ''' -------------------------------------------------------'''   
        share['tot_gdd'] += gdd

        if share['tot_gdd'] >= veg['gdd_fol_start'] and clim.loc[rstep, 'doy'] < veg['senesce_start']:

            old_fol_ms = veg['fol_ms']
            gdd_fol_eff = (share['tot_gdd'] - veg['gdd_fol_start']) / \
                (veg['gdd_fol_end'] - veg['gdd_fol_start'])

            if gdd_fol_eff < 0:
                gdd_fol_eff = 0
            if gdd_fol_eff > 0:
                gdd_fol_eff = 1
                '''And if it equals 0?
                Can I write this as a simple ifelse?'''

            del_gdd_fol_eff = gdd_fol_eff - share['old_gdd_fol_eff']
            veg['fol_ms'] = veg['fol_ms'] + \
                (veg['bud_c'] * del_gdd_fol_eff) / veg['c_frac_biomass']
            share['fol_prod_c_mo'] = (
                veg['fol_ms'] - old_fol_ms) * veg['c_frac_biomass']
            share['fol_g_rsp_mo'] = share['fol_prod_c_mo'] * veg['g_rsp_frac']
            share['old_gdd_fol_eff'] = gdd_fol_eff
        else:
            share['fol_prod_c_mo'] = 0
            share['fol_g_rsp_mo'] = 0

    else:  # if growthphase does not equal 1

        share['fol_lit_m'] = 0

        if share['pos_c_bal_ms'] < veg['fol_ms'] and clim.loc[rstep, 'doy'] > veg['senesce_start']:

            if share['pos_c_bal_ms'] > veg['fol_ms_min']:
                fol_ms_new = share['pos_c_bal_ms']
            else:
                fol_ms_new = veg['fol_ms_min']

            if fol_ms_new == 0:
                share['lai'] = 0
            elif fol_ms_new < veg['fol_ms']:
                share['lai'] = share['lai'] * (fol_ms_new / veg['fol_ms'])
            '''I was expecting a third case -- if fol_ms_new > veg['fol_ms] '''

            if fol_ms_new < veg['fol_ms']:
                share['fol_lit_ms'] = veg['fol_ms'] - fol_ms_new

            veg['fol_ms'] = fol_ms_new
            '''This may be a reason to have fol_ms in the share pool -- it change
            Pay attention for other non-share variables that change. 
            If it's just the ones that were assigned to share in c++ that'll explain the logic'''

    
