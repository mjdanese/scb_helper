def scb(filename)
    import pandas as pd
    import numpy as np
    import csv
    import matplotlib.pyplot as plt
    %matplotlib inline

    heads = ['Time (Sec)','Load (kN)','Disp (mm)',
             'Core Temp (C)','Surf Temp (C)']

    df = pd.read_csv(filename, header = None, skiprows = 44)
    meta = pd.read_csv(filename, header = None, skiprows = 12, 
                       nrows =3, usecols = [1]) 

    df.columns = heads

    vals = meta.values
    diameter, thickness, notch = vals[0][0], vals[1][0], vals[2][0]

    idxmax = df['Load (kN)'].idxmax()
    pre = df.ix[0:idxmax]
    post_all = df.ix[idxmax:]

    # Find first index of value below 0.1 kN termination point
    end = post_all.loc[post_all['Load (kN)'] < 0.1].index[0]
    post = post_all.ix[:end]

    poly_pre = np.polyfit(pre['Disp (mm)'], pre['Load (kN)'], deg = 3)
    poly_post = np.polyfit(post['Disp (mm)'], post['Load (kN)'], deg = 3)

    # Integrate to get area under curve
    polyint_pre = np.polyint(poly_pre)
    polyint_post = np.polyint(poly_post)

    def poly3_def_int(coefficients, bottom, top):
        lower = np.polyval(coefficients, bottom)
        upper = np.polyval(coefficients, top)
        return upper-lower

    max_load_disp = df.ix[idxmax]['Disp (mm)']
    terminal_disp = post.iloc[-1]['Disp (mm)']
    pre_work = poly3_def_int(polyint_pre, 0, max_load_disp)
    post_work = poly3_def_int(polyint_post, max_load_disp, terminal_disp)
    WORK_OF_FRACTURE = pre_work + post_work

    AREA_OF_FRACTURE = (thickness * (diameter - notch))
    FRACTURE_ENERGY = WORK_OF_FRACTURE / AREA_OF_FRACTURE

    SECANT_STIFFNESS = df['Load (kN)'].max() / max_load_disp

    der1 = np.polyder(poly_post)
    der2 = np.polyder(der1)

    infl_x = -der2[1]/der2[0]
    infl_y = np.polyval(poly_post, infl_x)

    SLOPE = (der1[0]*(infl_x**2))+(der1[1]*infl_x)+der1[2]

    CRITICAL_DISPLACEMENT = (0.1 - infl_x + SLOPE) / SLOPE
    FLEXIBILITY_INDEX = (FRACTURE_ENERGY / abs(SLOPE)) * 100000

    result = [filename, WORK_OF_FRACTURE, AREA_OF_FRACTURE, FRACTURE_ENERGY, SECANT_STIFFNESS,
              infl_x, infl_y, SLOPE, CRITICAL_DISPLACEMENT, FLEXIBILITY_INDEX]
    
    return result