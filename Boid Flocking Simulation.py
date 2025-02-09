import pygame
import sys
import math
import random
from pygame.math import Vector2
from pygame.locals import *

# Constants
WIDTH = 1280
HEIGHT = 720
BOID_SIZE = 12
BACKGROUND_COLOR = (30, 30, 45)
BOID_COLOR = (200, 220, 255)
TRACE_COLOR = (0, 100, 150)  # Deep sea blue
FPS = 60

# Boid parameters
NUM_BOIDS = 150
MAX_SPEED = 6.5
MAX_FORCE = 0.5
PERCEPTION_RADIUS = 80
SEPARATION_WEIGHT = 1.8
ALIGNMENT_WEIGHT = 1.2
COHESION_WEIGHT = 1.0

class Boid:
    def __init__(self):
        self.position = Vector2(random.randint(0, WIDTH), random.randint(0, HEIGHT))
        angle = random.uniform(0, 2 * math.pi)
        self.velocity = Vector2(math.cos(angle), math.sin(angle)) * MAX_SPEED
        self.acceleration = Vector2(0, 0)
        self.path = []

    def edges(self):
        margin = 50
        turn_factor = 0.2
        
        if self.position.x < margin:
            self.velocity.x += turn_factor
        if self.position.x > WIDTH - margin:
            self.velocity.x -= turn_factor
        if self.position.y < margin:
            self.velocity.y += turn_factor
        if self.position.y > HEIGHT - margin:
            self.velocity.y -= turn_factor

    def apply_rules(self, boids, separation_weight, alignment_weight, cohesion_weight):
        separation = Vector2(0, 0)
        alignment = Vector2(0, 0)
        cohesion = Vector2(0, 0)
        total_sep = 0
        total_ali = 0
        total_coh = 0

        for boid in boids:
            if boid is self:
                continue
            distance = self.position.distance_to(boid.position)
            
            if distance < PERCEPTION_RADIUS:
                # Separation
                if distance < PERCEPTION_RADIUS * 0.3:
                    diff = self.position - boid.position
                    if diff.length_squared() > 0:
                        diff /= distance  # Weight by distance
                        separation += diff
                        total_sep += 1
                
                # Alignment
                alignment += boid.velocity
                total_ali += 1
                
                # Cohesion
                cohesion += boid.position
                total_coh += 1

        # Apply separation
        if total_sep > 0:
            separation /= total_sep
            if separation.length_squared() > 0:
                separation = separation.normalize() * MAX_SPEED
                steering = separation - self.velocity
                steering = self.limit_force(steering)
                self.acceleration += steering * separation_weight

        # Apply alignment
        if total_ali > 0:
            alignment /= total_ali
            if alignment.length_squared() > 0:
                alignment = alignment.normalize() * MAX_SPEED
                steering = alignment - self.velocity
                steering = self.limit_force(steering)
                self.acceleration += steering * alignment_weight

        # Apply cohesion
        if total_coh > 0:
            cohesion /= total_coh
            desired = cohesion - self.position
            if desired.length_squared() > 0:
                desired = desired.normalize() * MAX_SPEED
                steering = desired - self.velocity
                steering = self.limit_force(steering)
                self.acceleration += steering * cohesion_weight

    def limit_force(self, force):
        if force.length() > MAX_FORCE:
            return force.normalize() * MAX_FORCE
        return force

    def update(self):
        self.velocity += self.acceleration
        if self.velocity.length() > MAX_SPEED:
            self.velocity = self.velocity.normalize() * MAX_SPEED
        self.position += self.velocity
        self.acceleration *= 0
        self.path.append(self.position.copy())
        if len(self.path) > 100:
            self.path.pop(0)

    def draw(self, screen):
        angle = math.degrees(math.atan2(-self.velocity.y, self.velocity.x))
        original_points = [
            Vector2(1, 0),
            Vector2(-0.7, 0.3),
            Vector2(-0.5, 0),
            Vector2(-0.7, -0.3)
        ]
        scaled_points = [p * BOID_SIZE for p in original_points]
        rotated_points = [p.rotate(angle) for p in scaled_points]
        translated_points = [self.position + p for p in rotated_points]
        pygame.draw.polygon(screen, BOID_COLOR, [(p.x, p.y) for p in translated_points])

def draw_sliders(screen, separation_weight, alignment_weight, cohesion_weight):
    font = pygame.font.Font(None, 36)
    screen.blit(font.render("Separation", True, (255, 255, 255)), (10, 10))
    screen.blit(font.render("Alignment", True, (255, 255, 255)), (10, 60))
    screen.blit(font.render("Cohesion", True, (255, 255, 255)), (10, 110))
    
    pygame.draw.rect(screen, (200, 200, 200), (200, 10, 200, 20))
    pygame.draw.rect(screen, (200, 200, 200), (200, 60, 200, 20))
    pygame.draw.rect(screen, (200, 200, 200), (200, 110, 200, 20))
    
    pygame.draw.rect(screen, (100, 100, 255), (200, 10, int(separation_weight * 100), 20))
    pygame.draw.rect(screen, (100, 255, 100), (200, 60, int(alignment_weight * 100), 20))
    pygame.draw.rect(screen, (255, 100, 100), (200, 110, int(cohesion_weight * 100), 20))

def draw_buttons(screen, tracing, reset):
    font = pygame.font.Font(None, 36)
    pygame.draw.rect(screen, (100, 100, 255) if not tracing else (200, 200, 200), (10, 160, 150, 40))
    screen.blit(font.render("Trace Paths", True, (255, 255, 255)), (20, 170))
    
    pygame.draw.rect(screen, (255, 100, 100), (170, 160, 150, 40))
    screen.blit(font.render("Reset", True, (255, 255, 255)), (200, 170))

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Boid Flocking Simulation")
    clock = pygame.time.Clock()

    boids = [Boid() for _ in range(NUM_BOIDS)]
    separation_weight = SEPARATION_WEIGHT
    alignment_weight = ALIGNMENT_WEIGHT
    cohesion_weight = COHESION_WEIGHT
    tracing = False
    reset = False

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == MOUSEBUTTONDOWN:
                if 10 <= event.pos[0] <= 160 and 160 <= event.pos[1] <= 200:
                    tracing = not tracing
                if 170 <= event.pos[0] <= 320 and 160 <= event.pos[1] <= 200:
                    boids = [Boid() for _ in range(NUM_BOIDS)]
                    reset = True
                # Slider interaction
                if 200 <= event.pos[0] <= 400:
                    if 10 <= event.pos[1] <= 30:
                        separation_weight = (event.pos[0] - 200) / 200 * 3
                    if 60 <= event.pos[1] <= 80:
                        alignment_weight = (event.pos[0] - 200) / 200 * 3
                    if 110 <= event.pos[1] <= 130:
                        cohesion_weight = (event.pos[0] - 200) / 200 * 3

        screen.fill(BACKGROUND_COLOR)
        
        for boid in boids:
            boid.apply_rules(boids, separation_weight, alignment_weight, cohesion_weight)
            boid.update()
            boid.edges()
            boid.draw(screen)
            if tracing:
                if len(boid.path) > 1:
                    pygame.draw.lines(screen, TRACE_COLOR, False, [(p.x, p.y) for p in boid.path], 1)

        draw_sliders(screen, separation_weight, alignment_weight, cohesion_weight)
        draw_buttons(screen, tracing, reset)

        pygame.display.flip()
        clock.tick(FPS)

if __name__ == "__main__":
    main()
