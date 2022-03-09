from math import sin, pi, fabs, tan, atan, sqrt, pow, exp  # same C/C++ Math Library

def atm_environ(rstep, share, clim, site):  # for transparency, require input dictionaries

    share['t_ave'] = (clim.loc[rstep, 't_min'] +
                      clim.loc[rstep, 't_max']) / 2.0
    share['t_day'] = (clim.loc[rstep, 't_max'] + share['t_ave'])/2.0
    share['t_night'] = (share['t_ave'] + clim.loc[rstep, 't_min'])/2.0

    latrad = site['lat'] * (2.0 * pi) / 360
    ''' r is a hold over from matlab. Never used. delete? '''
    # r = 1 - (0.0167 * cos(0.0172 * (clim.loc[rstep,'doy'] - 3)))
    z = 0.39785 * sin(4.868961 + 0.017203 * clim.loc[rstep, 'doy'] +
                      0.033446 * sin(6.224111 + 0.017202 * clim.loc[rstep, 'doy']))
    # I want to put in comments to reference each equation
    if fabs(z) < 0.7:
        decl = atan(z / (sqrt(1.0 - pow(z, 2))))
    else:
        decl = pi / 2.0 - atan(sqrt(1 - pow(z, 2)) / z)

    if fabs(latrad) >= (pi / 2):
        if (site['lat'] < 0):
            latrad = (-1.0) * (pi / 2.0 - 0.01)
        else:
            latrad = (1.0) * (pi / 2.0 - 0.01)

    z2 = -tan(decl) * tan(latrad)

    if z2 >= 1.0:
        h = 0
    elif z2 <= -1.0:
        h = pi
    else:
        ta = fabs(z2)
        if ta < 0.7:
            ac = 1.570796 - atan(ta / sqrt(1.0 - pow(ta, 2)))
        else:
            ac = atan(sqrt(1 - pow(ta, 2)) / ta)
        if z2 < 0:
            h = pi - ac
        else:
            h = ac

    hr = 2.0 * (h * 24.0) / (2.0 * pi)  # hours
    share['day_length'] = 3600 * hr  # seconds
    share['night_length'] = 3600 * (24.0 - hr)  # seconds

    es = 0.61078 * exp(17.26939 *  share['t_day'] / (share['t_day'] + 237.3))
    '''delta is defined, but never used in pnet-cn or pnet-daily AtmEnviron'''
    delta = 4098.0 * es / ((share['t_day'] + 237.3) * (share['t_day'] + 237.3))

    if(share['t_day'] < 0):
        es = 0.61078 * exp(21.87456 *  share['t_day'] / (share['t_day'] + 265.5))
        delta = 5808.0 * es / ((share['t_day'] + 265.5) * (share['t_day'] + 265.5))

    e_mean = 0.61078 * exp(17.26939 * clim.loc[rstep, 't_min'] / (clim.loc[rstep, 't_min'] + 237.3))

    if clim.loc[rstep, 't_min'] < 0:
        e_mean = 0.61078 * exp(21.87456 * clim.loc[rstep, 't_min'] / (clim.loc[rstep, 't_min'] + 265.5))

    share['vpd'] = es - e_mean

    

    


def getdays(doy, year):
    if doy > 367 or doy < 1:
        print("Cannot convert the number to date")
        return 0

    '''
    Note that indexing starts at zero. Jan = 0, Feb = 1, etc.
    This differs from c++ just barely because of that
    '''
    days = [31] * 12  # start with 31 days, specify from here
    days[1] = 28  # feb
    '''didn't know this about leap years...'''
    if (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0):
        days[1] = 29
    days[3] = days[5] = days[8] = days[10] = 30  # april, june, sept., Nov.

    i = 0
    while doy > days[i]:
        doy -= days[i]
        i += 1

    return days[i]


def getmonth(doy, year):
    if doy > 367 or doy < 1:
        print("Cannot convert the number to date")
        return 0

    '''
    Note that indexing starts at zero. Jan = 0, Feb = 1, etc.
    This differs from c++ just barely because of that
    '''
    days = [31] * 12  # start with 31 days, specify from here
    days[1] = 28  # feb
    '''didn't know this about leap years...'''
    if (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0):
        days[1] = 29
    days[3] = days[5] = days[8] = days[10] = 30  # april, june, sept., Nov.

    i = 0
    while doy > days[i]:
        doy -= days[i]
        i += 1

    return i  # note subtle difference between getday and getmonth


def is_leapyear(year):
    if (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0):
        return 1
    else:
        return 0
