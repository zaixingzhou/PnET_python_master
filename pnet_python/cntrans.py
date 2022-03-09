
def cntrans(site, veg, clim, rstep, share):
    biom_loss_frac = 0
    remove_frac = 0

    #if site['distyrs'] > 0: need to add

    root_turnover = veg['root_turnover_a'] - (veg['root_turnover_b'] * share['net_n_min_last_yr']) + (veg['root_turnover_c'] * pow(share['net_n_min_last_yr'], 2)
    if root_turnover > 2.5:
        root_turnover = 2.5
    if root_turnover < 0.1:
        root_turnover = 0.1
    root_turnover *= (share['dayspan'] / 365.0)

    if (biom_loss_frac > root_turnover):
        root_turnover = biom_loss_frac
    
    root_lit_m = veg['root_ms'] * root_turnover
    root_lit_n = root_lit_m * (share['root_ms_n'] / veg['root_ms'])
    veg['root_ms'] -= root_lit_m
    share['root_ms_n'] -= root_lit_n

    if (biom_loss_frac > 0):
        wood_lit_m = veg['wood_ms'] * biom_loss_frac * (1 - remove_frac)
        wood_lit_n = share['tot_wood_ms_n'] * biom_loss_frac * (1 - remove_frac)
        veg['wood_ms'] *= (1 - biom_loss_frac)
        share['tot_wood_ms_n'] *= (1 - biom_loss_frac)

    else:
        wood_lit_m = veg['wood_ms'] * veg['wood_turnover'] * (share['dayspan'] / 365.0)
        wood_lit_n = share['tot_wood_ms_n'] * veg['wood_turnover'] * (share['dayspan'] / 365.0)
        veg['wood_ms']  -= wood_lit_m
        share['tot_wood_ms_n'] -= wood_lit_n
    
    veg['dead_wood_ms'] += wood_lit_m #dead_wood_ms? maybe want to check where this is held
    share['tot_dead_wood_n'] += wood_lit_n
    wood_mass_loss = veg['dead_wood_ms'] * veg['wood_lit_loss_rate'] * (share['dayspan'] / 365.0)
    wood_trans_m = wood_mass_loss * (1 - veg['wood_lit_c_loss'])
    share['wood_dec_rsp'] = (wood_mass_loss - wood_trans_m) * veg['c_frac_biomass']
    wood_trans_n = (wood_mass_loss / veg['dead_wood_ms']) * share['tot_dead_wood_n']
    veg['dead_wood_ms'] -= wood_mass_loss
    share['tot_dead_wood_n'] -= wood_trans_n

    share['net_c_bal'] -= share['wood_dec_rsp']

    fol_n_loss = share['fol_lit_ms'] * (veg['fol_n_con'] / 100)
    retrans = fol_n_loss * veg['fol_n_retrans']
    veg['plant_n'] += retrans
    fol_lit_n = fol_n_loss - retrans

    if (biom_loss_frac > 0):
        share['fol_lit_ms'] += (veg['fol_ms'] * biom_loss_frac)
        fol_lit_n += (veg['fol_ms'] * biom_loss_frac * (veg['fol_n_con'] / 100))
        veg['fol_ms'] *= (1 - biom_loss_frac)
        veg['plant_c'] *= (1 - biom_loss_frac)
        veg['plant_n'] += (veg['max_n_store'] - veg['plant_n'] * biom_loss_frac)

    share['tot_lit_ms'] = share['fol_lit_ms'] + root_lit_m + wood_trans_m
    share['tot_lit_n'] = fol_lit_n + root_lit_n + wood_trans_n

    #agriculture
    if (clim.loc[rstep, 'year'] >= site['agstart'] and clim.loc[rstep, 'year'] < site['agstop']):
        share['tot_lit_ms'] *= (1 - site['agrem'])
        share['tot_lit_n'] *= (1 - site['agrem'])

        veg['wood_ms'] *= (1 - site['agrem'] * (share['dayspan'] / 365.0))
        share['tot_wood_ms_n'] *= (1 - site['agrem'] * (share['dayspan'] / 365.0))
    
    share['tot_lit_ms_yr'] += share['tot_lit_ms']
    share['tot_lit_n_yr'] += share['tot_lit_n']
