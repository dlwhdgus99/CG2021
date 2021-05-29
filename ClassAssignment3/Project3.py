import glfw
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np
from OpenGL.arrays import vbo
import ctypes

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
WIRE = True
ANIMATE = False
SKELETON = True

bvh_hierarchy = []
bvh_motion = []
frame_index = 0

joint_list= ["Hips", "Spine", "Head", "LeftArm", "LeftForeArm", "LeftHand", "RightArm", "RightForeArm", "RightHand",
             "LeftUpLeg", "LeftLeg", "LeftFoot", "RightUpLeg", "RightLeg", "RightFoot"]
joint_varrs = []

def createVertexAndIndexArrayForGrid():
    x = np.arange(-500,500,10)
    z = np.arange(-500,500,10)
 
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
    global gCamAng_Azimuth, gCamAng_Elevation, dist, frame_index

    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glEnable(GL_DEPTH_TEST)

    if WIRE:
        glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
    else:
        glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)

    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()

    if PERSPECTIVE:
        gluPerspective(45, 1, 0.1, 10000)
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

    lightPos0 = (500., 10., 500., 1.)
    lightPos1 = (-500., 10., -500., 1.)
    lightPos2 = (0., 200., 0., 1.)

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
    if DROP:
        setObjectColor(.2, .2, .2)

        if ANIMATE:
            animate_bvh(frame_index)
            frame_index = (frame_index+1)%(len(bvh_motion)-3)
        else:
            draw_bvh()

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

def drawJoint(joint_name):
    global SKELETON

    SKELETON = True

    glScalef(1/45, 1/45, 1/45)

    if joint_name == "Spine":
        glScalef(60/50, 45/50, 45/50)

    elif joint_name == "Hips":
        glTranslatef(0, 7, 0)

    elif joint_name == "LeftUpLeg" or joint_name == "RightUpLeg":
        glScalef(1, 3/2, 1)
        glTranslatef(0, -6, 0)
        
    elif joint_name == "LeftLeg" or joint_name == "RightLeg":
        glTranslatef(0, -8, 0)
        glRotatef(-15, 1, 0, 0)

    elif joint_name == "LeftFoot" or joint_name == "RightFoot":
        glTranslatef(0, -3, 9)
        glRotatef(20, 1, 0, 0) 

    elif joint_name == "LeftArm":
        glTranslatef(7, -2, 0)
        glRotatef(100, 0, 0, 1)
        glRotatef(30, 0, 1, 0)

    elif joint_name == "LeftForeArm":
        glTranslatef(6, -2, 2)
        glRotatef(70, 0, 0, 1)
        glRotatef(100, 0, 1, 0)

    elif joint_name == "LeftHand":
        glTranslatef(5, -2, 2)
        glRotatef(90, 0, 0, 1)

    elif joint_name == "RightArm":
        glTranslatef(-7, -2, 0)
        glRotatef(-100, 0, 0, 1)
        glRotatef(-30, 0, 1, 0)

    elif joint_name == "RightForeArm":
        glTranslatef(-6, -2, 2)
        glRotatef(-70, 0, 0, 1)
        glRotatef(-100, 0, 1, 0)

    elif joint_name == "RightHand":
        glTranslatef(-5, -2, 2)
        glRotatef(-90, 0, 0, 1)

    joint_index = joint_list.index(joint_name)
    drawMesh_glDrawArray(joint_varrs[joint_index])

    if joint_name == "Spine":
        glScalef(50/60, 50/45, 50/45)
    
    elif joint_name == "Hips":
        glTranslatef(0, -7, 0)

    elif joint_name == "LeftUpLeg" or joint_name == "RightUpLeg":
        glTranslatef(0, 6, 0)
        glScalef(1, 2/3, 1)

    elif joint_name == "LeftLeg" or joint_name == "RightLeg":
        glRotatef(15, 1, 0, 0)
        glTranslatef(0, 8, 0)

    elif joint_name == "LeftFoot" or joint_name == "RightFoot":
        glRotatef(-20, 1, 0, 0)
        glTranslatef(0, 3, -9)

    elif joint_name == "LeftArm":
        glRotatef(-30, 0, 1, 0)
        glRotatef(-100, 0, 0, 1)
        glTranslatef(-7, 2, 0)

    elif joint_name == "LeftForeArm":
        glRotatef(-100, 0, 1, 0)
        glRotatef(-70, 0, 0, 1)
        glTranslatef(-6, 2, -2)

    elif joint_name == "LeftHand":
        glRotatef(-90, 0, 0, 1)
        glTranslatef(-5, 2, -2)

    elif joint_name == "RightArm":
        glRotatef(30, 0, 1, 0)
        glRotatef(100, 0, 0, 1)
        glTranslatef(7, 2, 0)

    elif joint_name == "RightForeArm":
        glRotatef(100, 0, 1, 0)
        glRotatef(70, 0, 0, 1)
        glTranslatef(6, 2, -2)

    elif joint_name == "RightHand":
        glRotatef(90, 0, 0, 1)
        glTranslatef(5, 2, -2)

    glScalef(45, 45, 45)

def setObjectColor(R, G, B):
    objectColor = (R, G, B)
    specularObjectColor = (1., 1., 1., 1.)
    glMaterialfv(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, objectColor)
    glMaterialfv(GL_FRONT, GL_SHININESS, 10)
    glMaterialfv(GL_FRONT, GL_SPECULAR, specularObjectColor)

def key_callback(window, key, scancode, action, mods):
    global PERSPECTIVE, WIRE, ANIMATE

    if key == glfw.KEY_V:
        if action == glfw.PRESS:
            PERSPECTIVE = not PERSPECTIVE
    if key == glfw.KEY_Z:
        if action == glfw.PRESS:
            WIRE = not WIRE
    if key == glfw.KEY_SPACE:
        if action == glfw.PRESS:
            ANIMATE = not ANIMATE

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
            gCamHeight += delta_Y/10

        else:
            gCamHeight -= delta_Y/10

        gCamHorizon -= delta_X/10

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
    global DROP, SKELETON, frame_index

    num_frame = 0
    FPS = 0
    num_joint = 0
    joint_names = []
    frame_index = 0

    DROP = True
    SKELETON = False
    num_frame, FPS, num_joint, joint_names = load_bvh(paths[0])

    print("File name: ", paths[0])
    print("Number of frames: ", num_frame)
    print("FPS: ", int(FPS))
    print("Number of joints: ", num_joint)
    print("-----List of all joint names-----")
    for i in range(len(joint_names)):
        print(i+1, ".", joint_names[i])

def parse_obj(path):

    varr = []
    vPositions = []
    vNormals = []

    faces = 0
    three_faces = 0
    four_faces = 0
    more_faces = 0

    obj_file = open(path, "r")

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

    return varr

def load_bvh(path):

    global bvh_hierarchy, bvh_motion
    bvh_hierarchy = []
    bvh_motion = []
    sentence = ''

    num_frame = 0
    FPS = 0
    num_joint = 0
    joint_names = []

    bvh_file = open(path, 'r')

    sentence = bvh_file.readline()
    while sentence and "MOTION" not in sentence:

        if "ROOT" in sentence or "JOINT" in sentence:
            num_joint += 1
            joint_name = sentence.split()[1]
            joint_names.append(joint_name)

        bvh_hierarchy.append(sentence)
        sentence = bvh_file.readline()

    while sentence:

        if "Frames" in sentence:
            num_frame = int(sentence.split()[1])

        if "Frame Time" in sentence:
            FPS = 1/float(sentence.split()[2])

        bvh_motion.append(sentence)
        sentence = bvh_file.readline()

    bvh_file.close()

    return num_frame, FPS, num_joint, joint_names


def XYZEulerMatrix(xang, yang, zang):

    xang = np.radians(xang)
    yang = np.radians(yang)
    zang = np.radians(zang)

    rotate_z = np.array([[np.cos(zang), -np.sin(zang), 0, 0],
                         [np.sin(zang), np.cos(zang), 0, 0],
                         [0, 0, 1, 0],
                         [0, 0, 0, 1]])

    rotate_x = np.array([[1, 0, 0, 0],
                         [0, np.cos(xang), -np.sin(xang), 0],
                         [0, np.sin(xang), np.cos(xang), 0],
                         [0, 0, 0, 1]])

    rotate_y = np.array([[np.cos(yang), 0, np.sin(yang), 0],
                         [0, 1, 0, 0],
                         [-np.sin(yang), 0, np.cos(yang), 0],
                         [0, 0, 0, 1]])
    
    return rotate_x @ rotate_y @ rotate_z

def ZXYEulerMatrix(zang, xang, yang):

    zang = np.radians(zang)
    xang = np.radians(xang)
    yang = np.radians(yang)

    rotate_z = np.array([[np.cos(zang), -np.sin(zang), 0, 0],
                         [np.sin(zang), np.cos(zang), 0, 0],
                         [0, 0, 1, 0],
                         [0, 0, 0, 1]])

    rotate_x = np.array([[1, 0, 0, 0],
                         [0, np.cos(xang), -np.sin(xang), 0],
                         [0, np.sin(xang), np.cos(xang), 0],
                         [0, 0, 0, 1]])

    rotate_y = np.array([[np.cos(yang), 0, np.sin(yang), 0],
                         [0, 1, 0, 0],
                         [-np.sin(yang), 0, np.cos(yang), 0],
                         [0, 0, 0, 1]])

    return rotate_z @ rotate_x @ rotate_y

def ZYXEulerMatrix(zang, yang, xang):

    zang = np.radians(zang)
    yang = np.radians(yang)
    xang = np.radians(xang)

    rotate_z = np.array([[np.cos(zang), -np.sin(zang), 0, 0],
                         [np.sin(zang), np.cos(zang), 0, 0],
                         [0, 0, 1, 0],
                         [0, 0, 0, 1]])

    rotate_y = np.array([[np.cos(yang), 0, np.sin(yang), 0],
                         [0, 1, 0, 0],
                         [-np.sin(yang), 0, np.cos(yang), 0],
                         [0, 0, 0, 1]])

    rotate_x = np.array([[1, 0, 0, 0],
                         [0, np.cos(xang), -np.sin(xang), 0],
                         [0, np.sin(xang), np.cos(xang), 0],
                         [0, 0, 0, 1]])

    return rotate_z @ rotate_y @ rotate_x

def draw_bvh():

    joint_name = ''

    for sentence in bvh_hierarchy:
        if "{" in sentence:
            glPushMatrix()

        elif "ROOT" in sentence or "JOINT" in sentence:
            joint_name = sentence.split()[1]

            if "ROOT" in sentence and not SKELETON:
                setObjectColor(.5, .2, 0)
                glScale(1/50, 1/50, 1/50)

        elif "OFFSET" in sentence:
            offset = sentence.split()[1:]
            offset_matrix = np.array([[1., 0., 0., float(offset[0])],
                                      [0., 1., 0., float(offset[1])],
                                      [0., 0., 1., float(offset[2])],
                                      [0., 0., 0., 1.]])

            cur_point = offset_matrix @ np.array([0., 0., 0., 1.])

            if joint_name not in joint_list and not SKELETON:
                glBegin(GL_LINES)
                glVertex3f(0, 0, 0)
                glVertex3f(cur_point[0], cur_point[1], cur_point[2])
                glEnd()

            glTranslatef(float(offset[0]), float(offset[1]), float(offset[2]))

            if joint_name in joint_list:
                drawJoint(joint_name)

        elif "}" in sentence:
            glPopMatrix()
        
        elif "End Site" in sentence:
            joint_name  = ''


def animate_bvh(frame_index):

    motion = bvh_motion[frame_index+3]
    motion = motion.split()
    channel_index = 0
    END = False

    offset_matrix = np.eye(4)
    prev_point = np.array([0., 0., 0., 1.])
    cur_point = np.array([0., 0., 0., 1.])

    XYZEulerMat = np.eye(4)
    ZXYEulerMat = np.eye(4)
    ZYXEulerMat = np.eye(4)

    joint_name = ''

    for sentence in bvh_hierarchy:
        if "{" in sentence:
            glPushMatrix()
        
        elif "ROOT" in sentence or "JOINT" in sentence:
            joint_name = sentence.split()[1]

            if "ROOT" in sentence and not SKELETON:
                setObjectColor(.5, .2, 0)
                glScale(1/50, 1/50, 1/50)

        elif "OFFSET" in sentence:
            offset = sentence.split()[1:]
            offset_matrix = np.array([[1., 0., 0., float(offset[0])],
                                      [0., 1., 0., float(offset[1])],
                                      [0., 0., 1., float(offset[2])],
                                      [0., 0., 0., 1.]])

            if END:
                cur_point = offset_matrix @ np.array([0., 0., 0., 1.])

                if not SKELETON:
                    glBegin(GL_LINES)
                    glVertex3f(0, 0, 0)
                    glVertex3f(cur_point[0], cur_point[1], cur_point[2])
                    glEnd()

                glTranslatef(float(offset[0]), float(offset[1]), float(offset[2]))

                END = False

        elif "CHANNELS" in sentence:

            sentence = sentence.split()
            num_channel = int(sentence[1])

            if num_channel == 6:
                glTranslatef(float(motion[channel_index]), (float)(motion[channel_index+1]), (float)(motion[channel_index+2]))

                if "X" in sentence[5]:
                    XYZEulerMat = XYZEulerMatrix(float(motion[channel_index+3]), float(motion[channel_index+4]), float(motion[channel_index+5]))
                    glMultMatrixf(XYZEulerMat.T)
                elif "Z" in sentence[5] and "X" in sentence[6]:
                    ZXYEulerMat = ZXYEulerMatrix(float(motion[channel_index+3]), float(motion[channel_index+4]), float(motion[channel_index+5]))
                    glMultMatrixf(ZXYEulerMat.T)
                else:
                    ZYXEulerMat = ZYXEulerMatrix(float(motion[channel_index+3]), float(motion[channel_index+4]), float(motion[channel_index+5]))
                    glMultMatrixf(ZYXEulerMat.T)

                if joint_name in joint_list:
                    drawJoint(joint_name)

            elif num_channel == 3:
                if "X" in sentence[2]:
                    XYZEulerMat = XYZEulerMatrix(float(motion[channel_index]), float(motion[channel_index+1]), float(motion[channel_index+2]))
                    cur_point = offset_matrix @ XYZEulerMat @ np.array([0., 0., 0., 1.])
                elif "Z" in sentence[2] and "X" in sentence[3]:
                    ZXYEulerMat = ZXYEulerMatrix(float(motion[channel_index]), float(motion[channel_index+1]), float(motion[channel_index+2]))
                    cur_point = offset_matrix @ ZXYEulerMat @ np.array([0., 0., 0., 1.])
                else:
                    ZYXEulerMat = ZYXEulerMatrix(float(motion[channel_index]), float(motion[channel_index+1]), float(motion[channel_index+2]))
                    cur_point = offset_matrix @ ZYXEulerMat @ np.array([0., 0., 0., 1.])

                if joint_name not in joint_list:
                    glBegin(GL_LINES)
                    glVertex3f(0, 0, 0)
                    glVertex3f(cur_point[0], cur_point[1], cur_point[2])
                    glEnd()
    
                glTranslatef(float(offset[0]), float(offset[1]), float(offset[2]))
                if "X" in sentence[2]:
                    glMultMatrixf(XYZEulerMat.T)
                elif "Z" in sentence[2] and "X" in sentence[3]:
                    glMultMatrixf(ZXYEulerMat.T)
                else:
                    glMultMatrixf(ZYXEulerMat.T)

                if joint_name in joint_list:
                    drawJoint(joint_name)

            channel_index += num_channel

        elif "}" in sentence:
            glPopMatrix()

        elif "End Site" in sentence:
            joint_name = ''
            END = True

gVertexArrayIndexedForGrid = None
gIndexArrayForGrid = None

gVertexArrayForMesh = None

def main():
    global gVertexArrayIndexedForGrid, gIndexArrayForGrid, joint_varrs
    i = 0

    if not glfw.init():
        return
    window = glfw.create_window(1200, 1200, "Bvh Viewer", None, None)
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

    for joint_name in joint_list:
        path = joint_name + ".obj"
        varr = parse_obj(path)
        joint_varrs.append(varr)

    while not glfw.window_should_close(window):
        glfw.swap_interval(1)
        glfw.poll_events()

        render()

        glfw.swap_buffers(window)

    glfw.terminate()

if __name__ == "__main__":
    main()        
