import pygame as pg
import math
import opensimplex
import numpy as np


SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
BLACK = (0, 0, 0)
# GREEN = (0, 128, 0)
FPS = 60

DEEP_OCEAN = np.array([0, 30, 100])
SHALLOW_OCEAN = np.array([0, 75, 150])
BEACH = np.array([240, 240, 180])
GRASS = np.array([34, 139, 34])
MOUNTAIN = np.array([139, 69, 19])
SNOW = np.array([250, 250, 250])


pg.init()
screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pg.display.set_caption("Simple 3D Planet")
clock = pg.time.Clock()

class Light:
    def __init__(self, direction, intensity):
        self.direction = np.array(direction, dtype=float)
        self.intensity = intensity

    def update_direction(self, angle):
        self.direction[0] = math.cos(angle) 
        self.direction[2] = math.sin(angle)
        self.direction[1] = 0.0
        self.direction = self.direction / np.linalg.norm(self.direction)


def normalized(a, axis=-1, order=2):
    l2 = np.linalg.norm(a, ord=order, axis=axis)
    if l2 == 0:
        return a
    return a / l2

        
def apply_lighting(normal, light):
    light_dir = normalized(-light.direction)  
    normal = normalized(normal)
    light_power = np.dot(normal, light_dir) * light.intensity
    return max(0.2, light_power)


def lerp_color(color1, color2, t):
    return color1 * (1 - t) + color2 * t


def get_terrain_color(height):
    if height < -0.1:  # Deep ocean
        t = (-height - 0.1) / 0.9  # Normalize between -1 and -0.1
        return lerp_color(SHALLOW_OCEAN, DEEP_OCEAN, t)
    elif height < 0:  # Shallow ocean
        t = -height / 0.1  # Normalize between -0.1 and 0
        return lerp_color(BEACH, SHALLOW_OCEAN, t)
    elif height < 0.1:  # Beach
        t = height / 0.1  # Normalize between 0 and 0.1
        return lerp_color(BEACH, GRASS, t)
    elif height < 0.5:  # Grass to mountain
        t = (height - 0.1) / 0.4  # Normalize between 0.1 and 0.5
        return lerp_color(GRASS, MOUNTAIN, t)
    else:  # Mountain to snow
        t = (height - 0.5) / 0.5  # Normalize between 0.5 and 1
        return lerp_color(MOUNTAIN, SNOW, t)

def circle_normal_map(display: pg.Surface, radius: int, position: np.array, light: Light) -> None:
    opensimplex.random_seed()

    for x in range(-radius, radius + 1):
        for y in range(-radius, radius + 1):
            if (x * x) + (y * y) <= radius * radius:
        
                normal = np.array([x, y], dtype=float)
                
                normal[0] = -(radius - normal[0]) / radius + 1
                normal[1] = (radius - normal[1]) / radius - 1
                
                if normal[0] ** 2 + normal[1] ** 2 <= 1:
                   z = math.sqrt(1 - (normal[0] ** 2 + normal[1] ** 2))
                   normal = np.append(normal, z)
                else:
                   continue

                normal = normalized(normal)

                scale = 1.5
                terrain_value = (
                    opensimplex.noise3(normal[0] * scale, normal[1] * scale, normal[2] * scale) * 0.5 +
                    opensimplex.noise3(normal[0] * scale * 2, normal[1] * scale * 2, normal[2] * scale * 2) * 0.25 +
                    opensimplex.noise3(normal[0] * scale * 4, normal[1] * scale * 4, normal[2] * scale * 4) * 0.125 
                )
                
                terrain_height = terrain_value
                
                terrain_normal = normal * (1 + terrain_height * 0.2)  
                terrain_normal = normalized(terrain_normal)

                terrain_normal = normal * terrain_height
                terrain_normal = normalized(terrain_normal)

                light_power = apply_lighting(terrain_normal, light)
                
                base_color = get_terrain_color(terrain_height)
                
                color = (base_color * light_power).astype(int)
                color = np.clip(color, 0, 255)

                display.set_at((position[0] + x, position[1] + y), tuple(color))

running = True
light = Light(direction=[1, 0, 0], intensity=1.0)
angle = 0
rotation_speed = 0.5

while running:
    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False

    screen.fill(BLACK)

    light.update_direction(angle)

    center_position = np.array([SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2])
    circle_normal_map(screen, 200, center_position, light)


    pg.display.update()

    angle = (angle + rotation_speed) % (2 * math.pi)

    clock.tick(FPS)

pg.quit()

