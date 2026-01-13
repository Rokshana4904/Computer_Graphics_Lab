# pip3 install PyOpenGL PyOpenGL_accelerate playsound

from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import math
from datetime import datetime
import threading
import os
import platform
import subprocess
import time
import random

# ------------ WINDOW & CLOCK SETTINGS ------------

WINDOW_WIDTH = 900
WINDOW_HEIGHT = 900

CENTER_X = WINDOW_WIDTH // 2
CENTER_Y = WINDOW_HEIGHT // 2
CLOCK_RADIUS = 320

# ------------ ALARM SETTINGS ------------

ALARM_SOUND_FILE = "alarm.mp3"  # must be in the same folder
alarm_enabled = False
alarm_hour_input = 0
alarm_minute = 0
alarm_hour_12 = 0   # for 12-hour style comparison
alarm_triggered = False

# ------------ ANIMATION & DESIGN VARIABLES ------------

# Particle system for floating elements
particles = []
for _ in range(50):
    particles.append({
        'x': random.uniform(0, WINDOW_WIDTH),
        'y': random.uniform(0, WINDOW_HEIGHT),
        'size': random.uniform(1.0, 4.0),
        'speed': random.uniform(0.2, 1.0),
        'angle': random.uniform(0, 2 * math.pi),
        'color': (
            random.uniform(0.6, 0.8),
            random.uniform(0.6, 0.9),
            random.uniform(0.7, 1.0)
        )
    })

# Gradient colors for background
bg_colors = [(0.05, 0.05, 0.15), (0.02, 0.05, 0.1), (0.08, 0.03, 0.12)]
color_phase = 0

# Star particles
stars = []
for _ in range(100):
    stars.append({
        'x': random.uniform(0, WINDOW_WIDTH),
        'y': random.uniform(0, WINDOW_HEIGHT),
        'size': random.uniform(0.5, 2.0),
        'twinkle_speed': random.uniform(0.5, 2.0),
        'brightness': random.uniform(0.3, 1.0)
    })

# Hour marks animation
hour_mark_pulse = [0.0] * 12
hour_mark_colors = []

# Generate pastel colors for hour marks
for i in range(12):
    hue = i / 12.0
    hour_mark_colors.append((
        0.5 + 0.5 * math.sin(hue * 2 * math.pi) * 0.3,
        0.5 + 0.5 * math.sin(hue * 2 * math.pi + 2.09) * 0.3,
        0.5 + 0.5 * math.sin(hue * 2 * math.pi + 4.18) * 0.3
    ))

# ------------ ASTRONAUT & PLANETS ------------

# Astronaut properties
astronaut = {
    'x': WINDOW_WIDTH // 2,
    'y': WINDOW_HEIGHT // 2,
    'radius': 20,
    'speed_x': 0.5,
    'speed_y': 0.7,
    'bob_speed': 0.05,
    'bob_phase': random.uniform(0, 2 * math.pi),
    'rotation': 0,
    'rotation_speed': 0.5,
    'trail': [],
    'max_trail': 15,
    'color': (0.8, 0.9, 1.0)
}

# Planets orbiting the clock
planets = []
for i in range(3):
    planets.append({
        'radius': random.uniform(15, 30),
        'distance': random.uniform(CLOCK_RADIUS + 80, CLOCK_RADIUS + 150),
        'speed': random.uniform(0.002, 0.008),
        'angle': random.uniform(0, 2 * math.pi),
        'color': (
            random.uniform(0.5, 0.9),
            random.uniform(0.4, 0.8),
            random.uniform(0.6, 1.0)
        ),
        'name': ['Luna', 'Solara', 'Chronos'][i],
        'rings': i == 1,  # Second planet has rings
        'moons': i == 2   # Third planet has moons
    })

# Moons for the third planet
moons = []
for i in range(2):
    moons.append({
        'planet_idx': 2,
        'distance': random.uniform(30, 50),
        'speed': random.uniform(0.01, 0.02),
        'angle': random.uniform(0, 2 * math.pi),
        'radius': random.uniform(5, 8),
        'color': (0.7, 0.7, 0.7)
    })

# Comets for added effect
comets = []
for _ in range(2):
    comets.append({
        'x': random.uniform(-100, 100),
        'y': WINDOW_HEIGHT + 50,
        'speed_x': random.uniform(0.5, 1.5),
        'speed_y': random.uniform(-2.0, -1.0),
        'size': random.uniform(3, 6),
        'trail_length': 20,
        'trail': [],
        'color': (random.uniform(0.7, 1.0), random.uniform(0.8, 1.0), random.uniform(0.9, 1.0))
    })

# ------------ BASIC CIRCLE USING MIDPOINT ALGORITHM ------------

def mid_point_circle(cx, cy, r):
    """Midpoint circle algorithm (integer arithmetic, 8-way symmetry)."""
    pts = []
    x = 0
    y = r
    d = 1 - r

    def plot8(cx, cy, x, y):
        pts.extend([
            (cx + x, cy + y),
            (cx + y, cy + x),
            (cx + y, cy - x),
            (cx + x, cy - y),
            (cx - x, cy - y),
            (cx - y, cy - x),
            (cx - y, cy + x),
            (cx - x, cy + y),
        ])

    plot8(cx, cy, x, y)
    while x <= y:
        x += 1
        if d < 0:
            d += 2 * x + 1
        else:
            y -= 1
            d += 2 * (x - y) + 1
        plot8(cx, cy, x, y)

    return pts

# ------------ ANIMATION FUNCTIONS ------------

def update_animations():
    """Update all animation states"""
    global color_phase
    
    # Update color phase for gradient animation
    color_phase = (color_phase + 0.002) % (2 * math.pi)
    
    # Update particles
    for p in particles:
        p['x'] += math.cos(p['angle']) * p['speed']
        p['y'] += math.sin(p['angle']) * p['speed']
        
        # Wrap around screen edges
        if p['x'] < 0: p['x'] = WINDOW_WIDTH
        if p['x'] > WINDOW_WIDTH: p['x'] = 0
        if p['y'] < 0: p['y'] = WINDOW_HEIGHT
        if p['y'] > WINDOW_HEIGHT: p['y'] = 0
        
        # Slowly change angle
        p['angle'] += random.uniform(-0.05, 0.05)
    
    # Update stars twinkle
    for star in stars:
        star['brightness'] = 0.5 + 0.5 * math.sin(time.time() * star['twinkle_speed'])
    
    # Update hour mark pulses based on current time
    now = datetime.now()
    current_hour = now.hour % 12
    for i in range(12):
        if i == current_hour:
            hour_mark_pulse[i] = min(hour_mark_pulse[i] + 0.1, 1.0)
        else:
            hour_mark_pulse[i] = max(hour_mark_pulse[i] - 0.05, 0.0)
    
    # Update astronaut
    update_astronaut()
    
    # Update planets
    update_planets()
    
    # Update comets
    update_comets()

def update_astronaut():
    """Update astronaut position and animation"""
    # Bobbing motion
    astronaut['bob_phase'] += astronaut['bob_speed']
    bob_offset = math.sin(astronaut['bob_phase']) * 10
    
    # Move astronaut
    astronaut['x'] += astronaut['speed_x']
    astronaut['y'] += astronaut['speed_y'] + bob_offset * 0.1
    
    # Bounce off walls
    if astronaut['x'] < astronaut['radius']:
        astronaut['x'] = astronaut['radius']
        astronaut['speed_x'] *= -1
    elif astronaut['x'] > WINDOW_WIDTH - astronaut['radius']:
        astronaut['x'] = WINDOW_WIDTH - astronaut['radius']
        astronaut['speed_x'] *= -1
    
    if astronaut['y'] < astronaut['radius']:
        astronaut['y'] = astronaut['radius']
        astronaut['speed_y'] *= -1
    elif astronaut['y'] > WINDOW_HEIGHT - astronaut['radius']:
        astronaut['y'] = WINDOW_HEIGHT - astronaut['radius']
        astronaut['speed_y'] *= -1
    
    # Update rotation
    astronaut['rotation'] += astronaut['rotation_speed']
    if astronaut['rotation'] > 360:
        astronaut['rotation'] -= 360
    
    # Update trail
    astronaut['trail'].append((astronaut['x'], astronaut['y']))
    if len(astronaut['trail']) > astronaut['max_trail']:
        astronaut['trail'].pop(0)

def update_planets():
    """Update planet positions"""
    for planet in planets:
        planet['angle'] += planet['speed']
        if planet['angle'] > 2 * math.pi:
            planet['angle'] -= 2 * math.pi
    
    # Update moons
    for moon in moons:
        moon['angle'] += moon['speed']
        if moon['angle'] > 2 * math.pi:
            moon['angle'] -= 2 * math.pi

def update_comets():
    """Update comet positions"""
    for comet in comets:
        # Update position
        comet['x'] += comet['speed_x']
        comet['y'] += comet['speed_y']
        
        # Update trail
        comet['trail'].append((comet['x'], comet['y']))
        if len(comet['trail']) > comet['trail_length']:
            comet['trail'].pop(0)
        
        # Reset comet if it goes off screen
        if (comet['x'] < -100 or comet['x'] > WINDOW_WIDTH + 100 or 
            comet['y'] < -100 or comet['y'] > WINDOW_HEIGHT + 100):
            comet['x'] = random.uniform(-100, 100)
            comet['y'] = WINDOW_HEIGHT + 50
            comet['trail'] = []

# ------------ ENHANCED DRAWING FUNCTIONS ------------

def draw_gradient_background():
    """Draw animated gradient background"""
    glBegin(GL_QUADS)
    
    # Calculate animated colors
    r1 = bg_colors[0][0] + 0.03 * math.sin(color_phase)
    g1 = bg_colors[0][1] + 0.02 * math.sin(color_phase + 1)
    b1 = bg_colors[0][2] + 0.04 * math.sin(color_phase + 2)
    
    r2 = bg_colors[1][0] + 0.02 * math.sin(color_phase + 0.5)
    g2 = bg_colors[1][1] + 0.03 * math.sin(color_phase + 1.5)
    b2 = bg_colors[1][2] + 0.02 * math.sin(color_phase + 2.5)
    
    r3 = bg_colors[2][0] + 0.04 * math.sin(color_phase + 1)
    g3 = bg_colors[2][1] + 0.01 * math.sin(color_phase + 2)
    b3 = bg_colors[2][2] + 0.03 * math.sin(color_phase + 3)
    
    # Top left
    glColor3f(r1, g1, b1)
    glVertex2f(0, WINDOW_HEIGHT)
    
    # Top right
    glColor3f(r2, g2, b2)
    glVertex2f(WINDOW_WIDTH, WINDOW_HEIGHT)
    
    # Bottom right
    glColor3f(r3, g3, b3)
    glVertex2f(WINDOW_WIDTH, 0)
    
    # Bottom left
    glColor3f(r2, g2, b2)
    glVertex2f(0, 0)
    
    glEnd()

def draw_stars():
    """Draw twinkling stars in background"""
    glPointSize(1.5)
    glBegin(GL_POINTS)
    for star in stars:
        brightness = star['brightness']
        glColor3f(brightness, brightness, brightness)
        glVertex2f(star['x'], star['y'])
    glEnd()

def draw_particles():
    """Draw floating particles"""
    glPointSize(2.0)
    glBegin(GL_POINTS)
    for p in particles:
        glColor3f(p['color'][0], p['color'][1], p['color'][2])
        glVertex2f(p['x'], p['y'])
    glEnd()

def draw_astronaut():
    """Draw floating astronaut with space suit"""
    x, y = astronaut['x'], astronaut['y']
    radius = astronaut['radius']
    
    # Draw trail with fade effect
    if len(astronaut['trail']) > 1:
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glLineWidth(2.0)
        glBegin(GL_LINE_STRIP)
        for i, (trail_x, trail_y) in enumerate(astronaut['trail']):
            alpha = i / len(astronaut['trail'])
            glColor4f(0.8, 0.9, 1.0, alpha * 0.5)
            glVertex2f(trail_x, trail_y)
        glEnd()
        glDisable(GL_BLEND)
    
    # Save current matrix
    glPushMatrix()
    glTranslatef(x, y, 0)
    glRotatef(astronaut['rotation'], 0, 0, 1)
    
    # Space suit body (main circle)
    glColor3f(astronaut['color'][0], astronaut['color'][1], astronaut['color'][2])
    glBegin(GL_POLYGON)
    for i in range(32):
        angle = 2 * math.pi * i / 32
        glVertex2f(math.cos(angle) * radius, math.sin(angle) * radius)
    glEnd()
    
    # Helmet visor
    glColor3f(0.1, 0.2, 0.4)
    glBegin(GL_POLYGON)
    for i in range(16):
        angle = math.pi * 0.25 + math.pi * 0.5 * i / 15
        glVertex2f(math.cos(angle) * radius * 0.8, math.sin(angle) * radius * 0.8)
    glEnd()
    
    # Oxygen tank
    glColor3f(0.3, 0.3, 0.3)
    glBegin(GL_POLYGON)
    tank_points = [
        (-radius * 0.6, radius * 0.3),
        (-radius * 0.4, radius * 0.6),
        (-radius * 0.2, radius * 0.6),
        (-radius * 0.4, radius * 0.3)
    ]
    for point in tank_points:
        glVertex2f(point[0], point[1])
    glEnd()
    
    # Arms
    glLineWidth(3.0)
    glColor3f(0.9, 0.9, 0.9)
    glBegin(GL_LINES)
    # Right arm
    arm_angle = math.sin(time.time() * 2) * 0.5
    glVertex2f(radius * 0.7, 0)
    glVertex2f(radius * 1.5, math.cos(time.time()) * radius * 0.5)
    # Left arm
    glVertex2f(-radius * 0.7, 0)
    glVertex2f(-radius * 1.5, math.sin(time.time()) * radius * 0.5)
    glEnd()
    
    # Legs
    glBegin(GL_LINES)
    # Right leg
    leg_angle = math.cos(time.time() * 2) * 0.5
    glVertex2f(radius * 0.3, -radius * 0.7)
    glVertex2f(radius * 0.6, -radius * 1.5)
    # Left leg
    glVertex2f(-radius * 0.3, -radius * 0.7)
    glVertex2f(-radius * 0.6, -radius * 1.5)
    glEnd()
    
    # Restore matrix
    glPopMatrix()

def draw_planets():
    """Draw orbiting planets with rings and moons"""
    for i, planet in enumerate(planets):
        # Calculate planet position
        px = CENTER_X + math.cos(planet['angle']) * planet['distance']
        py = CENTER_Y + math.sin(planet['angle']) * planet['distance']
        
        # Draw planet
        glColor3f(planet['color'][0], planet['color'][1], planet['color'][2])
        glBegin(GL_POLYGON)
        for j in range(32):
            angle = 2 * math.pi * j / 32
            glVertex2f(px + math.cos(angle) * planet['radius'], 
                      py + math.sin(angle) * planet['radius'])
        glEnd()
        
        # Draw planet name
        glColor3f(1.0, 1.0, 1.0)
        draw_text(px - 20, py - planet['radius'] - 20, planet['name'], GLUT_BITMAP_HELVETICA_10)
        
        # Draw rings for specific planet
        if planet['rings']:
            glColor3f(0.8, 0.8, 0.5)
            glLineWidth(2.0)
            glBegin(GL_LINE_STRIP)
            for j in range(32):
                angle = 2 * math.pi * j / 31
                glVertex2f(px + math.cos(angle) * planet['radius'] * 1.5, 
                          py + math.sin(angle) * planet['radius'] * 0.6)
            glEnd()
        
        # Draw moons for this planet
        if planet['moons']:
            for moon in [m for m in moons if m['planet_idx'] == i]:
                moon_x = px + math.cos(moon['angle']) * moon['distance']
                moon_y = py + math.sin(moon['angle']) * moon['distance']
                
                glColor3f(moon['color'][0], moon['color'][1], moon['color'][2])
                glBegin(GL_POLYGON)
                for j in range(16):
                    angle = 2 * math.pi * j / 16
                    glVertex2f(moon_x + math.cos(angle) * moon['radius'], 
                              moon_y + math.sin(angle) * moon['radius'])
                glEnd()

def draw_comets():
    """Draw shooting comets"""
    for comet in comets:
        # Draw comet trail
        if len(comet['trail']) > 1:
            glEnable(GL_BLEND)
            glBlendFunc(GL_SRC_ALPHA, GL_ONE)
            glLineWidth(comet['size'] * 0.5)
            glBegin(GL_LINE_STRIP)
            for i, (trail_x, trail_y) in enumerate(comet['trail']):
                alpha = 1.0 - (i / len(comet['trail']))
                glColor4f(comet['color'][0], comet['color'][1], comet['color'][2], alpha)
                glVertex2f(trail_x, trail_y)
            glEnd()
            glDisable(GL_BLEND)
        
        # Draw comet head
        glColor3f(comet['color'][0], comet['color'][1], comet['color'][2])
        glPointSize(comet['size'] * 2)
        glBegin(GL_POINTS)
        glVertex2f(comet['x'], comet['y'])
        glEnd()

def draw_decorative_rings():
    """Draw decorative concentric rings around clock"""
    glPointSize(1.0)
    
    # Multiple rings with different colors
    rings = [
        (CLOCK_RADIUS + 60, 0.3, 0.3, 0.5, 100),
        (CLOCK_RADIUS + 45, 0.4, 0.4, 0.6, 80),
        (CLOCK_RADIUS + 30, 0.5, 0.5, 0.7, 60),
        (CLOCK_RADIUS + 15, 0.6, 0.6, 0.8, 40),
    ]
    
    for radius, r, g, b, num_points in rings:
        glColor3f(r, g, b)
        glBegin(GL_POINTS)
        for i in range(num_points):
            angle = 2 * math.pi * i / num_points
            x = CENTER_X + math.cos(angle) * radius
            y = CENTER_Y + math.sin(angle) * radius
            glVertex2f(x, y)
        glEnd()

def draw_glowing_circle(cx, cy, radius, glow_intensity):
    """Draw a circle with glow effect"""
    glPointSize(2.0 + glow_intensity * 3)
    glBegin(GL_POINTS)
    points = mid_point_circle(int(cx), int(cy), int(radius))
    for x, y in points:
        # Fade glow towards edges
        dist_from_center = math.sqrt((x - cx)**2 + (y - cy)**2)
        fade = 1.0 - (dist_from_center / radius)
        intensity = glow_intensity * fade
        glColor3f(0.7 + intensity, 0.7 + intensity, 0.3 + intensity)
        glVertex2f(float(x), float(y))
    glEnd()

def draw_clock_face():
    # Draw decorative background rings
    draw_decorative_rings()
    
    # Outer glowing ring
    pulse = 0.3 + 0.2 * math.sin(time.time() * 2)
    draw_glowing_circle(CENTER_X, CENTER_Y, CLOCK_RADIUS + 10, pulse)
    
    # Main clock circle with gradient
    glPointSize(2.5)
    glBegin(GL_POINTS)
    outer_pts = mid_point_circle(CENTER_X, CENTER_Y, CLOCK_RADIUS)
    for x, y in outer_pts:
        # Create gradient based on position
        dist_from_center = math.sqrt((x - CENTER_X)**2 + (y - CENTER_Y)**2)
        gradient = dist_from_center / CLOCK_RADIUS
        
        # Color from light blue in center to white at edges
        r = 0.8 + 0.2 * gradient
        g = 0.9 + 0.1 * gradient
        b = 1.0
        glColor3f(r, g, b)
        glVertex2f(float(x), float(y))
    glEnd()

    # Inner center with animated glow
    center_pulse = 0.5 + 0.5 * math.sin(time.time() * 3)
    glPointSize(3.0 + center_pulse * 2)
    glColor3f(0.9, 0.9, 0.3)
    glBegin(GL_POINTS)
    center_pts = mid_point_circle(CENTER_X, CENTER_Y, 10)
    for x, y in center_pts:
        glVertex2f(float(x), float(y))
    glEnd()

    # Hour marks with animation
    glLineWidth(6.0)
    for i in range(12):
        angle_deg = i * 30.0
        angle_rad = math.radians(90.0 - angle_deg)
        
        # Animated length based on pulse
        pulse_factor = 1.0 + hour_mark_pulse[i] * 0.3
        r_outer = CLOCK_RADIUS * pulse_factor
        r_inner = (CLOCK_RADIUS - 25) * pulse_factor
        
        # Color with pulse effect
        color_intensity = 0.7 + hour_mark_pulse[i] * 0.3
        r, g, b = hour_mark_colors[i]
        glColor3f(r * color_intensity, g * color_intensity, b * color_intensity)
        
        glBegin(GL_LINES)
        x_outer = CENTER_X + math.cos(angle_rad) * r_outer
        y_outer = CENTER_Y + math.sin(angle_rad) * r_outer
        x_inner = CENTER_X + math.cos(angle_rad) * r_inner
        y_inner = CENTER_Y + math.sin(angle_rad) * r_inner
        glVertex2f(x_inner, y_inner)
        glVertex2f(x_outer, y_outer)
        glEnd()

    # Numbers with glow effect
    number_radius = CLOCK_RADIUS - 65
    glColor3f(1.0, 1.0, 1.0)
    for i in range(1, 13):
        if i == 12:
            angle_deg = 0.0
        else:
            angle_deg = i * 30.0
        angle_rad = math.radians(90.0 - angle_deg)

        x = CENTER_X + math.cos(angle_rad) * number_radius
        y = CENTER_Y + math.sin(angle_rad) * number_radius

        text = str(i)
        
        # Add subtle pulse to current hour number
        current_hour = datetime.now().hour % 12
        if i == 12: current_hour = 0
        pulse_scale = 1.0 + (0.2 if (i % 12) == current_hour else 0.0)
        
        glPushMatrix()
        glTranslatef(x, y, 0)
        glScalef(pulse_scale, pulse_scale, 1.0)
        draw_text(-10, -5, text, GLUT_BITMAP_HELVETICA_18)
        glPopMatrix()

    # Decorative corner elements with animation
    corner_r = 15
    corner_positions = [
        (100, 100),
        (WINDOW_WIDTH - 100, 100),
        (100, WINDOW_HEIGHT - 100),
        (WINDOW_WIDTH - 100, WINDOW_HEIGHT - 100),
    ]
    
    rotation = time.time() * 0.5  # Slow rotation
    
    for (cx, cy) in corner_positions:
        # Draw rotating decorative element
        glPushMatrix()
        glTranslatef(cx, cy, 0)
        glRotatef(rotation * 30, 0, 0, 1)
        
        glColor3f(0.6, 0.7, 0.9)
        glPointSize(2.0)
        glBegin(GL_POINTS)
        for i in range(8):
            angle = 2 * math.pi * i / 8
            px = math.cos(angle) * corner_r
            py = math.sin(angle) * corner_r
            glVertex2f(px, py)
        glEnd()
        
        glPopMatrix()
    
    # Digital time display at bottom with glow
    now = datetime.now()
    time_str = now.strftime("%I:%M:%S %p")
    date_str = now.strftime("%A, %B %d")
    
    glColor3f(0.9, 0.9, 1.0)
    draw_text(CENTER_X - 70, 50, time_str, GLUT_BITMAP_HELVETICA_18)
    glColor3f(0.7, 0.8, 1.0)
    draw_text(CENTER_X - 100, 30, date_str, GLUT_BITMAP_TIMES_ROMAN_10)

# ------------ TEXT DRAWING ------------

def draw_text(x, y, text, font=GLUT_BITMAP_HELVETICA_18):
    glRasterPos2f(x, y)
    for ch in text:
        glutBitmapCharacter(font, ord(ch))

# ------------ ENHANCED HAND DRAWING ------------

def draw_hand(clock_angle_deg, length, width, r, g, b, is_seconds=False):
    angle_rad = math.radians(90.0 - clock_angle_deg)
    
    # For seconds hand, add slight wiggle animation
    if is_seconds:
        wiggle = math.sin(time.time() * 10) * 0.5
        angle_rad += math.radians(wiggle)
    
    x_end = CENTER_X + math.cos(angle_rad) * length
    y_end = CENTER_Y + math.sin(angle_rad) * length
    
    # Draw shadow first (slightly offset and darker)
    glLineWidth(width + 2)
    glColor3f(r * 0.3, g * 0.3, b * 0.3)
    glBegin(GL_LINES)
    glVertex2f(float(CENTER_X) + 2, float(CENTER_Y) + 2)
    glVertex2f(float(x_end) + 2, float(y_end) + 2)
    glEnd()
    
    # Draw main hand with gradient
    glLineWidth(width)
    glBegin(GL_LINES)
    
    # Gradient from center to tip
    glColor3f(r, g, b)
    glVertex2f(float(CENTER_X), float(CENTER_Y))
    
    # Tip is brighter
    glColor3f(min(1.0, r * 1.3), min(1.0, g * 1.3), min(1.0, b * 1.3))
    glVertex2f(float(x_end), float(y_end))
    
    glEnd()
    
    # Draw hand tip decoration
    if is_seconds:
        # Red circle at tip of seconds hand
        glPointSize(8.0)
        glColor3f(1.0, 0.2, 0.2)
        glBegin(GL_POINTS)
        glVertex2f(float(x_end), float(y_end))
        glEnd()

# ------------ ALARM HAND & SOUND ------------

def play_alarm_sound():
    print(">>> Alarm time reached! Trying to play audio...")
    
    if not ALARM_SOUND_FILE or not os.path.exists(ALARM_SOUND_FILE):
        print("Alarm audio file not found:", ALARM_SOUND_FILE)
        return
    
    system = platform.system()
    try:
        if system == "Darwin":  # macOS
            subprocess.Popen(["afplay", ALARM_SOUND_FILE])
        elif system == "Windows":
            import winsound
            winsound.PlaySound(
                ALARM_SOUND_FILE,
                winsound.SND_FILENAME | winsound.SND_ASYNC
            )
        else:  # Linux / others
            try:
                subprocess.Popen(["aplay", ALARM_SOUND_FILE])
            except Exception:
                subprocess.Popen(["xdg-open", ALARM_SOUND_FILE])
    except Exception as e:
        print("Could not play alarm sound:", e)

def check_and_trigger_alarm(now):
    global alarm_triggered
    if not alarm_enabled:
        return
    if alarm_triggered:
        return
    
    current_hour_12 = now.hour % 12
    if current_hour_12 == alarm_hour_12 and now.minute == alarm_minute:
        alarm_triggered = True
        t = threading.Thread(target=play_alarm_sound, daemon=True)
        t.start()

# ------------ OPENGL CALLBACKS ------------

def display():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    
    # Update animations
    update_animations()
    
    # Draw background elements
    draw_gradient_background()
    draw_stars()
    draw_particles()
    draw_comets()
    draw_planets()
    
    # Draw clock face and outside design
    draw_clock_face()
    
    # Draw astronaut (in front of clock)
    draw_astronaut()
    
    # Current time
    now = datetime.now()
    check_and_trigger_alarm(now)
    
    seconds = now.second + now.microsecond / 1_000_000.0
    minutes = now.minute + seconds / 60.0
    hours = (now.hour % 12) + minutes / 60.0
    
    # Convert time to angles
    second_angle = seconds * 6.0
    minute_angle = minutes * 6.0
    hour_angle = hours * 30.0
    
    # Hand lengths
    hour_len = CLOCK_RADIUS * 0.45
    minute_len = CLOCK_RADIUS * 0.65
    second_len = CLOCK_RADIUS * 0.75
    
    # Draw hands with enhanced effects
    draw_hand(hour_angle, hour_len, 8.0, 0.2, 0.6, 1.0)      # Hour: Blue
    draw_hand(minute_angle, minute_len, 5.0, 0.2, 1.0, 0.4)  # Minute: Green
    draw_hand(second_angle, second_len, 2.5, 1.0, 0.3, 0.3, is_seconds=True)  # Second: Red with animation
    
    # Digital alarm indicator with blink effect
    if alarm_enabled:
        blink = 0.5 + 0.5 * math.sin(time.time() * 3)  # Blink at 3Hz
        glColor3f(1.0, 0.8 * blink, 0.2 * blink)
        text = f"ALARM: {alarm_hour_input:02d}:{alarm_minute:02d}"
        draw_text(CENTER_X - 70, CENTER_Y - CLOCK_RADIUS + 120, text)
        
        # Draw alarm hand (ghost hand showing alarm time)
        if not alarm_triggered:
            alarm_angle = alarm_hour_12 * 30.0  # Convert hour to angle
            glEnable(GL_BLEND)
            glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
            glLineWidth(3.0)
            glColor4f(1.0, 0.8, 0.2, 0.3)  # Semi-transparent yellow
            glBegin(GL_LINES)
            glVertex2f(float(CENTER_X), float(CENTER_Y))
            x_alarm = CENTER_X + math.cos(math.radians(90 - alarm_angle)) * hour_len
            y_alarm = CENTER_Y + math.sin(math.radians(90 - alarm_angle)) * hour_len
            glVertex2f(float(x_alarm), float(y_alarm))
            glEnd()
            glDisable(GL_BLEND)
    
    glutSwapBuffers()

def reshape(width, height):
    glViewport(0, 0, width, height)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluOrtho2D(0, width, 0, height)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

def update(value):
    glutPostRedisplay()
    glutTimerFunc(16, update, 0)  # ~60 FPS

# ------------ GLUT / OPENGL INIT ------------

def init_glut_window():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGBA | GLUT_DEPTH)
    glutInitWindowSize(WINDOW_WIDTH, WINDOW_HEIGHT)
    glutInitWindowPosition(200, 50)
    glutCreateWindow(b"Cosmic Clock with Astronaut & Planets")
    
    glutDisplayFunc(display)
    glutReshapeFunc(reshape)
    glutTimerFunc(0, update, 0)
    
    # Enable blending for transparency effects
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

def main():
    global alarm_enabled, alarm_hour_input, alarm_minute, alarm_hour_12
    
    print("=" * 50)
    print("COSMIC CLOCK WITH ASTRONAUT & PLANETS")
    print("=" * 50)
    print("\nFeatures:")
    print("* Animated gradient background")
    print("* Floating astronaut with bobbing motion")
    print("* 3 Orbiting planets with names (Luna, Solara, Chronos)")
    print("* Shooting comets with glowing trails")
    print("* Twinkling star particles")
    print("* Pulse animations for hour marks")
    print("* Smooth hand movements with shadows")
    print("* Rotating decorative elements")
    print("* Real-time digital display")
    print("=" * 50)
    
    choice = input("\nDo you want to set an alarm? (y/n): ").strip().lower()
    
    if choice.startswith("y"):
        alarm_enabled = True
        print("\n" + "=" * 50)
        print("ALARM SETUP")
        print("=" * 50)
        
        while True:
            try:
                alarm_hour_input = int(input("Alarm hour (1-12): "))
                if 1 <= alarm_hour_input <= 12:
                    break
                else:
                    print("Please enter hour between 1 and 12.")
            except ValueError:
                print("Invalid input. Please enter an integer.")
        
        while True:
            try:
                alarm_minute = int(input("Alarm minute (0-59): "))
                if 0 <= alarm_minute <= 59:
                    break
                else:
                    print("Please enter minute between 0 and 59.")
            except ValueError:
                print("Invalid input. Please enter an integer.")
        
        alarm_hour_12 = alarm_hour_input % 12
        print(f"\n[OK] Alarm set for {alarm_hour_input:02d}:{alarm_minute:02d}")
        print(f"[INFO] Make sure '{ALARM_SOUND_FILE}' is in the same folder for sound.\n")
    else:
        alarm_enabled = False
        print("\n[INFO] No alarm set. Enjoy the space animation!\n")
    
    init_glut_window()
    glutMainLoop()

if __name__ == "__main__":
    main()