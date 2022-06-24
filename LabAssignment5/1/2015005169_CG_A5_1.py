import glfw
import numpy as np
from OpenGL.GL import *


def render(M, N):
    glClear(GL_COLOR_BUFFER_BIT)
    glLoadIdentity()

    #C : draw white triangle
    glColor3ub(255, 255, 255)
    drawTriangle()
    #C : draw global frame
    drawFrame()
    
    #transpose for glMultMatrixf
    M=M.transpose()
    N=N.transpose()

    glPushMatrix()
    glMultMatrixf(N)
    glMultMatrixf(M)
    glColor3ub(0, 0, 255)
    drawTriangle()
    drawFrame()

    glPopMatrix()
    glMultMatrixf(M)
    glMultMatrixf(N)
    glColor3ub(255, 0, 0)
    drawTriangle()
    drawFrame()

    




def drawFrame():
    glBegin(GL_LINES)
    glColor3ub(255, 0, 0)
    glVertex2fv(np.array([0., 0.]))
    glVertex2fv(np.array([1., 0.]))
    glColor3ub(0, 255, 0)
    glVertex2fv(np.array([0., 0.]))
    glVertex2fv(np.array([0., 1.]))
    glEnd()


def drawTriangle():
    glBegin(GL_TRIANGLES)
    glVertex2fv(np.array([0., .5]))
    glVertex2fv(np.array([0., 0.]))
    glVertex2fv(np.array([.5, 0.]))
    glEnd()


def main():

    if not glfw.init():
        return

    window = glfw.create_window(480, 480, "2015005169", None, None)
    if not window:
        glfw.terminate()
        return

    glfw.make_context_current(window)
    glfw.swap_interval(1)

    while not glfw.window_should_close(window):
        glfw.poll_events()
        r = (30 * np.pi) / 180
        M = np.identity(4)
        M[:3, :3] = np.array([[np.cos(r), -np.sin(r), 0.],
                              [np.sin(r),   np.cos(r), 0.],
                              [0.,         0.,         1.]])
        N = np.identity(4)
        N[:3, 3] = np.array([0.6, 0., 0.])

        render(M, N)

        glfw.swap_buffers(window)

    glfw.terminate()


if __name__ == "__main__":
    main()