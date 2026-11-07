import numpy as np
import utils


# function: fPerlinNoise()
## returns a 2D-Array of values generated with fractal perlin noise.
def fPerlinNoise(Resolution=(16,16), Octaves=1, Seed=0, Persistence=.5, Lacunarity=2, Scale=1):
    #set up pixel grid.
    pxGrid = np.zeros(Resolution[::-1], dtype=float)

    #now, for each octave...
    for octave in range(Octaves):
        nodes = Scale*(Lacunarity**octave)  # each octave gets scaled by lacunarity
        nodes = int(np.ceil(nodes)+1)       # +1 for safety net
        pxPerNode = max(Resolution) / (nodes-1)

        #set up rng
        rng = np.random.default_rng(seed = Seed+octave)

        #make node grid and give each a random vector
        nodeGrid = np.ndarray((nodes, nodes), dtype=tuple)
        for n in np.ndindex(nodeGrid.shape):
            nodeGrid[n] = rng.random(2) - .5

        # get each pixel's value from this octave
        for px in np.ndindex(pxGrid.shape):
            
            pxPos = tuple(np.divide(px, pxPerNode))  # the pixel's position in the nodes' space.

            for nodeXY in utils.getCornerNodes(pxPos):  # for the four surrounding nodes...
                pxGrid[px] += np.dot(nodeGrid[nodeXY], tuple(np.subtract(nodeXY, pxPos))) * utils.sLerp(utils.dist(nodeXY, pxPos)) * (Persistence**octave)


    return(pxGrid)
##---
#


# funciton: voronoise()
## returns a 2D-Array of values assigned to generated Voronoi cells.
def voronoise(Resolution=(64,64), cellsDim=(4,4), Seed=0, Shake=1, ReturnMode="integer"):
    pxGrid = np.zeros(Resolution, dtype=tuple)

    rng = np.random.default_rng(Seed)

    #make shaken node grid
    nodeGrid = np.array([[(x + (Shake*(rng.random()-.5)), y + (Shake*(rng.random()-.5))) for y in range(cellsDim[1]+1)] for x in range(cellsDim[0]+1)])

    # get nearest node for each pixel
    for px in np.ndindex(pxGrid.shape):
        d = np.inf;
        nearest = (0,0);

        pxPos = (px[0]/(Resolution[0]+1)*cellsDim[0], px[1]/(Resolution[1]+1)*cellsDim[1])
        for n in [(round(pxPos[0])+x, round(pxPos[1])+y) for y in [-1,0,1] for x in [-1,0,1]]:
            if ((n[0]<0) or (n[0]>cellsDim[0]) or (n[1]<0) or (n[1]>cellsDim[1])):
                continue;
            else:
                if utils.dist(nodeGrid[n], pxPos) < d:
                    d = utils.dist(nodeGrid[n], pxPos)
                    nearest = n

        pxGrid[px] = nearest

    pxGrid = pxGrid.swapaxes(1,0)

    # different forms of cell information
    if ReturnMode == "integer":
        for px in np.ndindex(pxGrid.shape):
            pxGrid[px] = pxGrid[px][1]*cellsDim[0] + pxGrid[px][0]
    elif ReturnMode == "node_shaken":
        for px in np.ndindex(pxGrid.shape):
            pxGrid[px] = nodeGrid[pxGrid[px]]
    
    return(pxGrid)