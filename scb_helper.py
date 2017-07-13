def scb_plot():
    import matplotlib.pyplot as plt
    %matplotlib inline 

    # Define some kool kolors
    teals = ['#42f4bc','#4ecea6','#52aa8f','#016647']
    reds = ['#ff7c7c','#e28e8e','#d15353','#960606']
    warmgreys = ['#afa6a0','#96867b','#775d4b','#4c3b27']

    plt.figure(1, figsize = (8,5))
    plt.title(filename[8:-4])

    plt.plot(pre['Disp (mm)'], pre['Load (kN)'], color = teals[1])
    plt.plot(post['Disp (mm)'], post['Load (kN)'], color = reds[1])

    # Define x's that can be used for pre and post peak curve plotting
    postx = np.arange(post['Disp (mm)'].min(),post['Disp (mm)'].max(),0.001)
    prex = np.arange(pre['Disp (mm)'].min(),pre['Disp (mm)'].max(),0.001)

    # Pre and post-peak curve fitting
    pre_curve_fn = np.poly1d(poly_pre)
    plt.plot(prex, pre_curve_fn(prex), color = teals[3], linestyle = '--')

    post_curve_fn = np.poly1d(poly_post)
    plt.plot(postx, post_curve_fn(postx), color = reds[3], linestyle = '--')

    # Label inflection point
    plt.scatter(inflx, infly, color = 'White', edgecolor = warmgreys[3], s = 50)
    plt.scatter(CRITICAL_DISPLACEMENT, 0.1, color = 'White', edgecolor = warmgreys[3], s = 50)

    # Draw first inflection point tangential slope
    plt.plot(postx, infl_eqn(postx), color = reds[3], linestyle = ':')

    # Fix x axis limits and label with flex index
    plt.xlim((0, post['Disp (mm)'].max()+0.01))
    plt.ylim((0.09, df['Load (kN)'].max()+0.01))
    plt.text(0.02, 0.1, 'FI: %s' % FLEXIBILITY_INDEX.round(1))

    plt.savefig('%s.png' % filename[8:-4], dpi = 100)

def scb_analysis(files):
    import pandas as pd
    import numpy as np
    
    for filename in files:
        try:
            # Sketchy proprietary import
            # Skips lines with non-native encoding
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

            poly_pre = np.polyfit(pre['Disp (mm)'], 
                                  pre['Load (kN)'], deg = 4)
            poly_post = np.polyfit(post['Disp (mm)'], 
                                   post['Load (kN)'], deg = 5)

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
            post_work = poly3_def_int(polyint_post, 
                                      max_load_disp, 
                                      terminal_disp)

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
            CRITICAL_DISPLACEMENT = (0.1-y_intercept)/SLOPE
            FLEXIBILITY_INDEX = (FRACTURE_ENERGY / abs(SLOPE)) * 100000

            scb_plot()

            results = [filename, WORK_OF_FRACTURE, AREA_OF_FRACTURE, 
                       FRACTURE_ENERGY, SECANT_STIFFNESS, inflx[0], 
                       infly[0], SLOPE, CRITICAL_DISPLACEMENT, 
                       FLEXIBILITY_INDEX]

            return results

        except:
            print('Error analyzing %s' % file)
