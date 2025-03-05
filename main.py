import pygame
from pygame.locals import *
from powerup import *
import random
import math
import os
from PIL import Image
import ctypes
import json

from render_check import *

with open("config.json") as json_config_file:
    config = json.load(json_config_file)
    json_config_file.close()

# Initialize Pygame
pygame.init()

# Window settings
flags =  DOUBLEBUF | NOFRAME

screen_info = pygame.display.Info()
monitor_width = screen_info.current_w
monitor_height = screen_info.current_h
WIDTH_OFFSET, HEIGHT_OFFSET = config['window_settings']['WIDTH_OFFSET'], config['window_settings']['HEIGHT_OFFSET']
WIDTH, HEIGHT = screen_info.current_w - WIDTH_OFFSET - config['window_settings']['LEFT_X_PADDING'], monitor_height - HEIGHT_OFFSET
# Calculate position next to the right edge
start_x = config['window_settings']['LEFT_X_PADDING']  # Position at the right edge
start_y = (monitor_height // 2) - (HEIGHT // 2)  # Center vertically
os.environ['SDL_VIDEO_WINDOW_POS'] = f'{start_x},{start_y}'

screen = pygame.display.set_mode((WIDTH, HEIGHT), flags, 16)
pygame.event.set_allowed([QUIT, KEYDOWN, KEYUP])
pygame.display.set_caption("Wallpaper Royale")



# Colors and fonts
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)  # Color for the power-up
GREEN = (0, 255, 0)  # Color for the power-up
BLUE = (0, 0, 255)  # Color for the power-up
base_font_size = 36  # Base font size

# Circle settings
INITIAL_HEALTH = config['circle_settings']['INITIAL_HEALTH']  # Starting health for each circle
MAX_HEALTH_PER_RADIUS = config['circle_settings']['MAX_HEALTH_PER_RADIUS']
HEALTH_EXPONENT_FOR_SCALE = config['circle_settings']['HEALTH_EXPONENT_FOR_SCALE']
MIN_START_RADIUS = config['circle_settings']['MIN_START_RADIUS']
MAX_START_RADIUS = config['circle_settings']['MAX_START_RADIUS']
MAX_START_VEL_X = config['circle_settings']['MAX_START_VEL_X']
MAX_START_VEL_Y = config['circle_settings']['MAX_START_VEL_Y']
MAX_VEL_X = config['circle_settings']['MAX_VEL_X']
MAX_VEL_Y = config['circle_settings']['MAX_VEL_Y']
BUFFER_COUNT = config['circle_settings']['BUFFER_COUNT']

# Combat settings
RAD_TO_STRENGTH = config['combat_settings']['RAD_TO_STRENGTH']
RADIUS_EXPONENT_FOR_STRENGTH = config['combat_settings']['RADIUS_EXPONENT_FOR_STRENGTH']
WALL_DAMAGE = config['combat_settings']['WALL_DAMAGE']


# Frame rate control
FPS = config['fps_control']['FPS']
clock = pygame.time.Clock()



# Directory Initializing
script_directory = None
image_paths = None


# Get the window handle from pygame's window manager info.
wm_info = pygame.display.get_wm_info()
hwnd = wm_info.get('window')  # This is available on Windows


# Helper function to create a circular mask
def create_circular_mask(image, radius, image_name):
    """Create a circular mask for an image."""
    #print(f"{image_name}: + {radius * 2}, {radius * 2}")
    mask = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
    pygame.draw.circle(mask, (255, 255, 255, 255), (radius, radius), radius)
    image = pygame.transform.smoothscale(image, (radius * 2, radius * 2))
    image.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    return image

class Circle:
    """Circle object with physics, image rendering, health, and strength."""
    invincible_duration = 0
    
    def __init__(self, Id, x, y, vel_x, vel_y, radius, image_path, save):
        self.Id = Id  # Store the circle's ID
        self.x = x
        self.y = y
        self.vel_x = vel_x
        self.vel_y = vel_y
        self.radius = radius  # Unique radius for each circle
        self.health_percentage = INITIAL_HEALTH  # Health of the circle
        
        # Load the image with a circular mask
        self.image_path = image_path
        

        self.save = save
        self.health_percentage += self.save['health_buff']
        self.strength_buff = self.save['strength_buff']
        self.radius += self.save['radius_buff']

        self.player_name = os.path.basename(os.path.basename(self.image_path).split('/')[-1]).split('.')[0]
        self.image = create_circular_mask(pygame.image.load(self.image_path).convert_alpha(), self.radius, self.player_name)
        

        self.update_health()


    def update(self, delta_time):
        """Update the position of the circle and handle wall collisions."""
        if (self.vel_x != 0):
            self.vel_x = min(abs(self.vel_x), MAX_VEL_X) * (abs(self.vel_x)/self.vel_x)
        if (self.vel_y != 0):
            self.vel_y = min(abs(self.vel_y), MAX_VEL_Y) * (abs(self.vel_y)/self.vel_y)
        
        if delta_time != 0:
            self.x += self.vel_x * (FPS / clock.get_time())
            self.y += self.vel_y * (FPS / clock.get_time())
            self.update_buff(delta_time)
            self.handle_wall_collision()
            
            self.update_health()
        

    def handle_wall_collision(self):
        """Bounce off the walls."""
        if self.x - self.radius <= 0 or self.x + self.radius >= WIDTH:
            if self.x - self.radius <= 0:
                self.vel_x = abs(self.vel_x)
            else:
                self.vel_x = -abs(self.vel_x)
            self.health -= WALL_DAMAGE
            
        if self.y - self.radius <= 0 or self.y + self.radius >= HEIGHT:
            if self.y - self.radius <= 0:
                self.vel_y = abs(self.vel_y)
            else:
                self.vel_y = -abs(self.vel_y)
            self.health -= WALL_DAMAGE

    def draw(self, surface):
        """Draw the circle, its health, and strength."""
        if self.invincible_duration > 0:
            pygame.draw.circle(surface, BLACK, (self.x, self.y), self.radius + INVINCIBLE_SHIELD_RADIUS)
        
        # Draw the circle image
        surface.blit(self.image, (self.x - self.radius, self.y - self.radius))

        # Create a scaled font size based on radius
        scaled_font_size = int(self.radius * 0.5)  # Adjust the scaling factor as needed
        font = pygame.font.Font(None, scaled_font_size)

        # Render the health as text (and strength for debugging) as integers
        if (self.strength_buff == 0):
            player_text = f"{self.player_name} (HP: {round(self.health, 1)})"
        else:
            player_text = f"{self.player_name} (HP: {round(self.health, 1)} (+STR: {self.strength_buff})"
        
        text = font.render(player_text, True, BLACK)

        # Position the text above the circle
        text_rect = text.get_rect(center=(self.x, self.y - self.radius - 10))  # 10 pixels above the circle
        surface.blit(text, text_rect)
        
    def get_mass(self):
        return math.pi * self.radius * self.radius

    def increase_speed(self):
        """Increase the circle's speed."""
        self.vel_x *= VEL_X_MULT
        self.vel_y *= VEL_Y_MULT

    def increase_scale(self, increase_amount):
        self.change_scale(self.radius + increase_amount)

    def change_scale(self, new_scale):
        self.radius = new_scale
        self.update_health()
        self.image = create_circular_mask(pygame.image.load(self.image_path).convert_alpha(), self.radius, self.player_name)

    def add_health_percentage(self, added_percentage):
        self.health_percentage += added_percentage
        self.update_health()

    def update_health_percentage(self):
        self.health_percentage = (self.health / pow(self.radius * MAX_HEALTH_PER_RADIUS, HEALTH_EXPONENT_FOR_SCALE)) * 100
        
    def update_health(self):
        self.health = (self.health_percentage/100) * pow(self.radius * MAX_HEALTH_PER_RADIUS, HEALTH_EXPONENT_FOR_SCALE)


    def calculate_damage_before_buff(self):
        return round(pow(self.radius, RADIUS_EXPONENT_FOR_STRENGTH) * RAD_TO_STRENGTH, 1)   

    def calculate_damage(self):
        
        return self.calculate_damage_before_buff() + self.strength_buff

    def give_invincible(self, duration):
        self.invincible_duration = duration

    def update_buff(self, delta_time):

        #self.invincible_duration = max(self.invincible_duration - delta_time, 0)
        return
        

    
    def apply_damage(self, damage):
        """Apply damage to the circle's health."""
        self.health -= damage
        if self.health < 0:
            self.health = 0  # Ensure health doesn't go below 0

        self.update_health_percentage()

def handle_circle_collision(c1, c2):
    """Detect and handle elastic collision between two circles."""
    dx = c1.x - c2.x
    dy = c1.y - c2.y
    distance = math.sqrt(dx ** 2 + dy ** 2)

    if distance <= c1.radius + c2.radius:

        # Apply damage based on radius
        damage_to_c2 = c1.calculate_damage()
        damage_to_c1 = c2.calculate_damage()

        if c1.invincible_duration > 0:
            damage_to_c1 = 0
            c1.invincible_duration -= 1
        if c2.invincible_duration > 0:
            damage_to_c2 = 0
            c2.invincible_duration -= 1

        if c1.save is c2.save:
            damage_to_c1 = 0
            damage_to_c2 = 0
            
        c1_will_die = damage_to_c1 > c1.health
        c2_will_die = damage_to_c2 > c2.health

        if c1_will_die and c2_will_die:
            if c1.health > c2.health:
                c1.vel_x = c1.vel_x +c2.vel_x
                c1.vel_y = c1.vel_y +c2.vel_y
                
                c2.apply_damage(damage_to_c2)  # c2 takes damage from c1
            elif c2.health > c1.health:
                c2.vel_x = c2.vel_x +c1.vel_x
                c2.vel_y = c2.vel_y +c1.vel_y
                
                c1.apply_damage(damage_to_c1)  # c1 takes damage from c2
            return
        elif c1_will_die and not c2_will_die:
            c2.vel_x = c2.vel_x +c1.vel_x
            c2.vel_y = c2.vel_y +c1.vel_y
            
            c2.apply_damage(damage_to_c2)  # c2 takes damage from c1
            c1.apply_damage(damage_to_c1)  # c1 takes damage from c2
            return
        elif not c1_will_die and c2_will_die:
            c1.vel_x = c1.vel_x +c2.vel_x
            c1.vel_y = c1.vel_y +c2.vel_y
            
            c2.apply_damage(damage_to_c2)  # c2 takes damage from c1
            c1.apply_damage(damage_to_c1)  # c1 takes damage from c2
            return
        else:
            # Normalize the direction vector
            nx = dx / distance
            ny = dy / distance

            # Calculate relative velocity
            dvx = c1.vel_x - c2.vel_x
            dvy = c1.vel_y - c2.vel_y

            # Calculate the velocity along the normal
            velocity_along_normal = dvx * nx + dvy * ny

            if velocity_along_normal > 0:
                return  # Prevent sticking

            # Get the masses for the impulse calculation
            m1 = c1.get_mass()
            m2 = c2.get_mass()
            
            # Calculate impulse scalar
            impulse = -(2 * velocity_along_normal) / (1/m1 + 1/m2)  # Each circle has mass of 1

            # Apply the impulse to both circles
            c1.vel_x += impulse * nx / m1
            c1.vel_y += impulse * ny / m1
            c2.vel_x -= impulse * nx / m2
            c2.vel_y -= impulse * ny / m2
            
            c2.apply_damage(damage_to_c2)  # c2 takes damage from c1
            c1.apply_damage(damage_to_c1)  # c1 takes damage from c2


        

    



def check_power_up_collision(circle, power_up):
    """Check if a circle collides with a power-up."""
    dx = circle.x - power_up.x
    dy = circle.y - power_up.y
    distance = math.sqrt(dx ** 2 + dy ** 2)

    if distance <= circle.radius + POWER_UP_RADIUS:
        return True
    return False

def create_circles(count, image_path_set, player_saves):
    """Create a list of circles with unique IDs and random radii."""
    circles = []
    for i in range(count):
        radius = random.randint(MIN_START_RADIUS, MAX_START_RADIUS)  # Random radius between min and max radius
        x = random.randint(radius, WIDTH - radius)
        y = random.randint(radius, HEIGHT - radius)
        vel_x = random.randint(-MAX_START_VEL_X, MAX_START_VEL_X)
        vel_y = random.randint(-MAX_START_VEL_Y, MAX_START_VEL_Y)
        image_path = image_path_set[i]
        circle_save = None
        for save in player_saves:
            if (save['player_name'] == get_circle_name(image_path)):
                circle_save = save
        new_circle = Circle(i, x, y, vel_x, vel_y, radius, image_path, circle_save)
        circles.append(new_circle)
    return circles

def create_duplicate_circle(circle, circles):
    Id = circle.Id
    radius = (circle.radius - circle.save['radius_buff']) * DUPE_RADIUS_RATIO
    x = circle.x
    y = circle.y
    vel_x = circle.vel_x
    vel_y = circle.vel_y
    image_path = circle.image_path
    circle_save = circle.save
    dupe_circle = Circle(Id, x + radius * 7/3, y + radius * 7/3, vel_x, vel_y, radius, image_path, circle_save)
    circle.change_scale(radius)
    dupe_circle.health_percentage = circle.health_percentage
    dupe_circle.update_health()
    circles.append(dupe_circle)

    return dupe_circle

def get_circle_name(image_path):
    return os.path.basename(os.path.basename(image_path).split('/')[-1]).split('.')[0]

def get_all_circle_names(image_path_set):
    names = []
    for path in image_path_set:
        names.append(get_circle_name(path))
    return names



def display_message(surface, message):
    """Display a message at the center of the screen."""
    font = pygame.font.Font(None, 70)  # Big font size for the message
    text = font.render(message, True, BLACK)
    text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2))  # Center the text
    surface.blit(text, text_rect)





# Function to check if a file is an image
def is_image_file(file):
    valid_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.jfif']
    return os.path.splitext(file)[1].lower() in valid_extensions

# Function to fetch all image paths in a directory
def fetch_image_paths_in_folder(folder_path):
    image_paths = []
    
    # Iterate through all files in the directory
    for file in os.listdir(folder_path):
        file_path = os.path.join(folder_path, file)
        
        # If it's an image file, append its path
        if is_image_file(file_path):
            image_paths.append(file_path)
            
    
    return image_paths

script_directory = os.path.dirname(os.path.abspath(__file__))
image_paths = fetch_image_paths_in_folder(script_directory + "/images")




def load_saves():
    with open('saves/saves.json', 'r', encoding='utf-8') as file:
        loaded_data = json.load(file)
        file.close()

        
    loaded_player_saves = loaded_data

    all_names = get_all_circle_names(image_paths)
    for save in loaded_data:
        save_name = save['player_name']
        if save_name in all_names:
            all_names.remove(save_name)
    for missing_name in all_names:
        new_player = add_player(missing_name)
        loaded_player_saves.append(new_player)
        save_data(loaded_player_saves)
    return loaded_player_saves



def add_player(player_name):
    
    added_player = {
        'player_name': player_name,
        'win_count' : 0,
        'health_buff': 0,
        'strength_buff': 0,
        'radius_buff': 0,
        'win_sound_effect_path': ''
    }
    print(f"Added Player: {player_name}")
    return added_player


def save_data(player_data_saved):
    player_data_saved = sort_players_by_win(player_data_saved)

    # Save the list of dictionaries to a JSON file
    with open('saves/saves.json', 'w', encoding='utf-8') as file:
        json.dump(player_data_saved, file, indent=4)
        file.close()



def sort_players_by_win(players_being_sorted):
    sorted_players = sorted(players_being_sorted, key=lambda x: x['win_count'], reverse=True)
    return sorted_players


player_saves = load_saves()



def get_players(circles):
    players = []

    for circle in circles:
        if not circle.player_name in players:
            players.append(circle.player_name)
    return players



def spawn_power_up(power_ups):
    power_up_x = random.randint(POWER_UP_RADIUS, WIDTH - POWER_UP_RADIUS)
    power_up_y = random.randint(POWER_UP_RADIUS, HEIGHT - POWER_UP_RADIUS)
    
    
    power_up_type = random.choices(power_up_ids, weights=power_up_weights, k=1)[0]

    # print(f"{power_up_type} chosen, which has a weight of {POWER_UP_TYPES[power_up_type]}")
    
    power_up = PowerUp(power_up_x, power_up_y, power_up_type)
    power_ups.append(power_up)








def game_loop():

    # Create the initial array of circles
    circles = create_circles(len(image_paths), image_paths, player_saves)

    # Power-up management
    power_ups = []
    power_up_timer = 0

    # Pause management
    pause_start_time = None
    pause_duration = 2 * FPS  # 2 seconds in terms of frames
    is_paused = False
    message_display_time = 2 * FPS  # Duration to display the message (2 seconds)
    message_start_time = None
    message = ""
    winner_id = -1  # Variable to store the winner's ID

    buffer_pos = 0
    is_buffer = False

    rendering_enabled = True  # Flag to enable/disable rendering

    print_period = 10
    print_count_point = 0

    rendering_check_period = 10
    rendering_check_point = 0

    # Main game loop
    running = True
    while running:

        # Troubleshooting Things
        #print_count_point += 1
        #if (print_count_point%print_period == 0) :
        #    print(rendering_enabled)
        
        
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            # Detect when the window is hidden or minimized
            if event.type == pygame.WINDOWHIDDEN:  # Correct event name!
                rendering_enabled = False
            elif event.type == pygame.WINDOWSHOWN:
                rendering_enabled = True


        # Check if the window is focused
        rendering_check_point += 1
        if (rendering_check_point % rendering_check_period == 0) :
            if not pygame.display.get_active() or not is_window_on_current_desktop(hwnd):
                rendering_enabled = False
            else:
                rendering_enabled = True
        
        

           

        # Check if the mouse button is held down to pause the game
        mouse_buttons = pygame.mouse.get_pressed()
        if mouse_buttons[0]:  # Left mouse button is held down
            clock.tick(FPS)  # Maintain the frame rate
            continue  # Skip the update and drawing logic to pause the game


        # Buffer Frame Handling
        if buffer_pos is BUFFER_COUNT:
            is_buffer = False
            buffer_pos = 0
        else:
            is_buffer = True
            buffer_pos += 1

        
        # If the game is paused
        if is_paused:
            # If paused, check if the pause duration has elapsed
            if pygame.time.get_ticks() - pause_start_time >= pause_duration * 1000 / FPS:
                # Check the game state to display the correct message
                    # Restart the game if the message duration has elapsed
        
                circles = create_circles(len(image_paths), image_paths, player_saves)  # Restart with a new set of circles
                power_ups = []  # Reset power-up
                message = ""  # Clear the message
                winner_id = -1  # Reset winner ID

                message_start_time = pygame.time.get_ticks()  # Start message display timer
                is_paused = False  # Reset paused state
            else:
                continue  # Skip the update and drawing logic if paused

        
            
        for i in range(len(circles)):
            circles[i].update(clock.get_time())

        # Update each circle
        if not is_buffer:
            
            # Handle collisions between circles
            for i in range(len(circles)):
                for j in range(i + 1, len(circles)):
                    handle_circle_collision(circles[i], circles[j])

            # Remove circles with 0 health
            circles = [c for c in circles if c.health > 0]

            # Handle power-ups
            power_up_timer += 1
            if power_up_timer >= POWER_UP_SPAWN_RATE and len(power_ups) < MAX_POWER_UP_COUNT:
                spawn_power_up(power_ups)
                power_up_timer = 0

            # Check for power-up collisions
            if len(power_ups) > 0:
                for power_up in power_ups:
                    for circle in circles:
                        if check_power_up_collision(circle, power_up):
                            power_up_return = power_up.use_power_up(circle, circles)
                            if (power_up_return == "dupe"): create_duplicate_circle(circle, circles)
                            elif (power_up_return == "teleport"):
                                circle.x = random.randint(int(circle.radius), int(WIDTH - circle.radius))
                                circle.y = random.randint(int(circle.radius), int(HEIGHT - circle.radius))
                            power_ups.remove(power_up)  # Remove the power-up once collected
                            break
        

            # Check for game over conditions
            if len(get_players(circles)) <= 1 and not is_paused:
                is_paused = True
                if len(get_players(circles)) == 1:
                    winner_name = circles[0].player_name
                    winner_image_path = circles[0].image_path
                    message = (f"{winner_name} kazandı!").upper()
                    circles[0].save['win_count'] += 1
                    save_data(player_saves)
                    SPI_SETDESKWALLPAPER = 20
    
                    # The ctypes function to change the wallpaper
                    result = ctypes.windll.user32.SystemParametersInfoW(SPI_SETDESKWALLPAPER, 0, winner_image_path, 3)
                elif len(circles) == 0:
                    message = "Draw!"
                pause_start_time = pygame.time.get_ticks()  # Start the pause timer

        if rendering_enabled:
            
            # Draw everything
            screen.fill(WHITE)
            for circle in circles:
                circle.draw(screen)

            if (len(power_ups) > 0):
                for power_up in power_ups:
                    power_up.draw(screen)
        

            # Display the message if the game is paused
            if is_paused:
                if message:
                    display_message(screen, message)

            pygame.display.flip()  # Update the display
        #else:
            #pygame.time.delay(int(1000/60))  # Add a small delay to reduce CPU usage
        clock.tick(FPS)  # Maintain the frame rate


    
    # Quit Pygame
    pygame.quit()



if __name__ == "__main__":
    print("Ladies and gentleman, this system controls the game.")
    game_loop()
