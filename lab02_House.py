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



def display():
    glClear(GL_COLOR_BUFFER_BIT)

    # Set color to Red and point size
    glColor3f(1.0, 0.0, 0.0)
    glPointSize(4.0)

    glBegin(GL_POINTS)

    points= mid_point_line(100,200,300,400)
    for x, y in points:
        glVertex2f(float(x), float(y)) 
        
    points= mid_point_line(400,200,600,400)
    for x, y in points:
        glVertex2f(float(x), float(y)) 
        
    points= mid_point_line(300,400,600,400)
    for x, y in points:
        glVertex2f(float(x), float(y)) 
        
    points= mid_point_line(100,200,400,200)
    for x, y in points:
        glVertex2f(float(x), float(y)) 
        
    points= mid_point_line(600,400,750,150)
    for x, y in points:
        glVertex2f(float(x), float(y)) 
        
    points= mid_point_line(670,170,570,370)
    for x, y in points:
        glVertex2f(float(x), float(y)) 
        
    points= mid_point_line(670,170,750,150)
    for x, y in points:
        glVertex2f(float(x), float(y)) 
        
    points= mid_point_line(150,200,150,30)
    for x, y in points:
        glVertex2f(float(x), float(y)) 
        
    points= mid_point_line(400,200,400,20)
    for x, y in points:
        glVertex2f(float(x), float(y)) 
        
    points= mid_point_line(150,30,400,20)
    for x, y in points:
        glVertex2f(float(x), float(y)) 
    
    points= mid_point_line(670,170,670,20)
    for x, y in points:
        glVertex2f(float(x), float(y)) 

    points= mid_point_line(400,20,670,20)
    for x, y in points:
        glVertex2f(float(x), float(y)) 
    
    points= mid_point_line(200,30,200,100)
    for x, y in points:
        glVertex2f(float(x), float(y)) 
    
    points= mid_point_line(200,100,300,100)
    for x, y in points:
        glVertex2f(float(x), float(y)) 
    points= mid_point_line(300,30,300,100)
    for x, y in points:
        glVertex2f(float(x), float(y)) 
    
    points= mid_point_line(500,20,500,100)
    for x, y in points:
        glVertex2f(float(x), float(y)) 
    points= mid_point_line(570,20,570,100)
    for x, y in points:
        glVertex2f(float(x), float(y)) 
    points= mid_point_line(500,100,570,100)
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
