import glfw
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np

def render(th):
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

    M_rotate = np.array([[np.cos(th), -np.sin(th), 0],
        [np.sin(th), np.cos(th), 0],
        [0,     0,      1]])
    M_translate_x = np.array([[1,    0,      .5],
        [0,     1,      0],
        [0,     0,      1]])
    M_translate_y = np.array([[1,    0,      0],
        [0,     1,      .5],
        [0,     0,      1]])

    M1 = M_rotate @ M_translate_x
    M2 = M_rotate @ M_translate_y

    
    glBegin(GL_POINTS)
    glVertex2fv((M1 @ np.array([.5, 0., 1])) [:-1])
    glVertex2fv((M2 @ np.array([0., .5, 1])) [:-1])
    glEnd()

    glBegin(GL_LINES)
    glVertex2fv((M1 @ np.array([0., 0., 0])) [:-1])
    glVertex2fv((M1 @ np.array([.5, 0., 0])) [:-1])
    glVertex2fv((M2 @ np.array([0., 0., 0])) [:-1])
    glVertex2fv((M2 @ np.array([0., .5, 0])) [:-1])
    glEnd()

def main():
    if not glfw.init():
        return
    window = glfw.create_window(480, 480, "2019057356", None, None)
    if not window:
        glfw.terminate()
        return

    glfw.make_context_current(window)

    while not glfw.window_should_close(window):
        glfw.poll_events()

        th = glfw.get_time()

        render(-th)

        glfw.swap_buffers(window)

    glfw.terminate()

if __name__ == "__main__":
    main()

    
           
