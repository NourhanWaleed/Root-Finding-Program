import matplotlib.animation as ani
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np


def simulate(df, func, xrange, step):
    duration = len(df.index)/10 # in sec
    refreshPeriod = 100 # in ms
    def startanim(frame, iterator, p1, p2, p3):
        try:
            i = next(iterator)
            if i < len(df.index):
                x1 = df['x`'].iloc[i]
                p1.set_xdata([x1,x1])
                x2 = df['xl'].iloc[i]
                p2.set_xdata([x2,x2])
                x3 = df['xu'].iloc[i]
                p3.set_xdata([x3,x3])
                plt.xlim([x2 - 0.1, x3 + 0.1])

        except StopIteration:
            # iterator = iter(range(len(df.index)))
            root = df["x`"].iloc[-1]
            root_value = df["f(x`)"].iloc[-1]
            #plt.xlim([root - 0.000001, root + 0.000001])
            annotation_root = ax.annotate("x` = " + str(root), xy=(root, root_value), xytext=(root, root_value))




    x = np.arange(*xrange, step)
    f = []
    for x_ in x:
        f.append(func(x_))
    fig, ax = plt.subplots()
    # plt.xticks(rotation=45, ha="right", rotation_mode="anchor")
    plt.subplots_adjust(bottom = 0.2, top = 0.9)
    plt.ylabel('f(x)')
    plt.xlabel('x')
    plt.plot(x,f)
    p1 = plt.axvline(x=df['x`'].iloc[0], color='red', linestyle='--')
    p2 = plt.axvline(x=df['xl'].iloc[0], color='green')
    p3 = plt.axvline(x=df['xu'].iloc[0], color='blue')
    plt.legend(['xu', 'x`', 'xl'])

    animator = ani.FuncAnimation(fig, startanim,  frames=int(duration/(refreshPeriod/1000)), fargs=(iter(range(len(df.index))), p1, p2, p3), interval=refreshPeriod)

    plt.show()


