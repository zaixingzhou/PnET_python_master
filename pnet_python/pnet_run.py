

def pnet_run(modeloptions):
    if modeloptions['modeltype'] == 0:
        pnet_day()
    elif modeloptions['modeltype'] == 1:
        pnet_ii()
    elif modeloptions['modeltype'] == 2:
        pnet_cn()
    elif modeloptions['modeltype'] == 3:
        pnet_daily()