import numpy as np
from PIL import Image
from noise_gen import fPerlinNoise as FPN, voronoise as VN

def gen_fpn(resolution, octaves, seed, persistence, lacunarity, scale):
    arr = FPN(resolution, octaves, seed, persistence, lacunarity, scale)
    px = np.array([[(80, 0, (v + 0.5) * 255) for v in row] for row in arr], dtype=np.uint8)
    return Image.fromarray(px, mode='HSV').convert('RGB')

def gen_vn(resolution, cells_dim, seed, shake, return_mode):
    arr = VN(resolution, cells_dim, seed, shake, return_mode)
    cellCount = np.max(arr)
    valueList = [i * 255 / cellCount for i in range(cellCount)]
    shufflerng=np.random.default_rng(seed=seed)
    shufflerng.shuffle(valueList)
    px = np.array([[(80, 0, valueList[v-1]) for v in row] for row in arr], dtype=np.uint8)
    return Image.fromarray(px, mode='HSV').convert('RGB')

def rescale(res, max_dim):
    if res[0] < res[1]:
        return (int(max_dim * res[0] / res[1]), max_dim)
    elif res[0] > res[1]:
        return (max_dim, int(max_dim * res[1] / res[0]))
    return (max_dim, max_dim)   