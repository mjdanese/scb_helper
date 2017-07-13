def scb(filename)
    import pandas as pd
    import numpy as np

    filename = 'results/CE-SCB-2_25-4.csv'

    # Sketchy import, skipping lines with non-native encoding
    df = pd.read_csv(filename, header = None, skiprows = 44)
    meta = pd.read_csv(filename, header = None, skiprows = 12, 
                       nrows =3, usecols = [1]) 

    # Rename columns for EZ access
    heads = ['Time (Sec)','Load (kN)','Disp (mm)',
         'Core Temp (C)','Surf Temp (C)']
    df.columns = heads

    vals = meta.values
    diameter, thickness, notch = vals[0][0], vals[1][0], vals[2][0]

    idxmax = df['Load (kN)'].idxmax()
    pre = df.ix[0:idxmax]
    post_all = df.ix[idxmax:]

    # Find first index of value below 0.1 kN termination point
    end = post_all.loc[post_all['Load (kN)'] < 0.1].index[0]
    post = post_all.ix[:end]

    poly_pre = np.polyfit(pre['Disp (mm)'], pre['Load (kN)'], deg = 4)
    poly_post = np.polyfit(post['Disp (mm)'], post['Load (kN)'], deg = 5)

    # Integrate to get area under curve
    polyint_pre = np.polyint(poly_pre)
    polyint_post = np.polyint(poly_post)

    def poly3_def_int(coefficients, bottom, top):
        lower = np.polyval(coefficients, bottom)
        upper = np.polyval(coefficients, top)
        return upper-lower

    # Calculate definite integral and add pre- and post- peak areas
    max_load_disp = df.ix[idxmax]['Disp (mm)']
    terminal_disp = post.iloc[-1]['Disp (mm)']
    pre_work = poly3_def_int(polyint_pre, 0, max_load_disp)
    post_work = poly3_def_int(polyint_post, max_load_disp, terminal_disp)

    # Calculate as many variables as possible so far
    WORK_OF_FRACTURE = pre_work + post_work
    AREA_OF_FRACTURE = (thickness * (diameter - notch))
    FRACTURE_ENERGY = WORK_OF_FRACTURE / AREA_OF_FRACTURE
    SECANT_STIFFNESS = df['Load (kN)'].max() / max_load_disp

    # Find 1st and second derivative
    der1 = np.polyder(poly_post)
    der2 = np.polyder(der1)

    # Find x,y of inflection x,y
    px = np.poly1d(der2)

    inflx = (px).roots
    infly = np.polyval(poly_post, inflx)

    # Calculate slope of inflection point tangent
    SLOPE = np.polyval(der1, inflx[2])
    y_intercept = infly[2] - (SLOPE * inflx[2])

    # Define inflection point equation
    infl_eqn = np.poly1d([SLOPE, y_intercept])

    # Finally, calculate flexibility index and critical displacement
    CRITICAL_DISPLACEMENT = np.polyval(infl_eqn, 0.1)
    FLEXIBILITY_INDEX = (FRACTURE_ENERGY / abs(SLOPE)) * 100000

    result = [filename, WORK_OF_FRACTURE, AREA_OF_FRACTURE, FRACTURE_ENERGY, SECANT_STIFFNESS,
              inflx[0], infly[0], SLOPE, CRITICAL_DISPLACEMENT, FLEXIBILITY_INDEX]
    
    return result
