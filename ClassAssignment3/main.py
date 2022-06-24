import glfw
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np
import os

#for moving variables / mouse right click, left click, scroll action
stack_matrix = np.identity(4)
elav_stack_matrix = np.identity(4)
origin_xpos = 0.
origin_ypos = 0.
origin_panningx = 0.
origin_panningy = 0.
fov=45.0
origin_zoom = 0.
zoom =0.
# projection mode
# Press v : using perspective or Orthogonal default is Perspective mode
projection_mode = 'P'

motion_arr = []
bvh_info=[]
num_of_joints=0
num_of_frames=0
FPS =0
joints_name=[]
animate_motion = 'OFF'
animate_start_time = 0
model_count=0
scale_modifier = 1.0


def drawLine(vertex):
    glColor3ub(0, 191, 255)
    glBegin(GL_LINES)
    glVertex3f(0.,0.,0.)
    glVertex3fv(vertex)
    glEnd()
    
def drawCube(offset, norm,joint):
    tmp =np.array([0.77,0.77,0.8])
    offset = offset * tmp
    glBegin(GL_QUADS)

    glNormal3f(norm[0], 0, 0)
    glVertex3f(offset[0], offset[1], - offset[2])
    glVertex3f(offset[0], offset[1], offset[2])
    glVertex3f(offset[0], - offset[1], offset[2])
    glVertex3f(offset[0], - offset[1], - offset[2])

    glNormal3f(-norm[0], 0, 0)
    glVertex3f(- offset[0], offset[1], offset[2])
    glVertex3f(- offset[0], offset[1], - offset[2])
    glVertex3f(- offset[0], - offset[1], - offset[2])
    glVertex3f(- offset[0], - offset[1], offset[2])

    glNormal3f(0, norm[1], 0)
    glVertex3f(offset[0], offset[1], - offset[2])
    glVertex3f(- offset[0], offset[1], - offset[2])
    glVertex3f(- offset[0], offset[1], offset[2])
    glVertex3f(offset[0], offset[1], offset[2])

    glNormal3f(0, -norm[1], 0)
    glVertex3f(offset[0], - offset[1], offset[2])
    glVertex3f(- offset[0], - offset[1], offset[2])
    glVertex3f(- offset[0], - offset[1], - offset[2])
    glVertex3f(offset[0], - offset[1], - offset[2])

    glNormal3f(0, 0, norm[2])
    glVertex3f(offset[0], offset[1], offset[2])
    glVertex3f(- offset[0], offset[1], offset[2])
    glVertex3f(- offset[0], - offset[1], offset[2])
    glVertex3f(offset[0], - offset[1], offset[2])

    glNormal3f(0, 0, -norm[2])
    glVertex3f(offset[0], - offset[1], - offset[2])
    glVertex3f(- offset[0], - offset[1], - offset[2])
    glVertex3f(- offset[0], offset[1], - offset[2])
    glVertex3f(offset[0], offset[1], - offset[2])

    glEnd()

def drawFrame():
    glBegin(GL_LINES)
    glColor3ub(255, 0, 0)
    glVertex3fv(np.array([-100., 0., 0.]))
    glVertex3fv(np.array([100., 0., 0.]))
    glColor3ub(0, 255, 0)
    glVertex3fv(np.array([0., -2., 0.]))
    glVertex3fv(np.array([0., 2., 0.]))
    glColor3ub(0, 0, 255)
    glVertex3fv(np.array([0., 0., -100.]))
    glVertex3fv(np.array([0., 0., 100.]))
    glEnd()
    for i in range(-100, 100):
        glColor3ub(100, 100, 100)
        if i%10 == 0:
            glColor3ub(255,255,255)
        elif i%5==0:
            glColor3ub(160,160,160)
        glBegin(GL_LINES)
        glVertex3fv(np.array([i, 0., 100.]))
        glVertex3fv(np.array([i, 0., -100.]))
        glVertex3fv(np.array([100., 0., i]))
        glVertex3fv(np.array([-100., 0., i]))
        glEnd()

def set_camera(first_eye):
    global stack_matrix, elav_stack_matrix, zoom

    glTranslate(0., -2, first_eye+zoom)
    x = elav_stack_matrix @ stack_matrix
    glMultMatrixf(x.T)

def cursor_callback(window, xpos, ypos):
    global origin_xpos, origin_ypos, stack_matrix, elav_stack_matrix

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
    global fov, zoom, origin_zoom, projection_mode
    if projection_mode =='P':
        if fov >= 1.0 and fov <=90:
            fov -=yoffset
        if fov <=1.0:
            fov=1.0
            zoom=0.
        if fov >=90.0:
            fov=90.0
            zoom -= (origin_zoom - yoffset)/10
    elif projection_mode=='O':
        if fov >= 1.0 and fov <=170:
            fov -=yoffset
        if fov <=1.0:
            fov=1.0
        if fov >=170.0:
            fov=170.0
    
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
    global projection_mode, animate_motion, animate_start_time,scale_modifier
    if action == glfw.PRESS or action == glfw.REPEAT:
        if key == glfw.KEY_V:
            if projection_mode=='P':
                projection_mode='O'
            elif projection_mode=='O':
                projection_mode='P'
        elif key == glfw.KEY_SPACE:
            if animate_motion=='OFF':
                animate_motion='ON'
                animate_start_time = glfw.get_time()
            else:
                animate_motion='OFF'
                animate_start_time=0
        elif key == glfw.KEY_1 :
            scale_modifier -= 0.02
            if(scale_modifier <0.02):
                scale_modifier =0.02
        elif key == glfw.KEY_2 :
            scale_modifier =1.0      
        elif key == glfw.KEY_3 :
            scale_modifier += 0.02

def drop_callback(window, paths):
    global motion_arr,bvh_info,num_of_joints,joints_name,FPS,num_of_frames,animate_motion

    #initiate variable
    animate_motion='OFF'
    motion_arr =[]
    bvh_info=[]
    FPS=0
    joints_name=[]
    num_of_joints=0
    file_name=''
    num_of_frames=0 

    names = paths[0].split('\\')
    file_name = names[len(names) -1]
    f = open(paths[0],"r")

    line = f.readline()
    if not line:
        print('ERROR NO DATA')

    line = line.strip()
    tag = line.split(' ')

    if tag[0] == 'HIERARCHY':
        line = f.readline()
        line = line.strip()
        root = line.split(' ')
        joints_name.append(root[1])
        num_of_joints+=1
        line = f.readline()
        bvh_info = make_hierarchy_array(f,'N')
    else:
        print("bvh file format error..")
        return
    #from this line we will make Motion array 
    line = f.readline()
    line = f.readline()
    tmp = ' '.join(line.split())
    numframe = tmp.split(' ')
    num_of_frames = int(numframe[1])

    line = f.readline()
    tmp = ' '.join(line.split())
    frametime = tmp.split(' ')
    FPS = 1 / np.float32(frametime[2])
    
    while True:
        motion_tmp = []
        line = f.readline()
        if not line:
            break
        tmp = ' '.join(line.split())
        motion = tmp.split(' ')
        for i in range(len(motion)):
            motion_tmp.append(np.float32(motion[i]))
        motion_arr.append(motion_tmp)
    print("File name : ", file_name)
    print("Number of frames : ", num_of_frames)
    print("FPS : ", FPS)
    print("Number of joints : ", num_of_joints)
    print("List of all joint names : ", joints_name)
    f.close()
        
    
def make_hierarchy_array(f,label) :
    global num_of_joints,joints_name
    joint_info=[]
    joint_info.append(label)
    next_label = label

    while True:
        line = f.readline()
        if not line:
            break
        line = line.strip()
        tag = line.split(' ',1)
        
        if tag[0] == 'OFFSET' :
            tmp_off = tag[1].split(' ')
            off_arr = np.array([np.float32(tmp_off[0]),np.float32(tmp_off[1]),np.float32(tmp_off[2])])
            joint_info.append(off_arr)
        elif tag[0] == 'CHANNELS' :
            chan = tag[1].split(' ')
            joint_info.append(chan)
        elif tag[0] == '{' :
            child_joint = make_hierarchy_array(f,next_label)
            joint_info.append(child_joint)
        elif tag[0] == '}' :
            return joint_info
        elif tag[0] == 'JOINT' :
            joints_name.append(tag[1])
            num_of_joints +=1
            next_label=tag[1].upper()
        elif tag[0].upper() == 'END':
            next_label='END'
        
def make_cube_info(offset):
    len = 0.16*getlength(offset)
    lenx =len * 0.7
    if(lenx <0.02):
        lenx =0.02
    lenz =len * 1.6
    tmp = [0., 0., 0.]
    if offset[0] >= 0:
        tmp[0] = offset[0] + lenx
    elif offset[0] < 0:
        tmp[0] = offset[0] - lenx
    if offset[1] >= 0:
        tmp[1] = offset[1] + len
    elif offset[1] < 0:
        tmp[1] = offset[1] - len
    if offset[2] >= 0:
        tmp[2] = offset[2] + lenz
    elif offset[2] < 0:
        tmp[2] = offset[2] - lenz
    norm = [tmp[0]/abs(tmp[0]), tmp[1]/abs(tmp[1]), tmp[2]/abs(tmp[2])]

    return tmp, norm

def getlength(offset):
    x = offset[0]**2
    y = offset[1]**2
    z = offset[2]**2
    result = (x+y+z)**(1/2)
    return result

def drawbvh(bvh_info_arr):
    global animate_motion,FPS,motion_arr,animate_start_time,num_of_frames,model_count

    if not bvh_info_arr :
        return
    isEnd = bvh_info_arr[0]
    offset = bvh_info_arr[1]

    glPushMatrix()
    #drawLine(offset)
    #glTranslate(offset[0], offset[1], offset[2])
    tmp = [offset[0]/2, offset[1]/2, offset[2]/2]
    tmp_off, norm = make_cube_info(tmp)
    glTranslate(offset[0]/2, offset[1]/2, offset[2]/2)
    drawCube(tmp_off, norm,isEnd)
    glTranslate(offset[0]/2, offset[1]/2, offset[2]/2)
    t= glfw.get_time()
    current_frame = int(((t-animate_start_time)*FPS)%num_of_frames) 

    if isEnd !='END': 
        chan = bvh_info_arr[2]
        if animate_motion == 'ON':
            for i in range(int(chan[0])):
                if chan[i+1].upper() == 'XPOSITION':
                    trans_x = motion_arr[current_frame][model_count]
                    model_count +=1
                    glTranslate(trans_x,0,0)
                elif chan[i+1].upper() == 'YPOSITION':
                    trans_y = motion_arr[current_frame][model_count]
                    model_count +=1
                    glTranslate(0,trans_y,0)
                elif chan[i+1].upper() == 'ZPOSITION':
                    trans_z = motion_arr[current_frame][model_count]
                    model_count +=1
                    glTranslate(0,0,trans_z)
                elif chan[i+1].upper() == 'XROTATION':
                    rotate_x = motion_arr[current_frame][model_count]
                    model_count +=1
                    glRotate(rotate_x,1,0,0)
                elif chan[i+1].upper() == 'YROTATION':
                    rotate_y = motion_arr[current_frame][model_count]
                    model_count +=1
                    glRotate(rotate_y,0,1,0)
                elif chan[i+1].upper() == 'ZROTATION':
                    rotate_z = motion_arr[current_frame][model_count]
                    model_count +=1
                    glRotate(rotate_z,0,0,1)
        for i in range(len(bvh_info_arr)-3):
            drawbvh(bvh_info_arr[i+3])
    glPopMatrix()

    

def render():
    global projection_mode,fov,bvh_info,model_count, scale_modifier
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glEnable(GL_DEPTH_TEST)

    # projection Mode : Perspective or glOrtho
    if projection_mode == 'P':
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(fov, 1.2, 1, 100)
    elif projection_mode == 'O':
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        fov_o = fov/5
        glOrtho(-fov_o,fov_o, -fov_o,fov_o, -100,100)

    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    set_camera(-10)

    # redering model
    drawFrame()
    # lighting
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
	
    glEnable(GL_NORMALIZE)
    glPushMatrix()
    t =glfw.get_time()
    lightPos = (3*np.cos(t),3.,3*np.sin(t),1.)
    glLightfv(GL_LIGHT0, GL_POSITION, lightPos)
    glPopMatrix()
    
    LightColor = (1., 1., 1., 1.)
    ambientLightColor = (.1,.1,.1,1.)
    glLightfv(GL_LIGHT0, GL_DIFFUSE, LightColor)
    glLightfv(GL_LIGHT0, GL_SPECULAR, LightColor)
    glLightfv(GL_LIGHT0, GL_AMBIENT, ambientLightColor)
    
    ObjectColor = (0., 0.6, 1., 1.)
    specularObjectColor = (1.,1.,1.,1.)
    glMaterialfv(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, ObjectColor)
    glMaterialfv(GL_FRONT, GL_SHININESS, 50)
    glMaterialfv(GL_FRONT, GL_SPECULAR, specularObjectColor)

    glPushMatrix()
    glScalef(scale_modifier,scale_modifier,scale_modifier)
    model_count =0
    drawbvh(bvh_info)
    glPopMatrix()
    
    glDisable(GL_LIGHTING)
     

def main(): 
    if not glfw.init():
        return
    window = glfw.create_window(800, 800, 'classassignment3', None, None)
    if not window:
        glfw.terminate()
        return

    glfw.set_key_callback(window, key_callback)
    glfw.set_mouse_button_callback(window, button_callback)
    glfw.make_context_current(window)
    glfw.set_scroll_callback(window, scroll_callback)
    glfw.set_drop_callback(window, drop_callback)

    glfw.swap_interval(1)

    while not glfw.window_should_close(window):
        glfw.poll_events()
        render()
        glfw.swap_buffers(window)

    glfw.terminate()

if __name__ == "__main__":
    main()