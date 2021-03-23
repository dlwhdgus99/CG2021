import glfw
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np

keyboard = []

def render():
    glClear(GL_COLOR_BUFFER_BIT)
    glLoadIdentity()
    glBegin(GL_LINES)
    glColor3ub(255, 0, 0)
    glVertex2fv(np.array([0., 0.]))
    glVertex2fv(np.array([1., 0.]))
    glColor3ub(0, 255, 0)
    glVertex2fv(np.array([0., 0.]))
    glVertex2fv(np.array([0., 1.]))
    glEnd()
    
    glColor3ub(255, 255, 255)

    global keyboard
    size = len(keyboard)

    for i in reversed(range(size)):
        if keyboard[i] == 'Q':
            glTranslatef(-.1, 0., 0.)
        elif keyboard[i] == 'E':
            glTranslatef(.1, 0., 0.)
        elif keyboard[i] == 'A':
            glRotatef(10, 0, 0, 1)
        elif keyboard[i] == 'D':
            glRotatef(-10, 0, 0, 1)
        elif keyboard[i] == '1':
            glLoadIdentity()
            keyboard = []
            break

    drawTriangle()

def drawTriangle():
    glBegin(GL_TRIANGLES)
    glVertex2fv(np.array([0., .5]))
    glVertex2fv(np.array([0., 0.]))
    glVertex2fv(np.array([.5, 0.]))
    glEnd()

def key_callback(window, key, scancode, action, mods):
    global keyboard

    if key == glfw.KEY_Q:
        if action == glfw.PRESS or action == glfw.REPEAT:
            keyboard.append('Q')
    
    if key == glfw.KEY_E:
        if action == glfw.PRESS or action == glfw.REPEAT:
            keyboard.append('E')

    if key == glfw.KEY_A:
        if action == glfw.PRESS or action == glfw.REPEAT:
            keyboard.append('A')

    if key == glfw.KEY_D:
        if action == glfw.PRESS or action == glfw.REPEAT:
            keyboard.append('D')

    if key == glfw.KEY_1:
        if action == glfw.PRESS or action == glfw.REPEAT:
            keyboard.append('1')

def main():
    if not glfw.init():
        return
    window = glfw.create_window(480, 480, "2019057356", None, None)
    if not window:
        glfw.terminate()
        return

    glfw.set_key_callback(window, key_callback)
    glfw.make_context_current(window)

    while not glfw.window_should_close(window):
        glfw.poll_events()

        render()

        glfw.swap_buffers(window)

    glfw.terminate()

if __name__ == "__main__":
    main()

    
           
