from OpenGL.GL import *          
from OpenGL.GLU import *          
from OpenGL.GLUT import *        
import math


WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600


X0, Y0 = 100, 80
X1, Y1 = 200, 520

def get_zone(dx,dy):

    adx, ady = abs(dx), abs(dy)

    if adx >= ady:
        if dx >= 0 and dy >= 0:
            return 0
        if dx < 0 and dy >= 0:
            return 3
        if dx < 0 and dy < 0:
            return 4
        return 7
    else:         
        if dx >= 0 and dy >= 0:
            return 1
        if dx < 0 and dy >= 0:
            return 2
        if dx < 0 and dy < 0:
            return 5
        return 6


def convert_to_zone_0(x,y,zone):
    if zone == 0:   
        return x, y
    if zone == 1:   
        return y, x
    if zone == 2:   
        return y, -x
    if zone == 3:   
        return -x, y
    if zone == 4:   
        return -x, -y
    if zone == 5:   
        return -y, -x
    if zone == 6:   
        return -y, x
    if zone == 7:   
        return x, -y
    return x, y


def convert_back_from_zone_0(x,y,zone):
    if zone == 0:   
        return x, y
    if zone == 1:   
        return y, x
    if zone == 2:   
        return -y, x
    if zone == 3:   
        return -x, y
    if zone == 4:   
        return -x, -y
    if zone == 5:   
        return -y, -x
    if zone == 6:   
        return y, -x
    if zone == 7:   
        return x, -y
    return x, y

def mid_point_line(X1, Y1, X2, Y2):
    points = []  

    dx = X2 - X1
    dy = Y2 - Y1

    zone = get_zone(dx, dy)

    x0_z0, y0_z0 = convert_to_zone_0(X1, Y1, zone)
    x1_z0, y1_z0 = convert_to_zone_0(X2, Y2, zone)

    dx = x1_z0 - x0_z0
    dy = y1_z0 - y0_z0

    dx = abs(dx)
    dy = abs(dy)

    x = x0_z0
    y = y0_z0
    xr,yr= convert_back_from_zone_0(x,y,zone)
    points.append((xr,yr))

    if dx >= dy:
        d = 2 * dy - dx
        for _ in range(dx):
            x += 1
            if d <= 0:
                d += 2 * dy
            else:
                y += 1
                d += 2 * (dy - dx)
            xr,yr= convert_back_from_zone_0(x,y,zone)
            points.append((xr,yr))
    else:
        d = 2 * dx - dy
        for _ in range(dy):
            y += 1
            if d <= 0:
                d += 2 * dx
            else:
                x += 1
                d += 2 * (dx - dy)
                xr,yr= convert_back_from_zone_0(x,y,zone)
                points.append((xr,yr))

    return points

def line_from(p, q):
    return mid_point_line(p[0], p[1], q[0], q[1])

def display():
    glClear(GL_COLOR_BUFFER_BIT)

    glColor3f(1.0, 0.0, 0.0) 
    glPointSize(4.0)

    

    glBegin(GL_POINTS)
    
    arr = [
    (100, 200),
    (400, 200),
    (100, 400),
    (400, 400),
    (250, 100),
    (250, 300),
    (500, 100),
    (500, 300)
    ]

    points= line_from(arr[0], arr[1])
    for x, y in points:
        glVertex2f(float(x), float(y)) 

    points= line_from(arr[0],arr[2])
    for x, y in points:
        glVertex2f(float(x), float(y)) 

    points= line_from(arr[2],arr[3])
    for x, y in points:
        glVertex2f(float(x), float(y)) 

    points= line_from(arr[1],arr[3])
    for x, y in points:
        glVertex2f(float(x), float(y)) 

    points= line_from(arr[4],arr[6])
    for x, y in points:
        glVertex2f(float(x), float(y)) 

    points= line_from(arr[4],arr[5])
    for x, y in points:
        glVertex2f(float(x), float(y)) 

    points= line_from(arr[5],arr[7])
    for x, y in points:
        glVertex2f(float(x), float(y)) 

    points= line_from(arr[6],arr[7])
    for x, y in points:
        glVertex2f(float(x), float(y)) 

    points= line_from(arr[2],arr[5])
    for x, y in points:
        glVertex2f(float(x), float(y)) 

    points= line_from(arr[0],arr[4])
    for x, y in points:
        glVertex2f(float(x), float(y)) 
    points= line_from(arr[3],arr[7])
    for x, y in points:
        glVertex2f(float(x), float(y)) 
    points= line_from(arr[1],arr[6])
    for x, y in points:
        glVertex2f(float(x), float(y)) 

    

    glEnd()

    glutSwapBuffers()


def reshape(width, height):

    glViewport(0, 0, width, height)

    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()

    gluOrtho2D(0, width, 0, height)

    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()


def init_glut_window():

    glutInit()

    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGBA)

    glutInitWindowSize(WINDOW_WIDTH, WINDOW_HEIGHT)

    glutInitWindowPosition(400, 100)

    glutCreateWindow(b"DDA Line Drawing Algorithm - PyOpenGL + GLUT")

    glutDisplayFunc(display)  
    glutReshapeFunc(reshape)  
    glClearColor(0.0, 0.0, 0.0, 1.0) 


def main():

    init_glut_window()

    glutMainLoop()


if __name__ == "__main__":
    main()
