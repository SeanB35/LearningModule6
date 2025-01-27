import pygame
import math

# Screen and Simulation Settings
WIDTH = 1000
HEIGHT = 600
FPS = 60

# Colors
BG_COLOR = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
ARC_COLOR = (200, 200, 200)

# Ball Settings
RADIUS = 10
gravity = 0.04
REBOUND_COEFFICIENT = 0.7
MAX_BOUNCES = 3

# Initial Ball Position and State
BALL_X = RADIUS * 2
BALL_Y = HEIGHT - RADIUS
BALL_Y_CHANGE = -2
BALL_X_CHANGE = 2
ball_moving = False
num_bounces = 0

# Parabolic Arc Data
arc_points = []  # Stores points for the parabolic path

# Initialize Pygame
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Projectile Motion Simulator")
clock = pygame.time.Clock()

# Main Loop
running = True
while running:
    screen.fill(BG_COLOR)
    mouse_x, mouse_y = pygame.mouse.get_pos()

    # Clamp mouse position for velocity limits
    mouse_x = max(BALL_X - 30, min(BALL_X + 30, mouse_x))
    mouse_y = max(BALL_Y - 30, min(BALL_Y + 30, mouse_y))

    # Main Logic: Set up velocity if ball is not moving
    if not ball_moving:
        pygame.draw.line(screen, RED, [BALL_X, BALL_Y], [mouse_x, mouse_y], 4)
        vel_x = mouse_x - BALL_X  # Allow for left or right motion
        vel_y = mouse_y - BALL_Y
        vel = math.sqrt(vel_x**2 + vel_y**2)

        if vel > 0:
            theta = math.atan2(-vel_y, vel_x)  # Calculate angle
            max_dist_x = (2 * (vel / 10)**2 * math.cos(theta) * math.sin(theta)) / gravity
            max_height = ((vel / 10)**2 * math.sin(theta)**2) / (2 * gravity)
            BALL_X_CHANGE = vel_x / 10
            BALL_Y_CHANGE = vel_y / 10

    # Handle Events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                ball_moving = True
                arc_points = []  # Reset arc points on new motion

    # Draw Ball
    pygame.draw.circle(screen, BLACK, [int(BALL_X), int(BALL_Y)], RADIUS)

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

    # Apply Friction When on Ground
    if BALL_Y >= HEIGHT - RADIUS and not ball_moving:
        BALL_X_CHANGE *= 0.98  # Simulate friction
        if abs(BALL_X_CHANGE) < 0.1:
            BALL_X_CHANGE = 0

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
        pygame.draw.line(screen, RED, [BALL_X, BALL_Y], [BALL_X + BALL_X_CHANGE * 10, BALL_Y], 4)
        pygame.draw.line(screen, RED, [BALL_X, BALL_Y], [BALL_X, BALL_Y - BALL_Y_CHANGE * 10], 4)

    # Draw Parabolic Arc
    if len(arc_points) > 1:
        pygame.draw.lines(screen, ARC_COLOR, False, arc_points, 2)

    clock.tick(FPS)
    pygame.display.update()

pygame.quit()
