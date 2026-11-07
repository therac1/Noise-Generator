import numpy as np

def dist(t1,t2):
    return np.sqrt(sum([(t1[i]-t2[i])**2 for i in range(len(t1))]));

def getCornerNodes(pixelPosition):
    list = [(int(x),int(y)) for x in [np.floor(pixelPosition[0]), np.floor(pixelPosition[0])+1] for y in [np.floor(pixelPosition[1]), np.floor(pixelPosition[1])+1]]
    return list;

def sLerp(a):
    if (a<=0):
        return 1;
    elif (a>=1):
        return 0;
    else:
        return(2*a**3 - 3*a**2 + 1);

