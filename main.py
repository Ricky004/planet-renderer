import pygame as pg
import math
import opensimplex
import numpy as np


SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
BLACK = (0, 0, 0)
# GREEN = (0, 128, 0)
FPS = 60


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
    return max(0.1, light_power)


# def circle(display: pg.Surface, radius: int, position: np.array, color: tuple) -> None:
#     for x in range(-radius, radius, 1):
#         for y in range(-radius, radius, 1):
#             if (x * x) + (y * y) <= radius * radius:
#                 display.set_at((position[0] + x, position[1] + y), color)


def circle_normal_map(display: pg.Surface, radius: int, position: np.array, light: Light) -> None:
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
                
                light_power = apply_lighting(normal, light)
                
                # normal map
                # r = int((normal[0] + 1) * 127.5 * light_power) 
                # g = int((normal[1] + 1) * 127.5 * light_power)
                # b = int((normal[2] + 1) * 127.5 * light_power)

                # r = max(0, min(255, r))
                # g = max(0, min(255, g))
                # b = max(0, min(255, b))

                # display.set_at((position[0] + x, position[1] + y), (r, g, b))
                base_color = ((normal + 1) * 127.5).astype(int)
                color = (base_color * light_power).astype(int)
                
                color = np.clip(color, 0, 255)

                display.set_at((position[0] + x, position[1] + y), tuple(color))

# terrain_value = opensimplex.noise3(normal[0], normal[1], normal[2])

running = True
light = Light(direction=[1, 0, 0], intensity=1.0)
angle = 0
rotation_speed = 0.2

while running:
    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False

    screen.fill(BLACK)

    light.update_direction(angle)

    center_position = np.array([SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2])
    circle_normal_map(screen, 150, center_position, light)


    pg.display.update()

    angle = (angle + rotation_speed) % (2 * math.pi)

    clock.tick(FPS)

pg.quit()

