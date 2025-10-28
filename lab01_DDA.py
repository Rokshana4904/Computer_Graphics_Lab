from OpenGL.GL import * 
from OpenGL.GLU import * 
from OpenGL.GLUT import * 
import math

WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600

X0, Y0 = 100, 80
X1, Y1 = 200, 520
def dda_line(x1, y1, x2, y2):

    dx = x2 - x1
    dy = y2 - y1

    if abs(dx) > abs(dy):
        steps = abs(dx)
    else:
        steps = abs(dy)

    # Handle the case where both points are the same
    if steps == 0:
        glBegin(GL_POINTS)
        glVertex2f(x1, y1)
        glEnd()
        return

    # Step 3: Calculate the increment values for each step
    # x_increment = how much to add to x in each step
    # y_increment = how much to add to y in each step
    x_increment = dx / steps
    y_increment = dy / steps

    # Step 4: Initialize starting position
    # We use floating point arithmetic for accuracy
    x = x1
    y = y1

    # Step 5: Begin drawing points
    # GL_POINTS mode draws individual pixels
    glBegin(GL_POINTS)

    # Step 6: Plot the line by drawing intermediate points
    # We iterate from 0 to steps (inclusive) to draw steps+1 points
    for i in range(int(steps) + 1):
        # Round the floating point coordinates to nearest integer
        # This is necessary because screen coordinates are discrete pixels
        pixel_x = round(x)
        pixel_y = round(y)

        # Draw the current point
        glVertex2f(pixel_x, pixel_y)

        # Increment x and y by their respective increment values
        # This moves us closer to the end point
        x += x_increment
        y += y_increment

    # End the drawing operation
    glEnd()
def display():

    # Clear the screen (color buffer). GL_COLOR_BUFFER_BIT refers to the
    # color buffer of the window.
    glClear(GL_COLOR_BUFFER_BIT)
    # Set current drawing color (r, g, b). Values in [0,1].
    # glColor3f sets the current primitive color for subsequent geometry.
    glPointSize(4.0)
    glColor3f(1.0, 0.0, 0.0) # red color for line points

    # Compute points using the DDA algorithm
    dda_line(X0, Y0, X1, Y1)

    # Flush commands and swap buffers:
    # - glFlush() ensures all issued GL commands will be executed in
    #   finite time.
    # - glutSwapBuffers() swaps front and back buffers (if
    #   double-buffered).
    # We use glutSwapBuffers because display mode below requests
    # GLUT_DOUBLE.
    glutSwapBuffers()
def reshape(width, height):
    # Set viewport to cover the whole window (0,0) to (width,height)
    glViewport(0, 0, width, height)
    # Select projection matrix and reset it
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    # Create orthographic projection that matches window pixel
    # coordinates.
    # gluOrtho2D(left, right, bottom, top)
    # We set bottom=0 and top=WINDOW_HEIGHT so the origin (0,0) is at
    # lower-left.
    gluOrtho2D(0, width, 0, height)
    # Return to modelview matrix
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
def init_glut_window():
    # Initialize GLUT runtime; pass no arguments (empty list)
    glutInit()
    # Use double buffering and RGBA color mode
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGBA)
    # Initial window size
    glutInitWindowSize(WINDOW_WIDTH, WINDOW_HEIGHT)
    # Initial window position (x, y)
    glutInitWindowPosition(400, 100)
    # Create and show window with title (this call creates an OpenGL
    # context)
    glutCreateWindow(b"DDA Line Drawing Algorithm - PyOpenGL + GLUT")
    # Register GLUT callback functions
    glutDisplayFunc(display) # display callback: called when the window
    # must be redrawn
    glutReshapeFunc(reshape) # reshape callback: called when window is
    # resized

    # Some GLUT implementations require an initial call to reshape or set
    # up projection,
    # but our reshape will be called automatically on initial window
    # creation.
    # Set clear color: glClearColor(r,g,b,a) sets the background color for
    # glClear
    glClearColor(0.0, 0.0, 0.0, 1.0) # black background
def main():

    init_glut_window()
    # Enter GLUT's main loop. This hands control to GLUT which will call
    # the callbacks we registered.
    # GLUT's main loop handles events (keyboard, mouse, reshape) and
    # rendering.
    glutMainLoop()
if __name__ == "__main__":
    main()
