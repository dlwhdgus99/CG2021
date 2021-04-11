import glfw
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np

gCamAng_Azimuth = 0
gCamAng_Elevation = np.radians(10)

gCamHorizon = 0
gCamHeight = 0

dist = 5

ORBIT = False
PANNING = False

initialXPos = 0
initialYPos = 0

PERSPECTIVE = True

def createVertexAndIndexArrayForGrid():
    x = np.arange(-10,10,0.5)
    z = np.arange(-10,10,0.5)
 
    vertex = []
    for i in range(x.size):
        for j in range(z.size):
            vertex.append((x[i], 0, z[j]))
    varr = np.array(vertex, 'float32')
    
    index = []
    for i in range(x.size):
        index.append((x.size*i, x.size*i + x.size - 1))
    for i in range(z.size):
        index.append((i, z.size*(z.size-1) + i))
    iarr = np.array(index)

    return varr, iarr

def render():
    global gCamAng_Azimuth, gCamAng_Elevation, dist
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glEnable(GL_DEPTH_TEST)
    glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
    glLoadIdentity()

    if PERSPECTIVE:
        gluPerspective(45, 1, 1, 20)
    else:
        glOrtho(-5, 5, -5, 5, -10, 10)

    s1 = np.sin(gCamAng_Azimuth)
    c1 = np.cos(gCamAng_Azimuth)

    s2 = np.sin(gCamAng_Elevation)
    c2 = np.cos(gCamAng_Elevation)

    gluLookAt(dist*c2*s1 + gCamHorizon*c1,      dist*s2 + gCamHeight,    dist*c2*c1 - gCamHorizon*s1,
              gCamHorizon*c1,                   gCamHeight,              -gCamHorizon*s1,
              0,                                c2,                      0)

    drawFrame()

    glColor3ub(255, 255, 255)
    drawGrid_glDrawElements()

def drawGrid_glDrawElements():
    global gVertexArrayIndexed, glIndexArray
    varr = gVertexArrayIndexed
    iarr = gIndexArray
    glEnableClientState(GL_VERTEX_ARRAY)
    glVertexPointer(3, GL_FLOAT, 3*varr.itemsize, varr)
    glDrawElements(GL_LINES, iarr.size, GL_UNSIGNED_INT, iarr)

def drawFrame():
    glBegin(GL_LINES)
    glColor3ub(255, 0, 0)
    glVertex3fv(np.array([0., 0., 0.]))
    glVertex3fv(np.array([1., 0., 0.]))
    glColor3ub(0, 255, 0)
    glVertex3fv(np.array([0., 0., 0.]))
    glVertex3fv(np.array([0., 1., 0.]))
    glColor3ub(0, 0, 255)
    glVertex3fv(np.array([0., 0., 0.]))
    glVertex3fv(np.array([0., 0., 1.]))
    glEnd()

def key_callback(window, key, scancode, action, mods):
    global PERSPECTIVE

    if key == glfw.KEY_V:
        if action == glfw.PRESS:
            if PERSPECTIVE:
                PERSPECTIVE = False
            else:
                PERSPECTIVE = True

def cursor_callback(window, xpos, ypos):

    global gCamAng_Azimuth, gCamAng_Elevation, gCamHorizon, gCamHeight, initialXPos, initialYPos

    delta_X = xpos - initialXPos
    delta_Y = ypos - initialYPos

    initialXPos = xpos
    initialYPos = ypos
    
    if ORBIT:
        if np.cos(gCamAng_Elevation) >= 0:
            gCamAng_Azimuth -= np.radians(delta_X/10)

        else:
            gCamAng_Azimuth += np.radians(delta_X/10)

        gCamAng_Elevation += np.radians(delta_Y/10)

    if PANNING:
        if np.cos(gCamAng_Elevation) >= 0:
            gCamHeight += delta_Y/100

        else:
            gCamHeight -= delta_Y/100

        gCamHorizon -= delta_X/100

def button_callback(window, button, action, mod):

    global initialXPos, initialYPos, ORBIT, PANNING

    if button == glfw.MOUSE_BUTTON_LEFT:

        if action == glfw.PRESS:
            initialXPos, initialYPos = glfw.get_cursor_pos(window)
            ORBIT = True
        else:
            ORBIT = False

    elif button == glfw.MOUSE_BUTTON_RIGHT:

        if action == glfw.PRESS:
            initialXPos, initialYPos = glfw.get_cursor_pos(window)
            PANNING = True
        else:
            PANNING = False

def scroll_callback(window, xoffset, yoffset):
    global dist

    ratio = 0.9

    if yoffset > 0:
        dist = ratio*dist

    else:
        dist = (1/ratio)*dist

gVertexArrayIndexed = None
gIndexArray = None

def main():
    global gVertexArrayIndexed, gIndexArray

    if not glfw.init():
        return
    window = glfw.create_window(1200, 1200, "OpenGL viewer", None, None)
    if not window:
        glfw.terminate()
        return
    
    glfw.make_context_current(window)

    glfw.set_key_callback(window, key_callback)
    glfw.set_cursor_pos_callback(window, cursor_callback)
    glfw.set_mouse_button_callback(window, button_callback)
    glfw.set_scroll_callback(window, scroll_callback)

    gVertexArrayIndexed, gIndexArray = createVertexAndIndexArrayForGrid()

    while not glfw.window_should_close(window):
        glfw.poll_events()

        render()

        glfw.swap_buffers(window)

    glfw.terminate()

if __name__ == "__main__":
    main()        
