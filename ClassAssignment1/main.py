import glfw
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np

azimuth = 0.

stack_matrix = np.identity(4)
elav_stack_matrix = np.identity(4)
origin_xpos = 0.
origin_ypos = 0.
origin_panningx = 0.
origin_panningy = 0.
fov=45.0
projection_mode = 'P'

gVertexArray = None
gIndexArray = None

def create_vertex_array_index_array():
    varr = np.array([
             (-1, 1., 1.),     # v0
             (-1, 1, -1),     # v1
             (1, 1, -1),         # v2
             (1, 1, 1),           # v3
             (-1, -1, 1),           # v4
             (-1, -1, -1),         # v5
             (1, -1, -1),       # v6
             (1, -1, 1)          # v7
             ], 'float32')

    iarr = np.array([
             (0, 3, 2, 1),
             (0, 4, 7, 3),
             (0, 1, 5, 4),
             (1, 2, 6, 5),
             (2, 3, 7, 6),
             (6, 7, 4, 5)
             ])
    return varr, iarr

def drawFrame():
    glBegin(GL_LINES)
    glColor3ub(255, 0, 0)
    glVertex3fv(np.array([-4., 0., 0.]))
    glVertex3fv(np.array([4., 0., 0.]))
    glColor3ub(0, 255, 0)
    glVertex3fv(np.array([0., -2., 0.]))
    glVertex3fv(np.array([0., 2., 0.]))
    glColor3ub(0, 0, 255)
    glVertex3fv(np.array([0., 0., -4.]))
    glVertex3fv(np.array([0., 0., 4.]))
    glEnd()

    glColor3ub(255, 255, 255)
    for i in range(-15, 15):
        glBegin(GL_LINES)
        glVertex3fv(np.array([i, 0., 16.]))
        glVertex3fv(np.array([i, 0., -16.]))
        glVertex3fv(np.array([16., 0., i]))
        glVertex3fv(np.array([-16., 0., i]))
        glEnd()


def set_camera(first_eye):
    global stack_matrix, elav_stack_matrix

    glTranslate(0., -2, first_eye)
    x = elav_stack_matrix @ stack_matrix
    glMultMatrixf(x.T)



def cursor_callback(window, xpos, ypos):
    global origin_xpos, origin_ypos, azimuth, stack_matrix, elav_stack_matrix

    azimuth = -(np.radians(origin_xpos - xpos))/10
    elavation = -(np.radians(origin_ypos - ypos))/10
    origin_xpos = xpos
    origin_ypos = ypos
    a_matrix = np.array([[np.cos(azimuth),  0, np.sin(azimuth), 0],
                           [0,                1,               0, 0],
                           [-np.sin(azimuth), 0, np.cos(azimuth), 0],
                           [0,                0,               0, 1]])

    el_matrix = np.array([[1,               0,                0, 0],
                            [0, np.cos(elavation),  -np.sin(elavation), 0],
                            [0, np.sin(elavation),   np.cos(elavation), 0],
                            [0,               0,                0, 1]])

    stack_matrix = a_matrix @ stack_matrix
    elav_stack_matrix = el_matrix @ elav_stack_matrix



def cursor_callback2(window, xpos, ypos):
    global origin_panningx, origin_panningy, stack_matrix,elav_stack_matrix

    panningx = (- origin_panningx + xpos) / 100
    panningy = (- origin_panningy + ypos) / 100

    panX_matrix = np.array([[1, 0, 0, panningx],
                           [0, 1, 0, 0],
                           [0, 0, 1, 0],
                           [0, 0, 0, 1]])

    panY_matrix = np.array([[1, 0, 0, 0],
                           [0, 1, 0, -panningy],
                           [0, 0, 1, 0],
                           [0, 0, 0, 1]])


    origin_panningx = xpos
    origin_panningy = ypos

    stack_matrix = panX_matrix @ stack_matrix
    elav_stack_matrix = panY_matrix @ elav_stack_matrix

def cursor_callback_nothing(window, xpos, ypos):
    pass

def scroll_callback(window, xoffset, yoffset):
    global fov
    if fov >= 1.0 and fov <=120:
        fov -=yoffset
    if fov <=1.0:
        fov=1.0
    if fov >=120.0:
        fov=120.0

def button_callback(window, button, action, mod):
    global origin_xpos, origin_ypos, origin_panningx, origin_panningy

    if button == glfw.MOUSE_BUTTON_LEFT:
        if action == glfw.PRESS:
            (origin_xpos, origin_ypos) = glfw.get_cursor_pos(window)
            glfw.set_cursor_pos_callback(window, cursor_callback)
        elif action == glfw.RELEASE:
            glfw.set_cursor_pos_callback(window, cursor_callback_nothing)

    elif button == glfw.MOUSE_BUTTON_RIGHT:
        if action == glfw.PRESS:
            (origin_panningx, origin_panningy) = glfw.get_cursor_pos(window)
            glfw.set_cursor_pos_callback(window, cursor_callback2)

        elif action == glfw.RELEASE:
            glfw.set_cursor_pos_callback(window, cursor_callback_nothing)

def key_callback(window, key, scancode, action, mods):
    global projection_mode
    if action == glfw.PRESS:
        if key == glfw.KEY_V:
            if projection_mode=='P':
                projection_mode='O'
            elif projection_mode=='O':
                projection_mode='P'
           


def render():
    global projection_mode,fov,gVertexArray, gIndexArray
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glEnable(GL_DEPTH_TEST)
    glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)

    # projection
    if projection_mode == 'P':
        glLoadIdentity()
        gluPerspective(fov, 1.2, 1, 100)
    elif projection_mode == 'O':
        glLoadIdentity()
        fov_o = fov/5
        glOrtho(-fov_o,fov_o, -fov_o,fov_o, -25,25)

    set_camera(-10)

    # redering model
    drawFrame()
    glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
    glColor3ub(255, 255, 255)
    
    varr = gVertexArray
    iarr = gIndexArray
    glEnableClientState(GL_VERTEX_ARRAY)
    glVertexPointer(3, GL_FLOAT, 3 * varr.itemsize, varr)
    glDrawElements(GL_QUADS, iarr.size, GL_UNSIGNED_INT, iarr)

def main():
    global gVertexArray, gIndexArray
    
    if not glfw.init():
        return
    window = glfw.create_window(800, 800, 'classassignment1', None, None)
    if not window:
        glfw.terminate()
        return

    glfw.set_key_callback(window, key_callback)
    glfw.set_mouse_button_callback(window, button_callback)
    glfw.make_context_current(window)
    glfw.set_scroll_callback(window, scroll_callback)

    glfw.swap_interval(1)
    gVertexArray, gIndexArray = create_vertex_array_index_array()

    while not glfw.window_should_close(window):
        glfw.poll_events()
        render()
        glfw.swap_buffers(window)

    glfw.terminate()


if __name__ == "__main__":
    main()