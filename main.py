"""
AI Self-Driving Car Game - Web Version
Custom Neural Network (no external dependencies)
Works with pygbag for browser deployment!
"""

import pygame
import math
import random
import asyncio
import time

# Initialize Pygame
pygame.init()

# Screen settings
WIDTH = 1200
HEIGHT = 750
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("AI Neural Racing - Web Demo")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
TRACK_COLOR = (60, 60, 65)
CURB_RED = (220, 50, 50)
CURB_WHITE = (240, 240, 240)
GRASS_DARK = (34, 120, 34)
GRASS_LIGHT = (45, 140, 45)
SAND_COLOR = (194, 178, 128)

CAR_COLORS = [
    (255, 60, 60), (60, 180, 255), (255, 200, 60), (60, 255, 120),
    (255, 120, 200), (200, 120, 255), (255, 150, 50), (100, 255, 255),
]

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
POPULATION_SIZE = 25

# Global state
current_generation = 0
best_fitness_ever = 0
paused = False

# Track surfaces
TRACK_SURFACE = None
COLLISION_SURFACE = None


class NeuralNetwork:
    """Simple feedforward neural network"""
    
    def __init__(self, layers=None):
        # Network structure: 5 inputs -> 6 hidden -> 2 outputs
        self.input_size = 5
        self.hidden_size = 6
        self.output_size = 2
        
        if layers:
            self.weights_ih = layers['w_ih']
            self.weights_ho = layers['w_ho']
            self.bias_h = layers['b_h']
            self.bias_o = layers['b_o']
        else:
            # Random initialization
            self.weights_ih = [[random.uniform(-1, 1) for _ in range(self.input_size)] 
                              for _ in range(self.hidden_size)]
            self.weights_ho = [[random.uniform(-1, 1) for _ in range(self.hidden_size)] 
                              for _ in range(self.output_size)]
            self.bias_h = [random.uniform(-1, 1) for _ in range(self.hidden_size)]
            self.bias_o = [random.uniform(-1, 1) for _ in range(self.output_size)]
    
    def tanh(self, x):
        """Activation function"""
        return math.tanh(max(-500, min(500, x)))
    
    def forward(self, inputs):
        """Forward pass through network"""
        # Hidden layer
        hidden = []
        for i in range(self.hidden_size):
            total = self.bias_h[i]
            for j in range(self.input_size):
                total += inputs[j] * self.weights_ih[i][j]
            hidden.append(self.tanh(total))
        
        # Output layer
        outputs = []
        for i in range(self.output_size):
            total = self.bias_o[i]
            for j in range(self.hidden_size):
                total += hidden[j] * self.weights_ho[i][j]
            outputs.append(self.tanh(total))
        
        return outputs
    
    def copy(self):
        """Create a copy of this network"""
        return NeuralNetwork({
            'w_ih': [row[:] for row in self.weights_ih],
            'w_ho': [row[:] for row in self.weights_ho],
            'b_h': self.bias_h[:],
            'b_o': self.bias_o[:]
        })
    
    def mutate(self, rate=0.2):
        """Mutate weights and biases"""
        for i in range(self.hidden_size):
            for j in range(self.input_size):
                if random.random() < rate:
                    self.weights_ih[i][j] += random.gauss(0, 0.5)
                    self.weights_ih[i][j] = max(-2, min(2, self.weights_ih[i][j]))
        
        for i in range(self.output_size):
            for j in range(self.hidden_size):
                if random.random() < rate:
                    self.weights_ho[i][j] += random.gauss(0, 0.5)
                    self.weights_ho[i][j] = max(-2, min(2, self.weights_ho[i][j]))
        
        for i in range(self.hidden_size):
            if random.random() < rate:
                self.bias_h[i] += random.gauss(0, 0.3)
        
        for i in range(self.output_size):
            if random.random() < rate:
                self.bias_o[i] += random.gauss(0, 0.3)


def create_track():
    """Create the race track"""
    global TRACK_SURFACE, COLLISION_SURFACE
    
    COLLISION_SURFACE = pygame.Surface((WIDTH, HEIGHT))
    COLLISION_SURFACE.fill(BLACK)
    
    TRACK_SURFACE = pygame.Surface((WIDTH, HEIGHT))
    TRACK_SURFACE.fill(GRASS_DARK)
    
    # Add grass texture
    for _ in range(200):
        x, y = random.randint(0, WIDTH), random.randint(0, HEIGHT)
        size = random.randint(15, 35)
        v = random.randint(-15, 15)
        pygame.draw.circle(TRACK_SURFACE, (34 + v, 120 + v, 34 + v), (x, y), size)
    
    # Track dimensions
    cx, cy = WIDTH // 2, HEIGHT // 2
    track_width = 90
    outer_rx, outer_ry = 480, 300
    inner_rx, inner_ry = outer_rx - track_width, outer_ry - track_width
    
    # Generate oval points
    num_points = 80
    outer_points, inner_points = [], []
    
    for i in range(num_points):
        angle = (2 * math.pi * i) / num_points
        outer_points.append((cx + outer_rx * math.cos(angle), cy + outer_ry * math.sin(angle)))
        inner_points.append((cx + inner_rx * math.cos(angle), cy + inner_ry * math.sin(angle)))
    
    # Collision surface (white = drivable)
    pygame.draw.polygon(COLLISION_SURFACE, WHITE, outer_points)
    pygame.draw.polygon(COLLISION_SURFACE, BLACK, inner_points)
    
    # Sand traps
    sand_points = []
    for ox, oy in outer_points:
        dx, dy = ox - cx, oy - cy
        length = math.sqrt(dx*dx + dy*dy)
        if length > 0:
            sand_points.append((ox + dx/length * 25, oy + dy/length * 25))
    pygame.draw.polygon(TRACK_SURFACE, SAND_COLOR, sand_points)
    
    # Track asphalt
    pygame.draw.polygon(TRACK_SURFACE, TRACK_COLOR, outer_points)
    pygame.draw.polygon(TRACK_SURFACE, GRASS_DARK, inner_points)
    
    # Curbs
    for points in [outer_points, inner_points]:
        for i in range(len(points)):
            p1, p2 = points[i], points[(i + 1) % len(points)]
            dx, dy = p2[0] - p1[0], p2[1] - p1[1]
            length = math.sqrt(dx*dx + dy*dy)
            if length > 0:
                for j in range(int(length / 12)):
                    t = j / (length / 12)
                    x, y = p1[0] + dx * t, p1[1] + dy * t
                    color = CURB_RED if j % 2 == 0 else CURB_WHITE
                    pygame.draw.circle(TRACK_SURFACE, color, (int(x), int(y)), 6)
    
    # Track lines
    pygame.draw.lines(TRACK_SURFACE, WHITE, True, outer_points, 3)
    pygame.draw.lines(TRACK_SURFACE, WHITE, True, inner_points, 3)
    
    # Start line
    start_x = cx - outer_rx + 25
    for row in range(8):
        for col in range(4):
            color = WHITE if (row + col) % 2 == 0 else BLACK
            pygame.draw.rect(TRACK_SURFACE, color, (start_x + col * 10, cy - 40 + row * 10, 10, 10))
    
    # Pit area text
    font = pygame.font.Font(None, 24)
    pygame.draw.rect(TRACK_SURFACE, (50, 50, 60), (cx - 70, cy - 40, 140, 80))
    text = font.render("PIT LANE", True, WHITE)
    TRACK_SURFACE.blit(text, (cx - 38, cy - 8))


def create_car_sprite(color):
    """Create car image"""
    surface = pygame.Surface((CAR_SIZE_X, CAR_SIZE_Y), pygame.SRCALPHA)
    
    # Shadow
    pygame.draw.ellipse(surface, (0, 0, 0, 50), (2, 2, CAR_SIZE_X - 4, CAR_SIZE_Y - 2))
    
    # Body
    pygame.draw.rect(surface, color, (3, 3, CAR_SIZE_X - 10, CAR_SIZE_Y - 6), border_radius=3)
    pygame.draw.polygon(surface, color, [
        (CAR_SIZE_X - 10, 3), 
        (CAR_SIZE_X - 2, CAR_SIZE_Y // 2), 
        (CAR_SIZE_X - 10, CAR_SIZE_Y - 3)
    ])
    
    # Window
    pygame.draw.ellipse(surface, (80, 150, 200), (9, 6, 10, CAR_SIZE_Y - 12))
    
    # Stripe
    pygame.draw.line(surface, WHITE, (5, CAR_SIZE_Y // 2), (CAR_SIZE_X - 5, CAR_SIZE_Y // 2), 2)
    
    # Wheels
    for pos in [(2, 0), (2, CAR_SIZE_Y - 5), (CAR_SIZE_X - 14, 0), (CAR_SIZE_X - 14, CAR_SIZE_Y - 5)]:
        pygame.draw.ellipse(surface, (30, 30, 30), (*pos, 8, 5))
    
    return surface


# Create assets
create_track()
CAR_SPRITES = [create_car_sprite(c) for c in CAR_COLORS]


class Car:
    """Self-driving car with neural network brain"""
    
    def __init__(self, car_id=0, brain=None):
        self.sprite = CAR_SPRITES[car_id % len(CAR_SPRITES)]
        self.color = CAR_COLORS[car_id % len(CAR_COLORS)]
        
        # Starting position (left side of oval)
        self.x = WIDTH // 2 - 480 + 45
        self.y = HEIGHT // 2 - CAR_SIZE_Y // 2
        self.angle = 90  # Facing up
        
        self.alive = True
        self.fitness = 0
        self.distance = 0
        
        self.brain = brain if brain else NeuralNetwork()
        self.radars = []
        self.radar_angles = [-90, -45, 0, 45, 90]
    
    def draw(self, win):
        if not self.alive:
            return
        rotated = pygame.transform.rotate(self.sprite, self.angle)
        rect = rotated.get_rect(center=(self.x + CAR_SIZE_X // 2, self.y + CAR_SIZE_Y // 2))
        win.blit(rotated, rect.topleft)
    
    def draw_radars(self, win):
        if not self.alive:
            return
        cx, cy = self.x + CAR_SIZE_X // 2, self.y + CAR_SIZE_Y // 2
        for pos, dist in self.radars:
            danger = 1 - (dist / SENSOR_LENGTH)
            color = (int(255 * danger), int(255 * (1 - danger)), 0)
            pygame.draw.line(win, color, (cx, cy), pos, 2)
            pygame.draw.circle(win, color, pos, 4)
    
    def check_collision(self):
        cx, cy = int(self.x + CAR_SIZE_X // 2), int(self.y + CAR_SIZE_Y // 2)
        if not (0 <= cx < WIDTH and 0 <= cy < HEIGHT):
            self.alive = False
            return
        try:
            if COLLISION_SURFACE.get_at((cx, cy))[0] < 50:
                self.alive = False
        except:
            self.alive = False
    
    def cast_ray(self, angle_offset):
        length = 0
        target = math.radians(self.angle + angle_offset)
        sx, sy = self.x + CAR_SIZE_X // 2, self.y + CAR_SIZE_Y // 2
        ex, ey = sx, sy
        
        while length < SENSOR_LENGTH:
            length += 5
            ex = int(sx + math.cos(target) * length)
            ey = int(sy - math.sin(target) * length)
            if not (0 <= ex < WIDTH and 0 <= ey < HEIGHT):
                break
            try:
                if COLLISION_SURFACE.get_at((ex, ey))[0] < 50:
                    break
            except:
                break
        
        self.radars.append(((ex, ey), length))
    
    def update_radars(self):
        self.radars.clear()
        for angle in self.radar_angles:
            self.cast_ray(angle)
    
    def get_inputs(self):
        return [r[1] / SENSOR_LENGTH for r in self.radars]
    
    def think(self):
        """Use neural network to decide movement"""
        inputs = self.get_inputs()
        outputs = self.brain.forward(inputs)
        
        if outputs[0] > 0.5:
            self.angle += ROTATION_SPEED
        if outputs[1] > 0.5:
            self.angle -= ROTATION_SPEED
    
    def update(self):
        if not self.alive:
            return
        
        # Move forward
        self.x += math.cos(math.radians(self.angle)) * CAR_SPEED
        self.y -= math.sin(math.radians(self.angle)) * CAR_SPEED
        
        self.distance += CAR_SPEED
        self.fitness += 0.1
        
        self.check_collision()
        self.update_radars()
        self.think()


def draw_ui(alive, total, ticks, max_ticks):
    """Draw game UI"""
    panel = pygame.Surface((250, 170), pygame.SRCALPHA)
    
    for i in range(170):
        pygame.draw.line(panel, (20, 25, 40, 200 - i // 3), (0, i), (250, i))
    pygame.draw.rect(panel, UI_ACCENT, (0, 0, 250, 170), 2, border_radius=10)
    
    font_title = pygame.font.Font(None, 30)
    font = pygame.font.Font(None, 24)
    
    panel.blit(font_title.render("NEURAL RACING", True, UI_ACCENT), (15, 10))
    pygame.draw.line(panel, UI_ACCENT, (15, 38), (235, 38), 2)
    
    stats = [
        ("Generation", str(current_generation), UI_TEXT),
        ("Cars Alive", f"{alive}/{total}", UI_SUCCESS if alive > total // 2 else UI_WARNING),
        ("Time", f"{ticks}/{max_ticks}", UI_TEXT),
        ("Best Fitness", f"{best_fitness_ever:.0f}", UI_ACCENT),
    ]
    
    y = 48
    for label, value, color in stats:
        panel.blit(font.render(f"{label}:", True, (150, 150, 170)), (15, y))
        val_surf = font.render(value, True, color)
        panel.blit(val_surf, (235 - val_surf.get_width(), y))
        y += 26
    
    # Progress bar
    pygame.draw.rect(panel, (50, 50, 60), (15, 150, 220, 10), border_radius=5)
    pygame.draw.rect(panel, UI_ACCENT, (15, 150, int(220 * ticks / max_ticks), 10), border_radius=5)
    
    WIN.blit(panel, (15, 15))
    
    # Controls
    hint_font = pygame.font.Font(None, 22)
    hint = hint_font.render("[R] Restart  [P] Pause  [S] Skip Gen", True, (180, 180, 180))
    WIN.blit(hint, (15, HEIGHT - 28))


def draw_pause():
    """Draw pause overlay"""
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 150))
    WIN.blit(overlay, (0, 0))
    
    font_big = pygame.font.Font(None, 72)
    font_small = pygame.font.Font(None, 36)
    
    text = font_big.render("PAUSED", True, UI_ACCENT)
    WIN.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2 - 40))
    
    text2 = font_small.render("Press P or SPACE to resume", True, WHITE)
    WIN.blit(text2, (WIDTH // 2 - text2.get_width() // 2, HEIGHT // 2 + 20))


def create_next_generation(cars):
    """Create next generation using genetic algorithm"""
    # Sort by fitness
    cars.sort(key=lambda c: c.fitness + c.distance * 0.01, reverse=True)
    
    new_brains = []
    
    # Keep top performers
    elite_count = max(2, POPULATION_SIZE // 5)
    for i in range(elite_count):
        new_brains.append(cars[i].brain.copy())
    
    # Create offspring from top performers
    while len(new_brains) < POPULATION_SIZE:
        parent = cars[random.randint(0, elite_count - 1)]
        child_brain = parent.brain.copy()
        child_brain.mutate(0.2)
        new_brains.append(child_brain)
    
    return new_brains


async def run_generation(brains=None):
    """Run one generation of cars"""
    global current_generation, best_fitness_ever, paused
    
    current_generation += 1
    
    # Create cars
    cars = []
    for i in range(POPULATION_SIZE):
        brain = brains[i] if brains and i < len(brains) else None
        cars.append(Car(i, brain))
    
    clock = pygame.time.Clock()
    ticks = 0
    max_ticks = 1200
    skip = False
    restart = False
    
    while ticks < max_ticks and any(c.alive for c in cars):
        clock.tick(FPS)
        
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None, True, False  # Quit
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p or event.key == pygame.K_SPACE:
                    paused = not paused
                if event.key == pygame.K_s:
                    skip = True
                if event.key == pygame.K_r:
                    restart = True
        
        if restart:
            return None, False, True
        
        if paused:
            draw_pause()
            pygame.display.flip()
            await asyncio.sleep(0)
            continue
        
        if skip:
            break
        
        ticks += 1
        
        # Update cars
        for car in cars:
            if car.alive:
                car.update()
                if car.fitness > best_fitness_ever:
                    best_fitness_ever = car.fitness
        
        # Draw
        WIN.blit(TRACK_SURFACE, (0, 0))
        
        for car in cars:
            car.draw_radars(WIN)
        for car in cars:
            car.draw(WIN)
        
        alive_count = sum(1 for c in cars if c.alive)
        draw_ui(alive_count, POPULATION_SIZE, ticks, max_ticks)
        
        pygame.display.flip()
        await asyncio.sleep(0)  # Yield to browser
    
    return cars, False, False


async def main():
    """Main game loop"""
    global current_generation, best_fitness_ever
    
    print("AI Neural Racing - Web Version")
    print("Cars learn to drive using neural networks!")
    
    while True:
        # Reset for new run - reseed random for different behavior each time
        random.seed(time.time() * 1000)
        
        current_generation = 0
        best_fitness_ever = 0
        brains = None
        create_track()
        
        restart_simulation = False
        
        # Run generations
        for gen in range(50):
            result = await run_generation(brains)
            
            cars, quit_game, restart = result
            
            if quit_game:
                return
            
            if restart:
                restart_simulation = True
                break
            
            if cars:
                # Create next generation
                brains = create_next_generation(cars)
        
        if restart_simulation:
            continue
        
        # Show completion
        clock = pygame.time.Clock()
        waiting = True
        
        while waiting:
            clock.tick(30)
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        waiting = False
            
            # Draw completion screen
            WIN.blit(TRACK_SURFACE, (0, 0))
            
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            WIN.blit(overlay, (0, 0))
            
            font_big = pygame.font.Font(None, 64)
            font_med = pygame.font.Font(None, 36)
            
            text1 = font_big.render("EVOLUTION COMPLETE!", True, UI_ACCENT)
            text2 = font_med.render(f"Generations: {current_generation}", True, WHITE)
            text3 = font_med.render(f"Best Fitness: {best_fitness_ever:.0f}", True, UI_SUCCESS)
            text4 = font_med.render("Press [R] to Restart", True, (150, 255, 150))
            
            WIN.blit(text1, (WIDTH // 2 - text1.get_width() // 2, HEIGHT // 3))
            WIN.blit(text2, (WIDTH // 2 - text2.get_width() // 2, HEIGHT // 2))
            WIN.blit(text3, (WIDTH // 2 - text3.get_width() // 2, HEIGHT // 2 + 45))
            WIN.blit(text4, (WIDTH // 2 - text4.get_width() // 2, HEIGHT // 2 + 110))
            
            pygame.display.flip()
            await asyncio.sleep(0)


# Entry point for pygbag
asyncio.run(main())
