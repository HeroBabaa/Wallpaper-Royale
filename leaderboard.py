import pygame
from pygame.locals import *
import math
import json
import os
import time

from render_check import *

def run_leaderboard():
        
        with open("config.json") as json_config_file:
            config = json.load(json_config_file)
        


        # Initialize Pygame
        pygame.init()
    
        LEADERBOARD_screen_info = pygame.display.Info()
        LEADERBOARD_monitor_width = LEADERBOARD_screen_info.current_w
        LEADERBOARD_monitor_height = LEADERBOARD_screen_info.current_h

        # Screen dimensions
        LEADERBOARD_WIDTH, LEADERBOARD_HEIGHT = (config['window_settings']['WIDTH_OFFSET'] - config['window_settings']['RIGHT_X_PADDING'] - config['window_settings']['BETWEEN_PADDING']), (LEADERBOARD_monitor_height - config['window_settings']['HEIGHT_OFFSET']) 
        LEADERBOARD_START_OFFSET = config['leaderboard_settings']['LEADERBOARD_START_OFFSET']
        LEADERBOARD_LINE_HEIGHT = config['leaderboard_settings']['LEADERBOARD_LINE_HEIGHT']

        # Calculate position next to the right edge
        LEADERBOARD_start_x = LEADERBOARD_monitor_width - LEADERBOARD_WIDTH - config['window_settings']['RIGHT_X_PADDING']  # Position at the right edge
        LEADERBOARD_start_y = (LEADERBOARD_monitor_height // 2) - (LEADERBOARD_HEIGHT // 2)  # Center vertically

        os.environ['SDL_VIDEO_WINDOW_POS'] = f'{LEADERBOARD_start_x},{LEADERBOARD_start_y}'
        
        flags =  DOUBLEBUF | NOFRAME
        LEADERBOARD_screen = pygame.display.set_mode((LEADERBOARD_WIDTH, LEADERBOARD_HEIGHT), flags)
        pygame.display.set_caption('Leaderboard')

        
        # Font settings
        LEADERBOARD_font_size = config['leaderboard_settings']['LEADERBOARD_FONT_SIZE']
        font_regular = pygame.font.Font(None, LEADERBOARD_font_size)
        font_large = pygame.font.Font(None, LEADERBOARD_font_size + 10)


        # Max displayable players
        LEADERBOARD_LAST_WIN_AREA = config['leaderboard_settings']['LEADERBOARD_LAST_WIN_AREA']
        LEADERBOARD_max_player_display = int((LEADERBOARD_HEIGHT - LEADERBOARD_START_OFFSET - LEADERBOARD_LAST_WIN_AREA) / LEADERBOARD_LINE_HEIGHT)
        # print(f"{LEADERBOARD_max_player_display} players displayable")


        # Get the window handle from pygame's window manager info.
        wm_info = pygame.display.get_wm_info()
        hwnd = wm_info.get('window')  # This is available on Windows

        
        last_winner = None
        prev_data = None

        running = True
        last_load_time = time.time() - 1
        clock = pygame.time.Clock()

        rendering_check_period = 10
        rendering_check_point = 0
        rendering_enabled = True
        
        try:
                while running:
                        # Event handling
                        for event in pygame.event.get():
                            if event.type == QUIT:
                                running = False

                            # Detect when the window is hidden or minimized
                            if event.type == pygame.WINDOWHIDDEN:  # Correct event name!
                                rendering_enabled = False
                            elif event.type == pygame.WINDOWSHOWN:
                                rendering_enabled = True
        


                        # Check if the window is focused
                        #rendering_check_point += 1
                        #if (rendering_check_point % rendering_check_period == 0) :
                        #    if not pygame.display.get_active() or not is_window_on_current_desktop(hwnd):
                        #        rendering_enabled = False
                        #    else:
                        #        rendering_enabled = True

                
                        # Load data from a JSON file every second
                        if time.time() - last_load_time > 1:  # Adjust the interval as needed
                                try:
                                        try:
                                            with open('saves/saves.json', 'r', encoding='utf-8') as f:
                                                data = json.load(f)
                                        except (FileNotFoundError, json.JSONDecodeError) as e:
                                                print(f"Error loading JSON: {e}")
                                                data = []

                                        if not prev_data is None:
                                                for player in data:
                                                        for old_player in prev_data:
                                                                if (old_player['player_name'] == player['player_name']):
                                                                        if not (old_player['win_count'] == player['win_count']):
                                                                                last_winner = player['player_name']
                                                                                break
                                                        
                                    
        
                                        prev_data = data
                                except FileNotFoundError:
                                        print("File not found. Please ensure the JSON file exists.")
                                        data = []  # Fallback to an empty list if the file is missing
        
                                # Sort data and take the top 6 players
                                LEADERBOARD_sorted_data = sorted(data, key=lambda x: x['win_count'], reverse=True)[:LEADERBOARD_max_player_display]

                                last_load_time = time.time()

                                if (rendering_enabled):
                        
                                        LEADERBOARD_screen.fill((255, 255, 255))  # Clear screen with white background
                                        y_offset = LEADERBOARD_START_OFFSET
                                        player_rank = 1
                                        for player in LEADERBOARD_sorted_data:
                                                text = f"{player_rank} | {player['player_name']}: {player['win_count']}"
                                                LEADERBOARD_text_surface = font_regular.render(text, True, (0, 0, 0))  # Black text
                                                LEADERBOARD_screen.blit(LEADERBOARD_text_surface, (10, y_offset))
                                                y_offset += LEADERBOARD_LINE_HEIGHT  # Move down for the next player
                                                player_rank += 1

                                        if not last_winner is None:
                                                text = f"Last Winner:"
                                                LEADERBOARD_text_surface = font_large.render(text, True, (0, 0, 0))  # Black text
                                                LEADERBOARD_screen.blit(LEADERBOARD_text_surface, (10, LEADERBOARD_HEIGHT - 90))

                                                text = f"{last_winner}!"
                                                LEADERBOARD_text_surface = font_large.render(text, True, (0, 0, 0))  # Black text
                                                LEADERBOARD_screen.blit(LEADERBOARD_text_surface, (10, LEADERBOARD_HEIGHT - 90 + LEADERBOARD_LINE_HEIGHT))


                                
                        
                                        pygame.display.flip()
                        clock.tick(3)
                        
                pygame.quit()
        except Exception as e:
                print(f"Unexpected error: {e}")
                with open("leaderboard_error_log.txt", "a") as log_file:
                        log_file.write(f"{time.ctime()}: {str(e)}\n")

print("Ladies and gentleman, this system is for keeping track of the leaderboard.")
run_leaderboard()
