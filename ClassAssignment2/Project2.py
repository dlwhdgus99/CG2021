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

DROP = False

initialXPos = 0
initialYPos = 0

PERSPECTIVE = True
HIERARCHY = False
WIRE = True

def createVertexAndIndexArrayForGrid():
    x = np.arange(-100,100,5)
    z = np.arange(-100,100,5)
 
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

    if WIRE:
        glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
    else:
        glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)

    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()

    if PERSPECTIVE:
        gluPerspective(45, 1, 0.1, 1000)
    else:
        glOrtho(-20, 20, -20, 20, -30, 30)

    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    s1 = np.sin(gCamAng_Azimuth)
    c1 = np.cos(gCamAng_Azimuth)

    s2 = np.sin(gCamAng_Elevation)
    c2 = np.cos(gCamAng_Elevation)

    gluLookAt(dist*c2*s1 + gCamHorizon*c1,      dist*s2 + gCamHeight,    dist*c2*c1 - gCamHorizon*s1,
              gCamHorizon*c1,                   gCamHeight,              -gCamHorizon*s1,
              0,                                c2,                      0)

    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    glEnable(GL_LIGHT1)
    glEnable(GL_LIGHT2)
    glEnable(GL_RESCALE_NORMAL)
    glPushMatrix()

    lightPos0 = (100., 10., 100., 1.)
    lightPos1 = (-100., 10., -100., 1.)
    lightPos2 = (0., 100., 0.)

    glLightfv(GL_LIGHT0, GL_POSITION, lightPos0)
    glLightfv(GL_LIGHT1, GL_POSITION, lightPos1)
    glLightfv(GL_LIGHT2, GL_POSITION, lightPos2)
    glPopMatrix()

    lightColor0 = (1., 1., 1., 1.)
    ambientLightColor0 = (.1, .1, .1, 1.)
    glLightfv(GL_LIGHT0, GL_DIFFUSE, lightColor0)
    glLightfv(GL_LIGHT0, GL_SPECULAR, lightColor0)
    glLightfv(GL_LIGHT0, GL_AMBIENT, ambientLightColor0)

    lightColor1 = (1., 1., 1., 1.)
    ambientLightColor1 = (.1, .1, .1, 1.)
    glLightfv(GL_LIGHT1, GL_DIFFUSE, lightColor1)
    glLightfv(GL_LIGHT1, GL_SPECULAR, lightColor1)
    glLightfv(GL_LIGHT1, GL_AMBIENT, ambientLightColor1)

    lightColor2 = (1., 1., 1., 1.)
    ambientLightColor2 = (.1, .1, .1, 1.)
    glLightfv(GL_LIGHT2, GL_DIFFUSE, lightColor2)
    glLightfv(GL_LIGHT2, GL_SPECULAR, lightColor2)
    glLightfv(GL_LIGHT2, GL_AMBIENT, ambientLightColor2)

    objectColor = (1., 1., 1., 1.)
    specularObjectColor = (1., 1., 1., 1.)
    glMaterialfv(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, objectColor)
    glMaterialfv(GL_FRONT, GL_SHININESS, 10)
    glMaterialfv(GL_FRONT, GL_SPECULAR, specularObjectColor)

    glPushMatrix()

    drawGrid_glDrawElements()
    if HIERARCHY:
        drawSolarSystem()
    elif DROP:
        setObjectColor(.3, 0., .5)
        drawMesh_glDrawArray(gVertexArrayForMesh)

    glPopMatrix()
    glDisable(GL_LIGHTING)

def drawGrid_glDrawElements():
    global gVertexArrayIndexedForGrid, glIndexArrayForGrid
    varr = gVertexArrayIndexedForGrid
    iarr = gIndexArrayForGrid
    glEnableClientState(GL_VERTEX_ARRAY)
    glVertexPointer(3, GL_FLOAT, 3*varr.itemsize, varr)
    glDrawElements(GL_LINES, iarr.size, GL_UNSIGNED_INT, iarr)

def drawMesh_glDrawArray(varr):
    glEnableClientState(GL_VERTEX_ARRAY)
    glEnableClientState(GL_NORMAL_ARRAY)
    glNormalPointer(GL_FLOAT, 6*varr.itemsize, varr)
    glVertexPointer(3, GL_FLOAT, 6*varr.itemsize, ctypes.c_void_p(varr.ctypes.data + 3*varr.itemsize))
    glDrawArrays(GL_TRIANGLES, 0, int(varr.size/6))

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

def drawSphere():
    dummy = np.zeros(4)
    varr, dummy[0], dummy[1], dummy[2], dummy[3] = parse_obj('Sphere.obj')
    drawMesh_glDrawArray(varr)

def drawSaturn():
    dummy = np.zeros(4)
    varr, dummy[0], dummy[1], dummy[2], dummy[3] = parse_obj('Saturn.obj')
    drawMesh_glDrawArray(varr)

def drawSatellite1():
    dummy = np.zeros(4)
    varr, dummy[0], dummy[1], dummy[2], dummy[3] = parse_obj('Satellite1.obj')
    drawMesh_glDrawArray(varr)

def setObjectColor(R, G, B):
    objectColor = (R, G, B)
    specularObjectColor = (1., 1., 1., 1.)
    glMaterialfv(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, objectColor)
    glMaterialfv(GL_FRONT, GL_SHININESS, 10)
    glMaterialfv(GL_FRONT, GL_SPECULAR, specularObjectColor)

def drawSolarSystem():

    t = glfw.get_time()

    #Sun
    glPushMatrix()
    glTranslatef(0, 10, 0) 
    glPushMatrix()
    glScale(10, 10, 10)
    glRotatef(20*t, 0, 1, 0)
    setObjectColor(1., .6, 0.)
    drawSphere()
    glPopMatrix()

    #Mercury
    glPushMatrix()
    glRotate(47*t, 0, 1, 0)
    glTranslatef(5, 0, 0)
    glRotatef(20*t, 0, 1, 0)
    setObjectColor(.5, .3, .2)
    drawSphere()
    glPopMatrix()

    #Venus
    glPushMatrix()
    glRotate(35*t, 0, 1, 0)
    glTranslatef(8, 0, 0)
    glRotate(20*t, 0, 1, 0)
    setObjectColor(1., .3, 0.)
    drawSphere()
    glPopMatrix()

    #Earth
    glPushMatrix()
    glRotate(29*t, 0, 1, 0)
    glTranslatef(11, 0, 0)
    glScalef(3, 3, 3)
    glRotate(20*t, 0, 1, 0)
    setObjectColor(0., 0., 1.)
    drawSphere()

    #Satellite1
    glPushMatrix()
    glRotatef(1.2*t, 0, 1, 0)
    glTranslatef(0.4, 0, 0)
    glScalef(1/200, 1/200, 1/200)
    setObjectColor(.5, .5, .5)
    drawSatellite1()
    glPopMatrix()

    #Moon
    glPushMatrix()
    glRotate(1*t, 0, 1, 0)
    glTranslatef(1, 0, 0)
    glScale(0.2, 0.2, 0.2)
    glRotate(20*t, 0, 1, 0)
    setObjectColor(.3, .3, .3)
    drawSphere()
    glPopMatrix() # moon

    glPopMatrix() #earth

    #Mars
    glPushMatrix()
    glRotate(24*t, 0, 1, 0)
    glTranslatef(14, 0, 0)
    glRotate(20*t, 0, 1, 0)
    setObjectColor(1., .2, 0.)
    drawSphere()
    glPopMatrix()

    #Jupiter
    glPushMatrix()
    glRotatef(13*t, 0, 1, 0)
    glTranslatef(17, 0, 0)
    glScalef(5, 5, 5)
    glRotatef(20*t, 0, 1, 0)
    setObjectColor(.6, .3, 0.)
    drawSphere()

    #Jupiter Moons
    glPushMatrix()
    glRotatef(2*t, 0, 1, 0)
    glTranslatef(0.5, 0, 0)
    glScalef(0.15, 0.15, 0.15)
    glRotatef(20*t, 0, 1, 0)
    setObjectColor(.5, .4, 0.)
    drawSphere()
    glPopMatrix() #moon

    glPushMatrix()
    glRotatef(2*t, 0, 1, 0)
    glTranslatef(0, 0, 0.5)
    glScalef(0.1, 0.1, 0.1)
    glRotatef(20*t, 0, 1, 0)
    setObjectColor(.4, .4, 0.)
    drawSphere()
    glPopMatrix() #moon

    glPopMatrix() #jupiter

    #Saturn
    glPushMatrix()
    glRotatef(9*t, 0, 1, 0)
    glTranslatef(25, 0, 0)
    glScalef(1/250, 1/250, 1/250)
    glRotate(20*t, 0, 1, 0)
    glRotate(90, 1, 0.2, 0)
    setObjectColor(.55, .25, 0.)
    drawSaturn()

    glPopMatrix()
    glPopMatrix()

def key_callback(window, key, scancode, action, mods):
    global PERSPECTIVE, HIERARCHY, WIRE

    if key == glfw.KEY_V:
        if action == glfw.PRESS:
            PERSPECTIVE = not PERSPECTIVE
    if key == glfw.KEY_H:
        if action == glfw.PRESS:
            HIERARCHY = not HIERARCHY
    if key == glfw.KEY_Z:
        if action == glfw.PRESS:
            WIRE = not WIRE

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
            gCamHeight += delta_Y/50

        else:
            gCamHeight -= delta_Y/50

        gCamHorizon -= delta_X/50

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

def drop_callback(window, paths):
    global DROP
    global gVertexArrayForMesh

    DROP = True
    gVertexArrayForMesh, faces, three_faces, four_faces, more_faces = parse_obj(paths[0])

    print('File name: ', paths[0])
    print('Total number of faces: ', faces)
    print('Number of faces with three vertices: ', three_faces)
    print('Number of faces with four vertices: ', four_faces)
    print('Number of faces with more than four vertifes: ', more_faces)

def parse_obj(path):

    varr = []
    vPositions = []
    vNormals = []

    faces = 0
    three_faces = 0
    four_faces = 0
    more_faces = 0

    obj_file = open(path, 'r')

    sentence = obj_file.readline()

    while sentence:
        sentence = sentence.split()
        if len(sentence) == 0:
            sentence = obj_file.readline()
            continue;
    
        mode = sentence[0]
        N_polygon = len(sentence)-1
        dimension = 3
        
        if mode == 'v':
            vPositions.append((float(sentence[1]), float(sentence[2]), float(sentence[3])))
        elif mode == 'vn':
            vNormals.append((float(sentence[1]), float(sentence[2]), float(sentence[3])))
        elif mode == 'f':
            for i in range(N_polygon-2):
                for j in range(dimension):
                    idx = 0
                    if j == 0:
                        idx = 1
                    else:
                        idx = i + j + 1

                    posNormPair = sentence[idx].split('/')
                    posIndex = int(posNormPair[0]) - 1
                    normIndex = int(posNormPair[2]) - 1

                    varr.append(vNormals[normIndex])
                    varr.append(vPositions[posIndex])

            if N_polygon == 3:
                three_faces += 1
            elif N_polygon == 4:
                four_faces += 1
            else:
                more_faces += 1
            faces += 1

        sentence = obj_file.readline()

    varr = np.array(varr, 'float32')

    obj_file.close()

    return varr, faces, three_faces, four_faces, more_faces


gVertexArrayIndexedForGrid = None
gIndexArrayForGrid = None

gVertexArrayForMesh = None

def main():
    global gVertexArrayIndexedForGrid, gIndexArrayForGrid

    if not glfw.init():
        return
    window = glfw.create_window(1200, 1200, "Solar System", None, None)
    if not window:
        glfw.terminate()
        return
    
    glfw.make_context_current(window)

    glfw.set_key_callback(window, key_callback)
    glfw.set_cursor_pos_callback(window, cursor_callback)
    glfw.set_mouse_button_callback(window, button_callback)
    glfw.set_scroll_callback(window, scroll_callback)
    glfw.set_drop_callback(window, drop_callback)

    gVertexArrayIndexedForGrid, gIndexArrayForGrid = createVertexAndIndexArrayForGrid()

    while not glfw.window_should_close(window):
        glfw.poll_events()

        render()

        glfw.swap_buffers(window)

    glfw.terminate()

if __name__ == "__main__":
    main()        
