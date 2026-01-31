"""
AI Self-Driving Car Game using NEAT-Python
Advanced Graphics Version - Professional Racing Track
"""

import pygame
import math
import sys
import neat
import os
import random

# Initialize Pygame
pygame.init()

# Screen settings
WIDTH = 1400
HEIGHT = 900
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("🏎️ AI Neural Racing - NEAT Evolution")

# Enhanced Color Palette
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (128, 128, 128)
DARK_GRAY = (30, 30, 30)

# Track Colors
TRACK_COLOR = (60, 60, 65)  # Dark asphalt
TRACK_BORDER = (255, 255, 255)  # White lines
CURB_RED = (220, 50, 50)
CURB_WHITE = (240, 240, 240)
GRASS_DARK = (34, 120, 34)
GRASS_LIGHT = (45, 140, 45)
SAND_COLOR = (194, 178, 128)

# Car Colors (gradient-like)
CAR_COLORS = [
    (255, 60, 60),    # Red
    (60, 180, 255),   # Blue
    (255, 200, 60),   # Yellow
    (60, 255, 120),   # Green
    (255, 120, 200),  # Pink
    (200, 120, 255),  # Purple
    (255, 150, 50),   # Orange
    (100, 255, 255),  # Cyan
]

# UI Colors
UI_BG = (20, 20, 30, 220)
UI_ACCENT = (0, 200, 255)
UI_TEXT = (255, 255, 255)
UI_SUCCESS = (50, 255, 100)
UI_WARNING = (255, 200, 50)

# Game settings
CAR_SIZE_X = 35
CAR_SIZE_Y = 18
CAR_SPEED = 6
ROTATION_SPEED = 5
SENSOR_LENGTH = 180
FPS = 60

# Generation counter
current_generation = 0
best_fitness_ever = 0

# Game control flags
restart_requested = False
quit_requested = False
paused = False
fullscreen = False

# Track and collision surfaces
TRACK_SURFACE = None
COLLISION_SURFACE = None
DECORATION_SURFACE = None


def create_smooth_track():
    """Create a professional-looking race track with curves"""
    global TRACK_SURFACE, COLLISION_SURFACE, DECORATION_SURFACE
    
    # Collision surface (simple black/white for detection)
    COLLISION_SURFACE = pygame.Surface((WIDTH, HEIGHT))
    COLLISION_SURFACE.fill(BLACK)
    
    # Visual track surface
    TRACK_SURFACE = pygame.Surface((WIDTH, HEIGHT))
    
    # Decoration surface (transparent overlay)
    DECORATION_SURFACE = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    
    # Draw grass background with texture
    draw_grass_background(TRACK_SURFACE)
    
    # Track width
    track_width = 100
    
    # Simplified oval track with smooth curves using thick lines
    # Center points for the track
    center_x, center_y = WIDTH // 2, HEIGHT // 2
    
    # Outer dimensions
    outer_rx = 550  # Horizontal radius
    outer_ry = 350  # Vertical radius
    
    # Inner dimensions
    inner_rx = outer_rx - track_width
    inner_ry = outer_ry - track_width
    
    # Generate oval points
    num_points = 100
    outer_points = []
    inner_points = []
    
    for i in range(num_points):
        angle = (2 * math.pi * i) / num_points
        
        # Outer oval
        ox = center_x + outer_rx * math.cos(angle)
        oy = center_y + outer_ry * math.sin(angle)
        outer_points.append((ox, oy))
        
        # Inner oval
        ix = center_x + inner_rx * math.cos(angle)
        iy = center_y + inner_ry * math.sin(angle)
        inner_points.append((ix, iy))
    
    # Draw track on collision surface (white = road)
    pygame.draw.polygon(COLLISION_SURFACE, WHITE, outer_points)
    pygame.draw.polygon(COLLISION_SURFACE, BLACK, inner_points)
    
    # Draw sand/gravel traps
    draw_sand_traps(TRACK_SURFACE, outer_points)
    
    # Draw asphalt track
    pygame.draw.polygon(TRACK_SURFACE, TRACK_COLOR, outer_points)
    pygame.draw.polygon(TRACK_SURFACE, GRASS_DARK, inner_points)
    
    # Draw grass pattern in inner area
    draw_inner_grass(TRACK_SURFACE, inner_points)
    
    # Draw curbs (red and white stripes)
    draw_curbs(TRACK_SURFACE, outer_points, inner_points)
    
    # Draw track lines
    pygame.draw.lines(TRACK_SURFACE, WHITE, True, outer_points, 4)
    pygame.draw.lines(TRACK_SURFACE, WHITE, True, inner_points, 4)
    
    # Draw center dashed line
    center_points = []
    mid_rx = (outer_rx + inner_rx) / 2
    mid_ry = (outer_ry + inner_ry) / 2
    for i in range(num_points):
        angle = (2 * math.pi * i) / num_points
        cx = center_x + mid_rx * math.cos(angle)
        cy = center_y + mid_ry * math.sin(angle)
        center_points.append((cx, cy))
    
    # Dashed center line
    for i in range(0, len(center_points), 4):
        if i + 1 < len(center_points):
            pygame.draw.line(TRACK_SURFACE, (150, 150, 150), 
                           center_points[i], center_points[i+1], 2)
    
    # Draw start/finish line
    draw_start_finish(TRACK_SURFACE, DECORATION_SURFACE, center_x - outer_rx + 30)
    
    # Draw decorations
    draw_decorations(DECORATION_SURFACE, inner_points)
    
    return outer_points, inner_points


def draw_grass_background(surface):
    """Draw textured grass background"""
    # Base grass color
    surface.fill(GRASS_DARK)
    
    # Add grass texture with random lighter patches
    for _ in range(500):
        x = random.randint(0, WIDTH)
        y = random.randint(0, HEIGHT)
        size = random.randint(20, 60)
        color_var = random.randint(-15, 15)
        color = (34 + color_var, 120 + color_var, 34 + color_var)
        pygame.draw.circle(surface, color, (x, y), size)


def draw_sand_traps(surface, outer_points):
    """Draw sand/gravel traps around corners"""
    # Expand outer points for sand traps
    sand_points = []
    cx, cy = WIDTH // 2, HEIGHT // 2
    
    for ox, oy in outer_points:
        dx = ox - cx
        dy = oy - cy
        length = math.sqrt(dx*dx + dy*dy)
        if length > 0:
            sand_points.append((
                ox + dx/length * 30,
                oy + dy/length * 30
            ))
    
    pygame.draw.polygon(surface, SAND_COLOR, sand_points)


def draw_inner_grass(surface, inner_points):
    """Draw grass pattern inside the track"""
    # Create inner grass with slight texture
    for _ in range(100):
        # Find random point inside inner area
        min_x = min(p[0] for p in inner_points)
        max_x = max(p[0] for p in inner_points)
        min_y = min(p[1] for p in inner_points)
        max_y = max(p[1] for p in inner_points)
        
        x = random.randint(int(min_x) + 50, int(max_x) - 50)
        y = random.randint(int(min_y) + 50, int(max_y) - 50)
        size = random.randint(10, 30)
        
        color = GRASS_LIGHT if random.random() > 0.5 else GRASS_DARK
        pygame.draw.circle(surface, color, (x, y), size)


def draw_curbs(surface, outer_points, inner_points):
    """Draw red and white curbs on track edges"""
    curb_width = 8
    segment_length = 15
    
    # Draw curbs along outer edge
    for i in range(len(outer_points)):
        p1 = outer_points[i]
        p2 = outer_points[(i + 1) % len(outer_points)]
        
        dx = p2[0] - p1[0]
        dy = p2[1] - p1[1]
        length = math.sqrt(dx*dx + dy*dy)
        
        if length > 0:
            segments = int(length / segment_length)
            for j in range(segments):
                t = j / segments
                x = p1[0] + dx * t
                y = p1[1] + dy * t
                color = CURB_RED if j % 2 == 0 else CURB_WHITE
                pygame.draw.circle(surface, color, (int(x), int(y)), curb_width)
    
    # Draw curbs along inner edge
    for i in range(len(inner_points)):
        p1 = inner_points[i]
        p2 = inner_points[(i + 1) % len(inner_points)]
        
        dx = p2[0] - p1[0]
        dy = p2[1] - p1[1]
        length = math.sqrt(dx*dx + dy*dy)
        
        if length > 0:
            segments = int(length / segment_length)
            for j in range(segments):
                t = j / segments
                x = p1[0] + dx * t
                y = p1[1] + dy * t
                color = CURB_RED if j % 2 == 0 else CURB_WHITE
                pygame.draw.circle(surface, color, (int(x), int(y)), curb_width)


def draw_track_lines(surface, center_points, outer_points, inner_points):
    """Draw racing lines and markings"""
    # White edge lines
    pygame.draw.lines(surface, WHITE, True, outer_points, 3)
    pygame.draw.lines(surface, WHITE, True, inner_points, 3)
    
    # Dashed center line
    for i in range(len(center_points)):
        if i % 2 == 0:
            p1 = center_points[i]
            p2 = center_points[(i + 1) % len(center_points)]
            pygame.draw.line(surface, (200, 200, 200), p1, p2, 2)


def draw_start_finish(track_surface, deco_surface, start_x=150):
    """Draw start/finish line and grid"""
    # Start/finish position
    start_y1 = HEIGHT // 2 - 50
    start_y2 = HEIGHT // 2 + 50
    
    # Checkered pattern
    square_size = 12
    for row in range(int((start_y2 - start_y1) / square_size)):
        for col in range(5):
            x = start_x + col * square_size
            y = start_y1 + row * square_size
            color = WHITE if (row + col) % 2 == 0 else BLACK
            pygame.draw.rect(track_surface, color, (x, y, square_size, square_size))


def draw_decorations(surface, inner_points):
    """Draw track decorations like trees, buildings, etc."""
    # Calculate center of inner area
    cx = sum(p[0] for p in inner_points) / len(inner_points)
    cy = sum(p[1] for p in inner_points) / len(inner_points)
    
    # Draw "pit area" building
    pygame.draw.rect(surface, (60, 60, 70), (cx - 100, cy - 60, 200, 120))
    pygame.draw.rect(surface, (80, 80, 90), (cx - 90, cy - 50, 180, 100))
    
    # Pit building text
    font = pygame.font.Font(None, 28)
    text = font.render("PIT LANE", True, WHITE)
    surface.blit(text, (cx - 45, cy - 10))
    
    # Draw some trees around inner area
    tree_positions = [
        (cx - 150, cy - 100), (cx + 150, cy - 100),
        (cx - 150, cy + 100), (cx + 150, cy + 100),
        (cx - 200, cy), (cx + 200, cy)
    ]
    
    for tx, ty in tree_positions:
        # Tree trunk
        pygame.draw.rect(surface, (101, 67, 33), (tx - 5, ty, 10, 20))
        # Tree foliage
        pygame.draw.circle(surface, (34, 100, 34), (int(tx), int(ty - 10)), 20)
        pygame.draw.circle(surface, (45, 120, 45), (int(tx), int(ty - 15)), 15)


def create_car_surface(color):
    """Create an advanced-looking car sprite"""
    surface = pygame.Surface((CAR_SIZE_X, CAR_SIZE_Y), pygame.SRCALPHA)
    
    # Shadow
    pygame.draw.ellipse(surface, (0, 0, 0, 50), (2, 2, CAR_SIZE_X - 4, CAR_SIZE_Y - 2))
    
    # Main body
    body_color = color
    darker = tuple(max(0, c - 40) for c in color)
    
    # Car body shape
    pygame.draw.rect(surface, body_color, (3, 3, CAR_SIZE_X - 10, CAR_SIZE_Y - 6), border_radius=3)
    
    # Front nose
    pygame.draw.polygon(surface, body_color, [
        (CAR_SIZE_X - 10, 3),
        (CAR_SIZE_X - 2, CAR_SIZE_Y // 2),
        (CAR_SIZE_X - 10, CAR_SIZE_Y - 3)
    ])
    
    # Cockpit/Window
    pygame.draw.ellipse(surface, (40, 40, 50), (8, 5, 12, CAR_SIZE_Y - 10))
    pygame.draw.ellipse(surface, (80, 150, 200), (9, 6, 10, CAR_SIZE_Y - 12))
    
    # Racing stripe
    pygame.draw.line(surface, WHITE, (5, CAR_SIZE_Y // 2), (CAR_SIZE_X - 5, CAR_SIZE_Y // 2), 2)
    
    # Wheels
    wheel_color = (30, 30, 30)
    pygame.draw.ellipse(surface, wheel_color, (2, 0, 8, 5))
    pygame.draw.ellipse(surface, wheel_color, (2, CAR_SIZE_Y - 5, 8, 5))
    pygame.draw.ellipse(surface, wheel_color, (CAR_SIZE_X - 14, 0, 8, 5))
    pygame.draw.ellipse(surface, wheel_color, (CAR_SIZE_X - 14, CAR_SIZE_Y - 5, 8, 5))
    
    # Rear wing hint
    pygame.draw.rect(surface, darker, (1, 2, 3, CAR_SIZE_Y - 4))
    
    return surface


# Create assets
create_smooth_track()
CAR_IMAGES = [create_car_surface(color) for color in CAR_COLORS]


class Car:
    def __init__(self, car_id=0):
        self.sprite = CAR_IMAGES[car_id % len(CAR_IMAGES)]
        self.color = CAR_COLORS[car_id % len(CAR_COLORS)]
        
        # Start Position - on the oval track (left side, middle)
        # Track center is at WIDTH//2, HEIGHT//2
        # Left side of track is at center_x - outer_rx + track_width/2
        self.x_pos = WIDTH // 2 - 550 + 50  # Left side of oval
        self.y_pos = HEIGHT // 2 - CAR_SIZE_Y // 2  # Middle vertically
        self.angle = 90  # Facing up (counterclockwise direction)
        self.speed = CAR_SPEED
        
        # NEAT Related
        self.alive = True
        self.distance_driven = 0
        self.time_alive = 0
        
        # Sensors
        self.radars = []
        self.radar_angles = [-90, -45, 0, 45, 90]

    def draw(self, win):
        """Draw the car with rotation and glow effect"""
        if not self.alive:
            return
            
        # Draw car shadow
        shadow = pygame.Surface((CAR_SIZE_X + 4, CAR_SIZE_Y + 4), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow, (0, 0, 0, 40), (0, 0, CAR_SIZE_X + 4, CAR_SIZE_Y + 4))
        rotated_shadow = pygame.transform.rotate(shadow, self.angle)
        shadow_rect = rotated_shadow.get_rect(center=(self.x_pos + CAR_SIZE_X//2 + 3, 
                                                       self.y_pos + CAR_SIZE_Y//2 + 3))
        win.blit(rotated_shadow, shadow_rect.topleft)
        
        # Draw car
        rotated_image = pygame.transform.rotate(self.sprite, self.angle)
        new_rect = rotated_image.get_rect(
            center=self.sprite.get_rect(topleft=(self.x_pos, self.y_pos)).center
        )
        win.blit(rotated_image, new_rect.topleft)

    def draw_radars(self, win):
        """Draw sensor lines with gradient effect"""
        for radar in self.radars:
            pos, dist = radar
            danger = 1 - (dist / SENSOR_LENGTH)
            
            # Gradient color from green to red
            r = int(255 * danger)
            g = int(255 * (1 - danger))
            color = (r, g, 0)
            
            center_x = self.x_pos + CAR_SIZE_X // 2
            center_y = self.y_pos + CAR_SIZE_Y // 2
            
            # Draw line with glow effect
            pygame.draw.line(win, (*color, 100), (center_x, center_y), pos, 4)
            pygame.draw.line(win, color, (center_x, center_y), pos, 2)
            
            # Draw endpoint circle with glow
            pygame.draw.circle(win, (*color, 150), pos, 6)
            pygame.draw.circle(win, color, pos, 4)

    def check_collision(self):
        """Check collision using collision surface"""
        check_x = int(self.x_pos + CAR_SIZE_X // 2)
        check_y = int(self.y_pos + CAR_SIZE_Y // 2)
        
        if not (0 <= check_x < WIDTH and 0 <= check_y < HEIGHT):
            self.alive = False
            return
        
        try:
            color = COLLISION_SURFACE.get_at((check_x, check_y))
            if color[0] < 50:  # Black = off track
                self.alive = False
        except IndexError:
            self.alive = False

    def update(self):
        """Update car position"""
        self.x_pos += math.cos(math.radians(self.angle)) * self.speed
        self.y_pos -= math.sin(math.radians(self.angle)) * self.speed
        
        self.distance_driven += self.speed
        self.time_alive += 1
        
        self.check_collision()
        self.update_radars()

    def update_radars(self):
        """Update sensor readings"""
        self.radars.clear()
        for degree in self.radar_angles:
            self.cast_ray(degree)

    def cast_ray(self, angle_offset):
        """Cast a ray to detect walls"""
        length = 0
        target_angle = math.radians(self.angle + angle_offset)
        
        start_x = self.x_pos + CAR_SIZE_X // 2
        start_y = self.y_pos + CAR_SIZE_Y // 2
        
        end_x, end_y = start_x, start_y
        
        while length < SENSOR_LENGTH:
            length += 5
            
            end_x = int(start_x + math.cos(target_angle) * length)
            end_y = int(start_y - math.sin(target_angle) * length)
            
            if not (0 <= end_x < WIDTH and 0 <= end_y < HEIGHT):
                break
            
            try:
                color = COLLISION_SURFACE.get_at((end_x, end_y))
                if color[0] < 50:
                    break
            except IndexError:
                break
        
        self.radars.append(((end_x, end_y), length))

    def get_data(self):
        """Get normalized sensor data"""
        return_data = [0.0] * 5
        for i, radar in enumerate(self.radars):
            return_data[i] = radar[1] / SENSOR_LENGTH
        return return_data


def toggle_fullscreen():
    """Toggle between fullscreen and windowed mode"""
    global WIN, fullscreen, WIDTH, HEIGHT
    
    fullscreen = not fullscreen
    
    if fullscreen:
        # Get the display info for fullscreen resolution
        display_info = pygame.display.Info()
        WIDTH = display_info.current_w
        HEIGHT = display_info.current_h
        WIN = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
    else:
        # Return to windowed mode
        WIDTH = 1400
        HEIGHT = 900
        WIN = pygame.display.set_mode((WIDTH, HEIGHT))
    
    # Recreate track surfaces with new dimensions
    create_smooth_track()
    
    pygame.display.set_caption("🏎️ AI Neural Racing - NEAT Evolution")


def eval_genomes(genomes, config):
    """Evaluate all genomes for one generation"""
    global current_generation, best_fitness_ever, restart_requested, quit_requested, paused
    current_generation += 1
    
    cars = []
    ge_list = []
    nets = []
    
    for i, (genome_id, genome) in enumerate(genomes):
        cars.append(Car(i))
        ge_list.append(genome)
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        nets.append(net)
        genome.fitness = 0
    
    clock = pygame.time.Clock()
    running = True
    ticks = 0
    max_ticks = 1500
    
    while running and len(cars) > 0 and ticks < max_ticks:
        clock.tick(FPS)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit_requested = True
                return
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE or event.key == pygame.K_q:
                    quit_requested = True
                    return
                if event.key == pygame.K_r:
                    restart_requested = True
                    return
                if event.key == pygame.K_p or event.key == pygame.K_SPACE:
                    paused = not paused
                if event.key == pygame.K_s:
                    # Skip to next generation
                    return
                if event.key == pygame.K_F11 or event.key == pygame.K_f:
                    toggle_fullscreen()
        
        # Handle pause
        if paused:
            draw_pause_screen()
            pygame.display.flip()
            continue
        
        ticks += 1
        
        # Update cars
        for i, car in enumerate(cars):
            if car.alive:
                ge_list[i].fitness += 0.1
                
                inputs = car.get_data()
                output = nets[i].activate(inputs)
                
                if output[0] > 0.5:
                    car.angle += ROTATION_SPEED
                if output[1] > 0.5:
                    car.angle -= ROTATION_SPEED
                
                car.update()
                
                # Update best fitness
                if ge_list[i].fitness > best_fitness_ever:
                    best_fitness_ever = ge_list[i].fitness
        
        # Remove dead cars
        for i in range(len(cars) - 1, -1, -1):
            if not cars[i].alive:
                ge_list[i].fitness += cars[i].distance_driven * 0.01
                if ge_list[i].fitness > best_fitness_ever:
                    best_fitness_ever = ge_list[i].fitness
                cars.pop(i)
                nets.pop(i)
                ge_list.pop(i)
        
        # Drawing
        WIN.blit(TRACK_SURFACE, (0, 0))
        WIN.blit(DECORATION_SURFACE, (0, 0))
        
        # Draw sensors first (behind cars)
        for car in cars:
            car.draw_radars(WIN)
        
        # Draw cars
        for car in cars:
            car.draw(WIN)
        
        # Draw UI
        draw_advanced_ui(len(cars), len(genomes), ticks, max_ticks)
        
        pygame.display.flip()


def draw_advanced_ui(alive, total, ticks, max_ticks):
    """Draw professional-looking UI"""
    # Main stats panel
    panel_width = 280
    panel_height = 200
    
    # Create panel surface with transparency
    panel = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
    
    # Panel background with gradient effect
    for i in range(panel_height):
        alpha = 200 - i // 3
        pygame.draw.line(panel, (20, 25, 40, alpha), (0, i), (panel_width, i))
    
    # Panel border
    pygame.draw.rect(panel, UI_ACCENT, (0, 0, panel_width, panel_height), 2, border_radius=10)
    
    # Title
    title_font = pygame.font.Font(None, 36)
    title = title_font.render("🧠 NEURAL RACING", True, UI_ACCENT)
    panel.blit(title, (15, 10))
    
    # Separator line
    pygame.draw.line(panel, UI_ACCENT, (15, 45), (panel_width - 15, 45), 2)
    
    # Stats
    font = pygame.font.Font(None, 28)
    stats = [
        ("Generation", str(current_generation), UI_TEXT),
        ("Cars Alive", f"{alive}/{total}", UI_SUCCESS if alive > total//2 else UI_WARNING),
        ("Time", f"{ticks}/{max_ticks}", UI_TEXT),
        ("Best Fitness", f"{best_fitness_ever:.1f}", UI_ACCENT),
    ]
    
    y = 55
    for label, value, color in stats:
        # Label
        label_surf = font.render(f"{label}:", True, (150, 150, 170))
        panel.blit(label_surf, (15, y))
        # Value
        value_surf = font.render(value, True, color)
        panel.blit(value_surf, (panel_width - 15 - value_surf.get_width(), y))
        y += 32
    
    # Progress bar for time
    bar_y = y + 5
    bar_width = panel_width - 30
    progress = ticks / max_ticks
    
    pygame.draw.rect(panel, (50, 50, 60), (15, bar_y, bar_width, 12), border_radius=6)
    pygame.draw.rect(panel, UI_ACCENT, (15, bar_y, int(bar_width * progress), 12), border_radius=6)
    
    WIN.blit(panel, (15, 15))
    
    # Legend panel (bottom right)
    legend_width = 200
    legend_height = 80
    legend = pygame.Surface((legend_width, legend_height), pygame.SRCALPHA)
    
    for i in range(legend_height):
        alpha = 180 - i // 2
        pygame.draw.line(legend, (20, 25, 40, alpha), (0, i), (legend_width, i))
    
    pygame.draw.rect(legend, (80, 80, 100), (0, 0, legend_width, legend_height), 1, border_radius=8)
    
    small_font = pygame.font.Font(None, 22)
    legend_text = small_font.render("Sensor Guide:", True, UI_TEXT)
    legend.blit(legend_text, (10, 8))
    
    # Green indicator
    pygame.draw.circle(legend, (0, 255, 0), (20, 38), 6)
    safe_text = small_font.render("Safe (far from wall)", True, (150, 255, 150))
    legend.blit(safe_text, (35, 30))
    
    # Red indicator
    pygame.draw.circle(legend, (255, 0, 0), (20, 60), 6)
    danger_text = small_font.render("Danger (near wall)", True, (255, 150, 150))
    legend.blit(danger_text, (35, 52))
    
    WIN.blit(legend, (WIDTH - legend_width - 15, HEIGHT - legend_height - 15))
    
    # Controls panel (bottom left)
    controls_width = 220
    controls_height = 130
    controls = pygame.Surface((controls_width, controls_height), pygame.SRCALPHA)
    
    for i in range(controls_height):
        alpha = 180 - i // 2
        pygame.draw.line(controls, (20, 25, 40, alpha), (0, i), (controls_width, i))
    
    pygame.draw.rect(controls, (80, 80, 100), (0, 0, controls_width, controls_height), 1, border_radius=8)
    
    small_font = pygame.font.Font(None, 22)
    controls_title = small_font.render("Controls:", True, UI_TEXT)
    controls.blit(controls_title, (10, 8))
    
    control_items = [
        ("[R]", "Restart"),
        ("[P/Space]", "Pause"),
        ("[S]", "Skip Generation"),
        ("[F/F11]", "Fullscreen"),
        ("[Q/ESC]", "Quit")
    ]
    
    y = 30
    for key, action in control_items:
        key_surf = small_font.render(key, True, UI_ACCENT)
        action_surf = small_font.render(action, True, (180, 180, 180))
        controls.blit(key_surf, (15, y))
        controls.blit(action_surf, (90, y))
        y += 20
    
    WIN.blit(controls, (15, HEIGHT - controls_height - 15))


def draw_pause_screen():
    """Draw pause overlay"""
    # Semi-transparent overlay
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 150))
    WIN.blit(overlay, (0, 0))
    
    # Pause text
    font_big = pygame.font.Font(None, 72)
    font_small = pygame.font.Font(None, 36)
    
    pause_text = font_big.render("PAUSED", True, UI_ACCENT)
    resume_text = font_small.render("Press P or SPACE to resume", True, WHITE)
    
    WIN.blit(pause_text, (WIDTH // 2 - pause_text.get_width() // 2, HEIGHT // 2 - 50))
    WIN.blit(resume_text, (WIDTH // 2 - resume_text.get_width() // 2, HEIGHT // 2 + 20))


def run_neat(config_path):
    """Run the NEAT algorithm"""
    global current_generation, best_fitness_ever, restart_requested, quit_requested, paused
    
    while True:
        # Reset game state
        current_generation = 0
        best_fitness_ever = 0
        restart_requested = False
        quit_requested = False
        paused = False
        
        # Recreate track
        create_smooth_track()
        
        config = neat.Config(
            neat.DefaultGenome,
            neat.DefaultReproduction,
            neat.DefaultSpeciesSet,
            neat.DefaultStagnation,
            config_path
        )
        
        population = neat.Population(config)
        population.add_reporter(neat.StdOutReporter(True))
        stats = neat.StatisticsReporter()
        population.add_reporter(stats)
        
        try:
            winner = population.run(eval_genomes, 50)
            
            if quit_requested:
                print("\nGame quit by user.")
                break
            
            if restart_requested:
                print("\n" + "="*40)
                print("   RESTARTING SIMULATION...")
                print("="*40 + "\n")
                continue
            
            print(f"\nBest genome:\n{winner}")
            
            # Show completion screen
            show_completion_screen(winner)
            
        except SystemExit:
            break
        
        break


def show_completion_screen(winner):
    """Show completion screen with options"""
    global restart_requested, quit_requested
    
    clock = pygame.time.Clock()
    
    while True:
        clock.tick(30)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    restart_requested = True
                    return
                if event.key == pygame.K_ESCAPE or event.key == pygame.K_q:
                    quit_requested = True
                    return
        
        # Draw completion screen
        WIN.blit(TRACK_SURFACE, (0, 0))
        
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        WIN.blit(overlay, (0, 0))
        
        font_big = pygame.font.Font(None, 72)
        font_med = pygame.font.Font(None, 42)
        font_small = pygame.font.Font(None, 32)
        
        # Title
        title = font_big.render("🏆 EVOLUTION COMPLETE! 🏆", True, UI_ACCENT)
        WIN.blit(title, (WIDTH // 2 - title.get_width() // 2, HEIGHT // 3 - 50))
        
        # Stats
        gen_text = font_med.render(f"Generations: {current_generation}", True, WHITE)
        fit_text = font_med.render(f"Best Fitness: {best_fitness_ever:.1f}", True, UI_SUCCESS)
        
        WIN.blit(gen_text, (WIDTH // 2 - gen_text.get_width() // 2, HEIGHT // 2 - 20))
        WIN.blit(fit_text, (WIDTH // 2 - fit_text.get_width() // 2, HEIGHT // 2 + 30))
        
        # Options
        restart_text = font_small.render("Press [R] to Restart", True, (150, 255, 150))
        quit_text = font_small.render("Press [Q] or [ESC] to Quit", True, (255, 150, 150))
        
        WIN.blit(restart_text, (WIDTH // 2 - restart_text.get_width() // 2, HEIGHT * 2 // 3 + 20))
        WIN.blit(quit_text, (WIDTH // 2 - quit_text.get_width() // 2, HEIGHT * 2 // 3 + 60))
        
        pygame.display.flip()


def main():
    """Main entry point"""
    print("\n" + "="*60)
    print("   🏎️  AI NEURAL RACING - NEAT Evolution  🧠")
    print("="*60)
    print("\n  Watch AI cars learn to race through evolution!")
    print("  Each generation gets smarter at navigating the track.")
    print("\n  Sensors:")
    print("  • Green = Safe distance from walls")
    print("  • Red = Danger! Close to walls")
    print("\n  Controls:")
    print("  • [R] Restart simulation")
    print("  • [P] or [Space] Pause/Resume")
    print("  • [S] Skip to next generation")
    print("  • [F] or [F11] Toggle Fullscreen")
    print("  • [Q] or [ESC] Quit game")
    print("  • [X] Close window button")
    print("="*60 + "\n")
    
    local_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(local_dir, "neat_config.txt")
    
    if not os.path.exists(config_path):
        print(f"Error: Config file not found at {config_path}")
        sys.exit(1)
    
    run_neat(config_path)
    pygame.quit()


if __name__ == "__main__":
    main()
