import numpy as np
import glfw
from OpenGL.GL import *

def main():
    
    M = np.arange(2,27)
    print(M, '\n')

    M = M.reshape(5,5)
    print(M, '\n')

    M[1:4, 1:4] = 0
    print(M, '\n')

    M = np.dot(M,M)
    print(M, '\n')

    v = M[0, :]
    v = np.square(v)
    v = np.sqrt(np.sum(v))
    print(v, '\n')

if __name__ == "__main__":
    main()


