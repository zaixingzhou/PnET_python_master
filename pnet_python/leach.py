
def leach(share):
    share['n_drain'] = share['frac_drain'] * share['no3']
    share['n_drain_yr'] += share['n_drain']
    share['n_drain_mg_l'] = (share['n_drain'] * 1000) / (share['drainage'] * 10+1.0e-6)
    share['no3'] -= share['n_drain']