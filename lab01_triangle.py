from OpenGL.GL import *          
from OpenGL.GLU import *          
from OpenGL.GLUT import *        
import math


WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600



X0, Y0 = 100, 80
X1, Y1 = 200, 520

points = []

def mid_point_line(X1, Y1, X2, Y2):

    global points
    points = []  

    dx = X2 - X1
    dy = Y2 - Y1

    x_step = 1 if dx >= 0 else -1
    y_step = 1 if dy >= 0 else -1

    dx = abs(dx)
    dy = abs(dy)

    x = X1
    y = Y1
    points.append((x, y))

    if dx >= dy:
        d = 2*dy - dx
        for _ in range(dx):
            x += x_step
            if d <= 0:
                d += 2*dy
            else:
                y += y_step
                d += 2*(dy - dx)
            points.append((x, y))
    else:
        d = 2*dx - dy
        for _ in range(dy):
            y += y_step
            if d <= 0:
                d += 2*dx
            else:
                x += x_step
                d += 2*(dx - dy)
            points.append((x, y))

    return points
    



def display():
    glClear(GL_COLOR_BUFFER_BIT)

    glColor3f(1.0, 0.0, 0.0) 
    glPointSize(4.0)

    glBegin(GL_POINTS)


    mid_point_line(150, 100, 450, 100)
    for x, y in points:
        glVertex2f(float(x), float(y)) 

    mid_point_line(450, 100, 400, 500)
    for x, y in points:
        glVertex2f(float(x), float(y)) 

    mid_point_line(400, 500, 150, 100)
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
