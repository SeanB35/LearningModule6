import pygame
import numpy as np
import pygame_gui
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas

# Initialize simulation variables
width, height = 800, 600  # Simulation area dimensions
num_particles = 100  # Initial number of particles
temperature = 300  # Kelvin (controls particle speed)
particle_radius = 5
particle_mass = 1e-26  # Approximate mass of a gas particle (kg)
k_B = 1.38e-23  # Boltzmann constant

# Calculate initial particle speed based on temperature
particle_speed = np.sqrt(3 * k_B * temperature / particle_mass)

# Initialize pygame
pygame.init()
screen = pygame.display.set_mode((width + 300, height))  # Extra space for side panel
pygame.display.set_caption("Gas Lab Simulator")
font = pygame.font.SysFont(None, 24)
clock = pygame.time.Clock()

# Initialize pygame_gui
manager = pygame_gui.UIManager((width + 300, height))

# Sliders for controlling particles, temperature, and container size
particle_slider = pygame_gui.elements.UIHorizontalSlider(
    relative_rect=pygame.Rect((width + 10, 40), (280, 20)),
    start_value=num_particles,
    value_range=(10, 500),  # min_value and max_value are passed as a tuple
    manager=manager
)

temperature_slider = pygame_gui.elements.UIHorizontalSlider(
    relative_rect=pygame.Rect((width + 10, 100), (280, 20)),
    start_value=temperature,
    value_range=(100, 500),  # min_value and max_value are passed as a tuple
    manager=manager
)

width_slider = pygame_gui.elements.UIHorizontalSlider(
    relative_rect=pygame.Rect((width + 10, 160), (280, 20)),
    start_value=width,
    value_range=(400, 1000),  # min_value and max_value are passed as a tuple
    manager=manager
)

height_slider = pygame_gui.elements.UIHorizontalSlider(
    relative_rect=pygame.Rect((width + 10, 220), (280, 20)),
    start_value=height,
    value_range=(300, 800),  # min_value and max_value are passed as a tuple
    manager=manager
)

# Function to calculate speed of a particle
def calculate_speed(velocity):
    return np.linalg.norm(velocity)

# Function to draw real-time histogram for speed distribution
def draw_speed_distribution(particles):
    speeds = [calculate_speed(p["vel"]) for p in particles]
    fig, ax = plt.subplots(figsize=(4, 4), dpi=100)
    ax.hist(speeds, bins=10, color='blue', edgecolor='black')
    ax.set_title("Speed Distribution")
    ax.set_xlabel("Speed")
    ax.set_ylabel("Frequency")
    canvas = FigureCanvas(fig)
    canvas.draw()
    buf = canvas.buffer_rgba()
    raw_data = np.asarray(buf)
    plt.close(fig)
    surface = pygame.image.frombuffer(raw_data, canvas.get_width_height(), 'RGBA')
    return pygame.transform.scale(surface, (300, 300))

# Function to handle particle-wall collisions
def handle_wall_collisions(particle, width, height):
    if particle["pos"][0] <= 0 or particle["pos"][0] >= width:
        particle["vel"][0] *= -1
    if particle["pos"][1] <= 0 or particle["pos"][1] >= height:
        particle["vel"][1] *= -1

# Main simulation loop
running = True
frame_count = 0
particles = [
    {"pos": np.array([np.random.uniform(0, width), np.random.uniform(0, height)]),
     "vel": np.random.uniform(-particle_speed, particle_speed, size=2)}
    for _ in range(num_particles)
]

while running:
    time_delta = clock.tick(60) / 1000.0  # Time in seconds since last tick
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        manager.process_events(event)

    # Update variables from sliders
    num_particles = int(particle_slider.get_current_value())
    temperature = int(temperature_slider.get_current_value())
    width = int(width_slider.get_current_value())
    height = int(height_slider.get_current_value())

    # Recalculate particle speed based on updated temperature
    particle_speed = np.sqrt(3 * k_B * temperature / particle_mass)

    # Adjust the number of particles
    while len(particles) < num_particles:
        particles.append({
            "pos": np.array([np.random.uniform(0, width), np.random.uniform(0, height)]),
            "vel": np.random.uniform(-particle_speed, particle_speed, size=2)
        })
    while len(particles) > num_particles:
        particles.pop()

    # Clear the screen
    screen.fill((0, 0, 0))

    # Update particle positions and draw them
    for particle in particles:
        particle["pos"] += particle["vel"] * 0.01  # Time step scaling
        handle_wall_collisions(particle, width, height)
        pygame.draw.circle(screen, (0, 255, 255), particle["pos"].astype(int), particle_radius)

    # Calculate and display pressure
    pressure = len(particles) * particle_mass * particle_speed**2 / (3 * width * height)

    # Side panel for data
    pygame.draw.rect(screen, (50, 50, 50), (width, 0, 300, height))  # Side panel background
    screen.blit(font.render(f"Temperature: {temperature} K", True, (255, 255, 255)), (width + 10, 20))
    screen.blit(font.render(f"Particles: {len(particles)}", True, (255, 255, 255)), (width + 10, 50))
    screen.blit(font.render(f"Pressure: {pressure:.2e} Pa", True, (255, 255, 255)), (width + 10, 80))

    # Update histogram every 10 frames
    if frame_count % 10 == 0:
        histogram = draw_speed_distribution(particles)
    screen.blit(histogram, (width + 10, 120))

    manager.update(time_delta)
    manager.draw_ui(screen)

    pygame.display.flip()
    frame_count += 1

pygame.quit()
