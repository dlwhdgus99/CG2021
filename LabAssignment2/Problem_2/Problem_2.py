import numpy as np
import glfw
from OpenGL.GL import *

keyboard_input = ''

def render():
    glClear(GL_COLOR_BUFFER_BIT)
    glLoadIdentity()
    glBegin(GL_LINE_LOOP)

    degree = np.linspace(0,(11/6)*np.pi,12)

    for i in range(0,12):
        x_coordinate = np.cos(degree[i])
        y_coordinate = np.sin(degree[i])
        glVertex2f(x_coordinate, y_coordinate)

    glEnd()
    
    if keyboard_input == '0':
        degree = (5/6)*np.pi

    elif keyboard_input == 'Q':
        degree = (2/3)*np.pi

    elif keyboard_input == 'W' or keyboard_input == '':
        degree = (1/2)*np.pi

    else:
        degree = (-int(keyboard_input)/6 + 1/2)*np.pi
    
    x_coordinate = np.cos(degree)
    y_coordinate = np.sin(degree)

    glBegin(GL_LINES)
    glVertex2f(0.0, 0.0)
    glVertex2f(x_coordinate, y_coordinate)
    glEnd()

def key_callback(window, key, scancode, action, mods):

    global keyboard_input

    if key==glfw.KEY_1:
        if action==glfw.PRESS:
            keyboard_input = '1'

    elif key==glfw.KEY_2:
        if action==glfw.PRESS:
            keyboard_input = '2'

    elif key==glfw.KEY_3:
        if action==glfw.PRESS:
            keyboard_input = '3'

    elif key==glfw.KEY_4:
        if action==glfw.PRESS:
            keyboard_input = '4'

    elif key==glfw.KEY_5:
        if action==glfw.PRESS:
            keyboard_input = '5'

    elif key==glfw.KEY_6:
        if action==glfw.PRESS:
            keyboard_input = '6'

    elif key==glfw.KEY_7:
        if action==glfw.PRESS:
            keyboard_input = '7'

    elif key==glfw.KEY_8:
        if action==glfw.PRESS:
            keyboard_input = '8'

    elif key==glfw.KEY_9:
        if action==glfw.PRESS:
            keyboard_input = '9'

    elif key==glfw.KEY_0:
        if action==glfw.PRESS:
            keyboard_input = '0'

    elif key==glfw.KEY_Q:
        if action==glfw.PRESS:
            keyboard_input = 'Q'

    elif key==glfw.KEY_W:
        if action==glfw.PRESS:
            keyboard_input = 'W'
            

def main():
    if not glfw.init():
        return
    
    window = glfw.create_window(480,480, "2019057356", None, None)
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

