import pygame
import math
import sys

# Screen and Simulation Settings
WIDTH = 1000
HEIGHT = 600
FPS = 60

# Colors
BG_COLOR = (30, 30, 45)  # Dark background
BALL_COLOR = (0, 200, 255)  # Bright cyan for the ball
TRAIL_COLOR = (0, 100, 150, 100)  # Semi-transparent trail
ARC_COLOR = (200, 200, 200)  # Parabolic arc color
TEXT_COLOR = (255, 255, 255)  # White text

# Ball Settings
RADIUS = 10
gravity = 0.04
REBOUND_COEFFICIENT = 0.7
AIR_RESISTANCE = 0.01  # Air resistance coefficient
MAX_BOUNCES = 3

# Initial Ball Position and State
BALL_X = RADIUS * 2
BALL_Y = HEIGHT - RADIUS
BALL_Y_CHANGE = 0
BALL_X_CHANGE = 0
ball_moving = False
num_bounces = 0

# Parabolic Arc Data
arc_points = []  # Stores points for the parabolic path

# Initialize Pygame
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Projectile Motion Simulator")
clock = pygame.time.Clock()
font = pygame.font.SysFont("Arial", 18)

# Function to draw gradient background
def draw_gradient_background():
    for y in range(HEIGHT):
        color = (30 + y // 4, 30 + y // 4, 45 + y // 4)
        pygame.draw.line(screen, color, (0, y), (WIDTH, y))

# Function to reset the simulation
def reset_simulation():
    global BALL_X, BALL_Y, BALL_X_CHANGE, BALL_Y_CHANGE, ball_moving, num_bounces, arc_points
    BALL_X = RADIUS * 2
    BALL_Y = HEIGHT - RADIUS
    BALL_X_CHANGE = 0
    BALL_Y_CHANGE = 0
    ball_moving = False
    num_bounces = 0
    arc_points = []

# Main Loop
running = True
dragging = False
while running:
    screen.fill(BG_COLOR)
    draw_gradient_background()
    mouse_x, mouse_y = pygame.mouse.get_pos()

    # Handle Events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN and not ball_moving:
            dragging = True
        if event.type == pygame.MOUSEBUTTONUP and dragging:
            dragging = False
            ball_moving = True
            arc_points = []  # Reset arc points on new motion
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:  # Reset simulation
                reset_simulation()

    # Set initial velocity if dragging
    if dragging and not ball_moving:
        vel_x = mouse_x - BALL_X
        vel_y = mouse_y - BALL_Y
        vel = math.sqrt(vel_x**2 + vel_y**2)
        if vel > 0:
            theta = math.atan2(-vel_y, vel_x)  # Calculate angle
            BALL_X_CHANGE = vel_x / 10
            BALL_Y_CHANGE = vel_y / 10
        pygame.draw.line(screen, (255, 0, 0), [BALL_X, BALL_Y], [mouse_x, mouse_y], 4)

    # Draw Ball
    pygame.draw.circle(screen, BALL_COLOR, [int(BALL_X), int(BALL_Y)], RADIUS)

    # Boundary Check and Bounce Logic
    if BALL_Y > HEIGHT - RADIUS and ball_moving:
        if num_bounces < MAX_BOUNCES:
            BALL_Y_CHANGE *= -REBOUND_COEFFICIENT
            BALL_X_CHANGE *= REBOUND_COEFFICIENT
        else:
            BALL_Y_CHANGE = 0
            BALL_X_CHANGE = 0
            BALL_Y = HEIGHT - RADIUS
            ball_moving = False
            num_bounces = 0
        num_bounces += 1

    # Left and Right Wall Bounce Logic
    if BALL_X <= RADIUS or BALL_X >= WIDTH - RADIUS:
        BALL_X_CHANGE *= -REBOUND_COEFFICIENT  # Reverse horizontal direction
        if BALL_X <= RADIUS:
            BALL_X = RADIUS  # Prevent getting stuck
        if BALL_X >= WIDTH - RADIUS:
            BALL_X = WIDTH - RADIUS

    # Apply Friction and Air Resistance
    if BALL_Y >= HEIGHT - RADIUS and not ball_moving:
        BALL_X_CHANGE *= 0.98  # Simulate friction
        if abs(BALL_X_CHANGE) < 0.1:
            BALL_X_CHANGE = 0
    if ball_moving:
        BALL_X_CHANGE *= (1 - AIR_RESISTANCE)  # Air resistance

    # Update Ball Position if Moving
    if ball_moving:
        BALL_Y += BALL_Y_CHANGE
        BALL_Y_CHANGE += gravity
        BALL_X += BALL_X_CHANGE

        # Add current position to arc points
        arc_points.append((int(BALL_X), int(BALL_Y)))

        # Limit arc points to last 2 seconds of motion
        if len(arc_points) > FPS * 2:
            arc_points.pop(0)

        # Draw Velocity Vectors
        pygame.draw.line(screen, (255, 0, 0), [BALL_X, BALL_Y], [BALL_X + BALL_X_CHANGE * 10, BALL_Y], 4)
        pygame.draw.line(screen, (255, 0, 0), [BALL_X, BALL_Y], [BALL_X, BALL_Y - BALL_Y_CHANGE * 10], 4)

    # Draw Parabolic Arc
    if len(arc_points) > 1:
        pygame.draw.lines(screen, ARC_COLOR, False, arc_points, 2)

    # Draw Trail
    if len(arc_points) > 1:
        for i in range(len(arc_points) - 1):
            alpha = int(255 * (i / len(arc_points)))
            trail_color = (*TRAIL_COLOR[:3], alpha)
            pygame.draw.line(screen, trail_color, arc_points[i], arc_points[i + 1], 2)

    # Display Stats
    stats = [
        f"Velocity: {math.hypot(BALL_X_CHANGE, BALL_Y_CHANGE):.2f}",
        f"Angle: {math.degrees(math.atan2(-BALL_Y_CHANGE, BALL_X_CHANGE)):.2f}°",
        f"Bounces: {num_bounces}",
        f"Press R to Reset"
    ]
    for i, stat in enumerate(stats):
        text = font.render(stat, True, TEXT_COLOR)
        screen.blit(text, (10, 10 + i * 20))

    clock.tick(FPS)
    pygame.display.update()

pygame.quit()