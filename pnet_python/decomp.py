
def decomp(site, veg, clim, rstep, share):
    f_n2o = 0
    f_no = 0
    f_n2 = 0
    f_n2o_d = 0
    kn = 0.01
    f_n_ratio_nit = 1.0

    #to do
    for iday in range(share['dayspan']):
        share['no3'] += clim.loc[rstep, 'no3_dep'] / share['dayspan']
        share['nh4'] += clim.loc[rstep, 'nh4_dep'] / share['dayspan']
        share['tot_n_dep'] += clim.loc[rstep, 'no3_dep'] / share['dayspan'] + clim.loc[rstep, 'nh4_dep'] / share['dayspan']

        if(share['t_ave'] > 1):
            t_eff_soil = share['t_ave']
        else:
            t_eff_soil = 1
        
        t_mult = (exp(0.1*(share['t_ave'] - 7.1)) * 0.68) * 1
        w_mult = share['mean_soil_moist_eff']

        #add litter to humus pool
        share['hom'] += share['tot_lit_ms'] / share['dayspan']
        share['hon'] += share['tot_lit_ms'] / share['dayspan']

        #humus dynamics
        kho_act = veg['kho'] / 365.0
        dho = share['hom'] * (1-exp(-kho_act * t_mult * w_mult))
        gross_n_min = dho * (share['hon'] / share['hom'])
        share['soil_dec_rsp'] = dho * veg['c_frac_biomass']
        share['soil_dec_rsp_yr'] += share['soil_dec_rsp']
        share['tot_grs_n_min_yr'] += gross_n_min
        share['hon'] -= gross_n_min
        share['hom'] -= dho

        share['net_c_bal'] -= share['soil_dec_rsp']

        #immobilization and net mineralization
        soil_pct_n = (share['hon'] / share['hom']) * 100
        n_reten = (veg['n_immob_a'] + veg['n_immob_b'] * soil_pct_n) / 100
        gross_n_immob = n_reten * gross_n_min
        share['hon'] += gross_n_immob
        share['tot_grs_n_immob_yr'] += gross_n_immob
        net_n_min = gross_n_min - gross_n_immob
        share['nh4'] += net_n_min

        #nitrification
        f_n_ratio_nit = 1/30.4 # daily time step
        net_nitr = (share['nh4'] * share['n_ratio_nit'] * f_n_ratio_nit)

        #NOx/N2O emission from soil nitrification
        share['wfps'] = share['water']/site['whc']*0.75
        if share['wfps'] > 1.0:
            share['wfps'] = 1.0
        
        w_nit = 1.0

        nit_lost_gas = kn*net_nitr*w_nit

        #to discard N gas emission processes, set nit_lost_gas = 0
        nit_lost_gas = 0

        r_nox_n2o = pow(10.0, -3.79*share['wfps'] + 2.73)
        f_n2o = nit_lost_gas / (1.0 + r_nox_n2o)
        f_no = nit_lost_gas - f_n2o

        share['no3'] += net_nitr
        share['nh4'] -= net_nitr - nit_lost_gas

        #soil denitrification

        #temperature effect on denitrification
        q10 = 2.0
        share['t_soil'] = share['t_ave']
        if 0.0 < share['t_soil']:
            den_t = pow(q10, 0.1*(share['t_soil'] - 20.0))
        else:
            den_t = 0.01
        
        # soil water effect on denitrification
        w_crit = 0.75
        den_w = 1.0-1.0/(1.0 + exp(12.5 *(share['wfps'] - w_crit)))

        #soil respiration effect as indicator of DOC
        #den_co2 = 24000
        c_crit = 1.8
        c_max = 3
        den_co2 = 1.0-1.0/(1.0+exp(6.8*(share['soil_dec_rsp'] - c_crit) / c_max))
        den_co2 = 1.0

        site['k_den'] = 0.03 #don't think k_den has been defined yet...

        if (den_w > den_co2):
            den_w = den_co2
        
        f_deni = share['no3'] * site['k_den'] * den_t * den_w

        #n2/n2o emission from soil in denitrificaiton
        r_n2_n2o = 1.44*exp(1.33*share['wfps'])

        #sigmodal curve as an alternative function
        share['rn_max'] = 10.0
        share['rn_x1'] = 0.7
        share['rn_y1'] = 1.5

        share['rn_x2'] = 1.0
        share['rn_y2'] = share['rn_max'] # all of these have not been defined

        rn_b = log(share['rn_y2'] / share['rn_y1']) / (share['rn_x2']) - share['rn_x1']
        rn_a = share['rn_y1'] * exp(-rn_b * share['rn_x1'])

        r_n2_n2o = rn_a * exp(rn_b * share['wfps'])

        f_n2o_d = f_deni * 1/(1+r_nox_n2o + r_n2_n2o)

        #to discard N gas emission processes, set f_n2o_d = 0
        f_n2o_d = 0

        f_no_d = r_nox_n2o * f_n2o_d
        f_n2 = f_n2o_d * r_n2_n2o

        share['flux_n2o_yr_de'] += f_n2o_d
        share['flux_no_yr_de'] += f_no_d

        share['flux_n2o_yr'] += f_n2o + f_n2o_d
        share['flux_no_yr'] += f_no + f_no_d
        share['flux_n2_yr'] += f_n2

        share['no3'] -= f_n2o_d + f_n2 + f_no_d

        #plant uptake
        root_n_sink_str = share['root_n_sink_eff'] * t_mult

        if (root_n_sink_str > 0.98):
            root_n_sink_str = 0.98
        root_n_sink_str = root_n_sink_str / 30.4 # *1.5 to make daily the same as monthly

        plant_n_uptake = (share['nh4'] + share['no3']) * root_n_sink_str

        if (plant_n_uptake + veg['plant_n']) > veg['max_n_store']:
            plant_n_uptake = veg['max_n_store'] - veg['plant_n']
            root_n_sink_str = plant_n_uptake / (share['no3'] + share['nh4'])
        
        if plant_n_uptake < 0:
            plant_n_uptake = 0
            root_n_sink_str = 0
        
        veg['plant_n'] += plant_n_uptake
        share['plant_n_uptake_yr'] += plant_n_uptake

        nh4_up = share['nh4'] * root_n_sink_str
        share['nh4'] = share['nh4'] - nh4_up
        no3_up = share['no3'] * root_n_sink_str
        share['no3'] = share['no3'] - no3_up

        share['net_n_min_yr'] += net_n_min
        share['net_nitr_yr'] += net_nitr

