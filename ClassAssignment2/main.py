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
# Press s : using obj normal <-> smooth shading
# 1: forced smooth shading 0: using obj normal data
shading_mode = 1
# Press z : Toggle wirefram <-> solid mode
# 1: solid mode 0: wire fram
polygon_fill_mode = 1
# Press h : Toggle animation mode <-> obj drop mode
animation_mode = 2
# for forced smooth shading normal array
smooth_shading_array = None
bind_normalV_vertex_array = None
# the variables for save hierarchy animation obj information
ssarray=[]
bnvarray=[]

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
    global projection_mode, polygon_fill_mode, shading_mode, animation_mode
    if action == glfw.PRESS or action == glfw.REPEAT:
        if key == glfw.KEY_V:
            if projection_mode=='P':
                projection_mode='O'
            elif projection_mode=='O':
                projection_mode='P'
        # Push z>> 1: solid mode 0: wire frame
        if key == glfw.KEY_Z:
            if polygon_fill_mode==0:
                polygon_fill_mode=1
            else:
                polygon_fill_mode = 0
        # Push S>> 1: forced smooth shading 0: using obj normal data
        if key == glfw.KEY_S:
            if shading_mode == 1:
                shading_mode =0
            else:
                shading_mode =1
        if key == glfw.KEY_H:
            if animation_mode == 0:
                animation_mode =1
            else:
                animation_mode =0

# the function for obj file read
def drop_callback(window, paths):
    global animation_mode,smooth_shading_array, bind_normalV_vertex_array
    animation_mode =0
    smooth_shading_array, bind_normalV_vertex_array=define_arrays(paths[0])

def define_arrays(paths):
    global animation_mode
    vncount=0
    v_arr = []
    n_arr = []
    face_i_arr = []
    face_normals = []
    #separate paths[0] to get file name
    names = paths.split('\\')
    f_name = names[len(names) - 1]
    
    #file open
    f = open(paths, "r")
    total_triangle_num=0
    triangle_num = 0
    quad_num = 0
    face_over4v_num = 0
    
    while True:
        line = f.readline()
        #file is end, break
        if not line:
            break

        line = line.rstrip()
        line = line.replace('  ', ' ')
        #seperate once to distinguish tag
        tag = line.split(' ', 1)

        if tag[0] == 'v':
            vertex = tag[1].split(' ', 3)
            v_arr.append([np.float32(vertex[0]), np.float32(vertex[1]), np.float32(vertex[2])])

        elif tag[0] == 'vn':
            normal = tag[1].split(' ', 3)
            n_arr.append([np.float32(normal[0]), np.float32(normal[1]), np.float32(normal[2])])
            vncount +=1

        elif tag[0] == 'f':
            face_arr = tag[1].split(' ')
            temp_index = []
            temp_normal = []
            for i in range(len(face_arr)):
                face = face_arr[i].split('/', 3)
                temp_index.append(int(face[0]) - 1)
                if vncount !=0:
                    temp_normal.append(int(face[2]) - 1)
            if len(face_arr)==3:
                face_i_arr.append(temp_index)
            elif len(face_arr) > 3:
                for k in range(len(face_arr)-2):
                    tmp =[]
                    tmp.append(int(temp_index[0]))
                    tmp.append(int(temp_index[k+1]))
                    tmp.append(int(temp_index[k+2]))
                    face_i_arr.append(tmp)
                
            if vncount !=0:
                if len(face_arr)==3:
                    face_normals.append(temp_normal)
                else:
                    for k in range(len(face_arr)-2):
                        tmp =[]
                        tmp.append(int(temp_normal[0]))
                        tmp.append(int(temp_normal[k+1]))
                        tmp.append(int(temp_normal[k+2]))
                        face_normals.append(tmp)
                
            total_triangle_num += (len(face_arr)-2)
            triangle_num += 1

            if len(face_arr) == 4:
                quad_num += 1
                triangle_num -= 1
            elif len(face_arr) > 4:
                face_over4v_num += 1
                triangle_num -=1
    f.close()
    total_face_num = triangle_num + quad_num + face_over4v_num
    if animation_mode==0:
        print("====================")
        print("File name:", f_name)
        print("Total number of faces:", total_face_num)
        print("Number of faces with 3 vertices:", triangle_num)
        print("Number of faces with 4 vertices:", quad_num)
        print("Number of faces with more than 4 vertices:", face_over4v_num)
        print("Number of triangle Mesh : " ,total_triangle_num)
    #save variable list-> array
    vertex_array = np.array(v_arr)
    index_array= np.array(face_i_arr)
    face_normal_array = np.array(face_normals)
    normal_array = np.array(n_arr)
    ssa=calculate_normal(total_triangle_num,vertex_array, index_array)
    bnva = None
    if vncount !=0:
        bnva=binding_normalvector_with_vertex(total_triangle_num,vertex_array, normal_array, face_normal_array, index_array)
    return ssa, bnva

def calculate_normal(total_triangle_num,vertex_array, face_index_array):
    if vertex_array is None:
        return
    narr = []
    normals = []
    #make normals have #ofvertex_array []
    for v in range(len(vertex_array)):
        normals.append([])

    for i in range(total_triangle_num):
        #p1, p2, p3 is vertex of triangle
        p1 = vertex_array[face_index_array[i][0]]
        p2 = vertex_array[face_index_array[i][1]]
        p3 = vertex_array[face_index_array[i][2]]
        #calculate normal vector by using p1, p2, p3
        temp_normal = np.cross(p1 - p2, p1 - p3)
        #calculate unit vector
        temp_normal = temp_normal / np.sqrt(np.dot(temp_normal, temp_normal))
        #add normal vectors to each of the three facing vertexs
        for j in range(3):
            normals[face_index_array[i][j]].append(temp_normal)
    #after this func. normals[i] have many temp_normal values
    #so we have to calculate average vector
    for i in range(len(normals)):
        temp_sum = [0., 0., 0.]
        for j in range(len(normals[i])):
            for k in range(3):
                temp_sum[k] += np.float32(normals[i][j][k])
        temp = np.array(temp_sum)
        temp = temp / (np.sqrt(np.dot(temp, temp)))
        narr.append(np.float32(temp))
    t_arr = []
    for i in range(total_triangle_num):
        for j in range(3):
            t_arr.append(narr[face_index_array[i][j]])
            t_arr.append(vertex_array[face_index_array[i][j]])
    return np.array(t_arr)

def binding_normalvector_with_vertex(total_triangle_num,vertex_array, normal_array, face_normal_array, face_index_array):
    varr = []
    for i in range(total_triangle_num):
        for j in range(3):
            varr.append(normal_array[face_normal_array[i][j]])
            varr.append(vertex_array[face_index_array[i][j]])
    return np.array(varr)

def draw_with_obj_shading(bind_normalV_vertex_array):

    if bind_normalV_vertex_array is None:
        return
    varr = bind_normalV_vertex_array

    glEnableClientState(GL_VERTEX_ARRAY)
    glEnableClientState(GL_NORMAL_ARRAY)
    glNormalPointer(GL_FLOAT, 6 * varr.itemsize, varr)
    glVertexPointer(3, GL_FLOAT, 6 * varr.itemsize,
                    ctypes.c_void_p(varr.ctypes.data + 3 * varr.itemsize))
    glDrawArrays(GL_TRIANGLES, 0, int(varr.size / 6))

def draw_with_smooth_shading(smooth_shading_array):
    if smooth_shading_array is None:
        return
    nvarr = smooth_shading_array

    glEnableClientState(GL_VERTEX_ARRAY)
    glEnableClientState(GL_NORMAL_ARRAY)
    glNormalPointer(GL_FLOAT, 6 * nvarr.itemsize, nvarr)
    glVertexPointer(3, GL_FLOAT, 6 * nvarr.itemsize,
                    ctypes.c_void_p(nvarr.ctypes.data + 3 * nvarr.itemsize))
    glDrawArrays(GL_TRIANGLES, 0, int(nvarr.size / 6))

def lighting(light, light_pos, light_color):
    glEnable(light)

    #set light position
    glPushMatrix()
    glLightfv(light, GL_POSITION,light_pos)
    glPopMatrix()
    #set light intensity
    ambient_light_color = (.1, .1, .1, 1.)
    glLightfv(light, GL_DIFFUSE,light_color)
    glLightfv(light, GL_SPECULAR,light_color)
    glLightfv(light, GL_AMBIENT,ambient_light_color)
    
def hierarchy_animate():
    global ssarray,bnvarray
    t=glfw.get_time()
    #soccer ball rotate
    glPushMatrix() #push1 for main frame
    glTranslatef(-7*np.sin(t*(0.5)),0,-7*np.cos(t*(0.5)))
    glRotatef(-28.84*t,0,1,0)

    glPushMatrix() #push2 for draw soccerball
    glTranslatef(0,0.65+np.abs(2.6*np.cos(2.2*t)),0)
    glScalef(0.01,0.01,0.01)
    glRotatef(200*t,1,0,0)
    if shading_mode==0:
        draw_with_obj_shading(bnvarray[0])
    else:
        draw_with_smooth_shading(ssarray[0])
    glPopMatrix() #pop2 soccerball

    glPushMatrix()
    glRotatef(57.6*t,0,1,0)
    glTranslatef(1+3*np.abs(np.sin(0.9*t)),(0.13+0.1*np.cos(t))*(np.abs(np.sin(7*t))),0)

    glPushMatrix()
    glScalef(0.3,0.3,0.3)
    if shading_mode==0:
        draw_with_obj_shading(bnvarray[1])
    else:
        draw_with_smooth_shading(ssarray[1])
    glPopMatrix()

    glPushMatrix()
    glRotate(270+30*np.sin(t),0,1,0)
    glTranslate(-1+2*np.sin(t),5+np.cos(7*t),-2+1.5*np.sin(t))
    glScalef(16,16,16)
    if shading_mode==0:
        draw_with_obj_shading(bnvarray[2])
    else:
        draw_with_smooth_shading(ssarray[2])
    glPopMatrix()
    glPopMatrix()
    glPopMatrix() #pop1

def render():
    global projection_mode,fov, polygon_fill_mode, shading_mode,animation_mode,smooth_shading_array,bind_normalV_vertex_array
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glEnable(GL_DEPTH_TEST)

    #select wire or solid
    if polygon_fill_mode==0:
        glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
    else :
        glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)

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
    
    t=glfw.get_time()
    #lighting ( Light number , light position,  light color)
    glEnable(GL_LIGHTING)
    glEnable(GL_RESCALE_NORMAL)
    lighting(GL_LIGHT0, (10., .0, .0, 0.), (1.0, .0, .0, 1.0))
    lighting(GL_LIGHT1, (0., 10.0, 0., 0.), (.0, 1.0, .0, 1.0))
    lighting(GL_LIGHT2, (0., 0., 10.0, 0.),(.0, .0, 1.0, 1.0))
    glPushMatrix()
    glTranslatef(2*np.sin(t),2.,2*np.cos(t))
    lighting(GL_LIGHT3, (0, 0, 0, 1.0), (0.4, 0.4, 0.4, 0.7))
    glPopMatrix()
    
    #object color
    object_color = (0.3, 0.3, 0.3, 1.)
    specular_object_color = (1., 1., 1., 1.)
    glMaterialfv(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, object_color)
    glMaterialfv(GL_FRONT, GL_SPECULAR, specular_object_color)
    glMaterialfv(GL_FRONT, GL_SHININESS, 10)
    
    if animation_mode ==0 or animation_mode==2:
        # shading mode : Using obj file or smooth shading
        if shading_mode==0:
            draw_with_obj_shading(bind_normalV_vertex_array)
        else:
            draw_with_smooth_shading(smooth_shading_array)
    elif animation_mode ==1:
        hierarchy_animate()
    glColor3ub(255, 255, 255)
    glDisable(GL_LIGHTING) 

def main():
    global ssarray, bnvarray
    path=[]
    path.append(os.path.abspath('./ball.obj'))
    path.append(os.path.abspath('./dog.obj'))
    path.append(os.path.abspath('./butterfly.obj'))
    #for hierarchical modeling
    for i in range(3):
        sarray,barray = define_arrays(path[i])
        ssarray.append(sarray)
        bnvarray.append(barray)  

    if not glfw.init():
        return
    window = glfw.create_window(800, 800, 'classassignment2', None, None)
    if not window:
        glfw.terminate()
        return

    glfw.set_key_callback(window, key_callback)
    glfw.set_mouse_button_callback(window, button_callback)
    glfw.make_context_current(window)
    glfw.set_scroll_callback(window, scroll_callback)
    glfw.set_drop_callback(window, drop_callback)

    while not glfw.window_should_close(window):
        glfw.poll_events()
        render()
        glfw.swap_buffers(window)

    glfw.terminate()

if __name__ == "__main__":
    main()