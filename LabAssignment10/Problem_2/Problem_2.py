import glfw
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np
from OpenGL.arrays import vbo

gCamAng = 0.
gCamHeight = 1.


def createVertexAndIndexArrayIndexed():
    varr = np.array([
            ( -0.5773502691896258 , 0.5773502691896258 ,  0.5773502691896258 ),
            ( -1 ,  1 ,  1 ), # v0
            ( 0.8164965809277261 , 0.4082482904638631 ,  0.4082482904638631 ),
            (  1 ,  1 ,  1 ), # v1
            ( 0.4082482904638631 , -0.4082482904638631 ,  0.8164965809277261 ),
            (  1 , -1 ,  1 ), # v2
            ( -0.4082482904638631 , -0.8164965809277261 ,  0.4082482904638631 ),
            ( -1 , -1 ,  1 ), # v3
            ( -0.4082482904638631 , 0.4082482904638631 , -0.8164965809277261 ),
            ( -1 ,  1 , -1 ), # v4
            ( 0.4082482904638631 , 0.8164965809277261 , -0.4082482904638631 ),
            (  1 ,  1 , -1 ), # v5
            ( 0.5773502691896258 , -0.5773502691896258 , -0.5773502691896258 ),
            (  1 , -1 , -1 ), # v6
            ( -0.8164965809277261 , -0.4082482904638631 , -0.4082482904638631 ),
            ( -1 , -1 , -1 ), # v7
            ], 'float32')
    iarr = np.array([
            (0,2,1),
            (0,3,2),
            (4,5,6),
            (4,6,7),
            (0,1,5),
            (0,5,4),
            (3,6,2),
            (3,7,6),
            (1,2,6),
            (1,6,5),
            (0,7,3),
            (0,4,7),
            ])
    return varr, iarr

def drawCube_glDrawElements():
    global gVertexArrayIndexed, gIndexArray
    varr = gVertexArrayIndexed
    iarr = gIndexArray
    glEnableClientState(GL_VERTEX_ARRAY)
    glEnableClientState(GL_NORMAL_ARRAY)
    glNormalPointer(GL_FLOAT, 6*varr.itemsize, varr)
    glVertexPointer(3, GL_FLOAT, 6*varr.itemsize, ctypes.c_void_p(varr.ctypes.data + 3*varr.itemsize))
    glDrawElements(GL_TRIANGLES, iarr.size, GL_UNSIGNED_INT, iarr)

def drawFrame():
    glBegin(GL_LINES)
    glColor3ub(255, 0, 0)
    glVertex3fv(np.array([0.,0.,0.]))
    glVertex3fv(np.array([3.,0.,0.]))
    glColor3ub(0, 255, 0)
    glVertex3fv(np.array([0.,0.,0.]))
    glVertex3fv(np.array([0.,3.,0.]))
    glColor3ub(0, 0, 255)
    glVertex3fv(np.array([0.,0.,0]))
    glVertex3fv(np.array([0.,0.,3.]))
    glEnd()

def l2norm(v):
    return np.sqrt(np.dot(v,v))

def normalized(v):
    l = l2norm(v)
    return (1/l) * np.array(v)

def exp(rv):
    th = l2norm(rv)

    if not th:
        ux = uy = uz = 0
    else:
        ux, uy, uz = normalized(rv)
       
    R = np.array([[np.cos(th) + ux*ux*(1-np.cos(th)), ux*uy*(1-np.cos(th)) - uz*np.sin(th), ux*uz*(1-np.cos(th)) + uy*np.sin(th)],
                  [uy*ux*(1-np.cos(th)) + uz*np.sin(th), np.cos(th) + uy*uy*(1-np.cos(th)), uy*uz*(1-np.cos(th)) - ux*np.sin(th)],
                  [uz*ux*(1-np.cos(th)) - uy*np.sin(th), uz*uy*(1-np.cos(th)) + ux*np.sin(th), np.cos(th) + uz*uz*(1-np.cos(th))]])

    return (R)

def log(R):
    if np.trace(R) == 3:
        u = np.array([0, 0, 0])
    elif np.trace(R) == -1:
        if((R[0][2] != 0) or (R[1][2] != 0) or (R[2][2] + 1 != 0)):
            u = np.array([R[0][2], R[1][2], R[2][2] + 1])/(np.sqrt(2*(1 + R[2][2])))
        elif (R[0][1] != 0) or (R[1][1] + 1 != 0) or (R[2][1] != 0):
            u = np.array([R[0][1], R[1][1] + 1, R[2][1]])/(np.sqrt(2*(1 + R[1][1])))
        else:
            u = np.array([R[0][0] + 1, R[1][0], R[2][0]])/(np.sqrt(2*(1 + R[0][0])))
    else:
        th = np.arccos((np.trace(R) - 1)/2)*(np.pi/2)
        ux = (R[2][1] - R[1][2])/(2*np.sin(th))
        uy = (R[0][2] - R[2][0])/(2*np.sin(th))
        uz = (R[1][0] - R[0][1])/(2*np.sin(th))
        u = np.array([ux, uy, uz])

    return u

def slerp(R1, R2, t):
    slerp = R1@exp(t*log((R1.T) @ R2))

    return slerp

frame = 0
def render():
    global gCamAng, gCamHeight, frame
    glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)
    glEnable(GL_DEPTH_TEST)

    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45, 1, 1,10)

    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    gluLookAt(5*np.sin(gCamAng),gCamHeight,5*np.cos(gCamAng), 0,0,0, 0,1,0)

    # draw global frame
    drawFrame()

    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)

    glEnable(GL_RESCALE_NORMAL)

    lightPos = (3.,4.,5.,1.)
    glLightfv(GL_LIGHT0, GL_POSITION, lightPos)

    lightColor = (1.,1.,1.,1.)
    ambientLightColor = (.1,.1,.1,1.)
    glLightfv(GL_LIGHT0, GL_DIFFUSE, lightColor)
    glLightfv(GL_LIGHT0, GL_SPECULAR, lightColor)
    glLightfv(GL_LIGHT0, GL_AMBIENT, ambientLightColor)
    
    T = np.eye(4)
    T[0][3] = 1
    M1 = np.eye(4)
    M2 = np.eye(4)

    setObjectColor(1, 0, 0)
    First_R1 = XYZEuler(np.radians(20), np.radians(30), np.radians(30))
    First_R2 = XYZEuler(np.radians(15), np.radians(30), np.radians(25))
    M1[:3, :3] = First_R1
    M2[:3, :3] = First_R2
    drawObject(M1, M2)

    setObjectColor(1,1,0)
    Second_R1 = XYZEuler(np.radians(45), np.radians(60), np.radians(40))
    Second_R2 = XYZEuler(np.radians(25), np.radians(40), np.radians(40))
    M1[:3, :3] = Second_R1
    M2[:3, :3] = Second_R2
    drawObject(M1, M2)

    setObjectColor(0,1,0)
    Third_R1 = XYZEuler(np.radians(60), np.radians(70), np.radians(50))
    Third_R2 = XYZEuler(np.radians(40), np.radians(60), np.radians(50))
    M1[:3, :3] = Third_R1
    M2[:3, :3] = Third_R2
    drawObject(M1, M2)

    setObjectColor(0, 0, 1)
    Fourth_R1 = XYZEuler(np.radians(80), np.radians(85), np.radians(70))
    Fourth_R2 = XYZEuler(np.radians(55), np.radians(80), np.radians(65))
    M1[:3, :3] = Fourth_R1
    M2[:3, :3] = Fourth_R2
    drawObject(M1, M2)

    if frame <= 20:
        t = frame/20.0
        setObjectColor(1,1,1)
        R1 = slerp(First_R1, Second_R1, t)
        R2 = slerp(First_R2, Second_R2, t)
        M1[:3, :3] = R1
        M2[:3, :3] = R2
        drawObject(M1, M2)
    elif 20 < frame and frame <= 40:
        t = (frame-21)/24.0
        setObjectColor(1, 1, 1)
        R1 = slerp(Second_R1, Third_R1, t)
        R2 = slerp(Second_R2, Third_R2, t)
        M1[:3, :3] = R1
        M2[:3, :3] = R2
        drawObject(M1, M2)
    else:
        t = (frame-41)/19.0
        setObjectColor(1, 1, 1)
        R1 = slerp(Third_R1, Fourth_R1, t)
        R2 = slerp(Third_R2, Fourth_R2, t)
        M1[:3, :3] = R1
        M2[:3, :3] = R2
        drawObject(M1, M2)

    frame += 1
    frame = frame % 61
    glDisable(GL_LIGHTING)

def setObjectColor(R, G, B):
    objectColor = (R, G, B)
    specularObjectColor = (1., 1., 1., 1.)
    glMaterialfv(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, objectColor)
    glMaterialfv(GL_FRONT, GL_SHININESS, 10)
    glMaterialfv(GL_FRONT, GL_SPECULAR, specularObjectColor)

def drawObject(R1, R2):
    J1 = R1
   
    glPushMatrix()
    glMultMatrixf(J1.T)
    glPushMatrix()
    glTranslatef(0.5,0,0)
    glScalef(0.5, 0.05, 0.05)
    drawCube_glDrawElements()
    glPopMatrix()
    glPopMatrix()

    T1 = np.identity(4)
    T1[0][3] = 1.

    J2 = R1 @ T1 @ R2

    glPushMatrix()
    glMultMatrixf(J2.T)
    glPushMatrix()
    glTranslatef(0.5,0,0)
    glScalef(0.5, 0.05, 0.05)
    drawCube_glDrawElements()
    glPopMatrix()
    glPopMatrix()

def XYZEuler(xang, yang, zang):
    X = np.array([[1, 0, 0],
                 [0, np.cos(xang), -np.sin(xang)],
                 [0, np.sin(xang), np.cos(xang)]])
    Y = np.array([[np.cos(yang), 0, np.sin(yang)],
                  [0, 1, 0],
                  [-np.sin(yang), 0, np.cos(yang)]])
    Z = np.array([[np.cos(zang), -np.sin(zang), 0],
                  [np.sin(zang), np.cos(zang), 0],
                  [0, 0, 1]])

    return X@Y@Z

def key_callback(window, key, scancode, action, mods):
    global gCamAng, gCamHeight
    # rotate the camera when 1 or 3 key is pressed or repeated
    if action==glfw.PRESS or action==glfw.REPEAT:
        if key==glfw.KEY_1:
            gCamAng += np.radians(-10)
        elif key==glfw.KEY_3:
            gCamAng += np.radians(10)
        elif key==glfw.KEY_2:
            gCamHeight += .1
        elif key==glfw.KEY_W:
            gCamHeight += -.1

gVertexArrayIndexed = None
gIndexArray = None

def main():
    global gVertexArrayIndexed, gIndexArray
    if not glfw.init():
        return
    window = glfw.create_window(640,640,'2019057356', None,None)
    if not window:
        glfw.terminate()
        return
    glfw.make_context_current(window)
    glfw.set_key_callback(window, key_callback)
    glfw.swap_interval(1)

    gVertexArrayIndexed, gIndexArray = createVertexAndIndexArrayIndexed()

    while not glfw.window_should_close(window):
        glfw.poll_events()
        
        #t = glfw.get_time()
        render()

        glfw.swap_buffers(window)

    glfw.terminate()

if __name__ == "__main__":
    main()

