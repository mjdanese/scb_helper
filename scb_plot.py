def scb_plot(df, pre, post, poly_pre, poly_post, 
                inflx, infly, infl_eqn, FLEXIBILITY_INDEX, 
                CRITICAL_DISPLACEMENT, filename):
    
    import matplotlib.pyplot as plt
    import pandas as pd
    import numpy as np

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

    # Fix x axis limits
    plt.xlim((0, post['Disp (mm)'].max()+0.01))
    plt.ylim((0.09, df['Load (kN)'].max()+0.01))
    plt.text(0.02, 0.1, 'FI: %s' % FLEXIBILITY_INDEX.round(1))

    plt.savefig('%s.png' % filename[8:-4], dpi=75)
    
    plt.close("all")