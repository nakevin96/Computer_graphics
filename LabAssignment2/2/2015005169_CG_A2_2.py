import numpy as np
import glfw
from OpenGL.GL import *

ButtonPress='W'

def render(T) :
    posList = np.arange(0,361,30)
    glClear(GL_COLOR_BUFFER_BIT)
    glLoadIdentity()
    glBegin(GL_LINE_LOOP)
    for i in posList :
        glVertex2f(np.cos((i)*np.pi/180),np.sin((i)*np.pi/180))
    glEnd()
    glBegin(GL_LINE_LOOP)
    glVertex2f(0,0)
    if(T=='W') :
        glVertex2f(0,1)
    elif(T=='Q') :
        glVertex2f(np.cos((120)*np.pi/180),np.sin((120)*np.pi/180))
    elif(T=='0') :
        glVertex2f(np.cos((150)*np.pi/180),np.sin((150)*np.pi/180))
    else :
        glVertex2f(np.cos((90-(30)*(int(T)))*np.pi/180),np.sin((90-(30)*(int(T)))*np.pi/180))

    glEnd()


def key_callback(window, key, scancode, action, mods) :
    global ButtonPress
    if key==glfw.KEY_1:
        if action==glfw.PRESS :
            ButtonPress='1'
    elif key==glfw.KEY_2:
        if action==glfw.PRESS :
            ButtonPress='2'
    elif key==glfw.KEY_3:
        if action==glfw.PRESS :
            ButtonPress='3'
    elif key==glfw.KEY_4:
        if action==glfw.PRESS :
            ButtonPress='4'
    elif key==glfw.KEY_5:
        if action==glfw.PRESS :
            ButtonPress='5'
    elif key==glfw.KEY_6:
        if action==glfw.PRESS :
            ButtonPress='6'
    elif key==glfw.KEY_7:
        if action==glfw.PRESS :
            ButtonPress='7'
    elif key==glfw.KEY_8:
        if action==glfw.PRESS :
            ButtonPress='8'
    elif key==glfw.KEY_9:
        if action==glfw.PRESS :
            ButtonPress='9'
    elif key==glfw.KEY_0:
        if action==glfw.PRESS :
            ButtonPress='0'
    elif key==glfw.KEY_Q:
        if action==glfw.PRESS :
            ButtonPress='Q'
    elif key==glfw.KEY_W:
        if action==glfw.PRESS :
            ButtonPress='W'


    

def main() :
    if not glfw.init() :
        return

    window = glfw.create_window(480,480,"2015005169",None,None)
    if not window :
        glfw.terminate()
        return

    global ButtonPress
    glfw.set_key_callback(window,key_callback)
    glfw.make_context_current(window)

    while not glfw.window_should_close(window) :
        glfw.poll_events()

        render(ButtonPress)

        glfw.swap_buffers(window)
    
    glfw.terminate()

if __name__=="__main__" :
    main()
