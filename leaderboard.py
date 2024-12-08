import pygame
from pygame.locals import *
import math
import json
import os
import time


def run_leaderboard():
        
        with open("config.json") as json_config_file:
            config = json.load(json_config_file)
            json_config_file.close()
        


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


        # Max displayable players
        LEADERBOARD_LAST_WIN_AREA = config['leaderboard_settings']['LEADERBOARD_LAST_WIN_AREA']
        LEADERBOARD_max_player_display = int((LEADERBOARD_HEIGHT - LEADERBOARD_START_OFFSET - LEADERBOARD_LAST_WIN_AREA) / LEADERBOARD_LINE_HEIGHT)
        # print(f"{LEADERBOARD_max_player_display} players displayable")
        last_winner = None
        prev_data = None

        running = True
        last_load_time = time.time() - 1
        
        while running:
                # Event handling
                for event in pygame.event.get():
                    if event.type == QUIT:
                        running = False
                
                # Load data from a JSON file every second
                if time.time() - last_load_time > 1:  # Adjust the interval as needed
                    try:
                        with open('saves/saves.json', 'r', encoding='utf-8') as f:
                            data = json.load(f)

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

                if 'LEADERBOARD_sorted_data' in locals():
                        
                        LEADERBOARD_screen.fill((255, 255, 255))  # Clear screen with white background
                        y_offset = LEADERBOARD_START_OFFSET
                        player_rank = 1
                        LEADERBOARD_font = pygame.font.Font(None, LEADERBOARD_font_size)
                        for player in LEADERBOARD_sorted_data:
                                text = f"{player_rank} | {player['player_name']}: {player['win_count']}"
                                LEADERBOARD_text_surface = LEADERBOARD_font.render(text, True, (0, 0, 0))  # Black text
                                LEADERBOARD_screen.blit(LEADERBOARD_text_surface, (10, y_offset))
                                y_offset += LEADERBOARD_LINE_HEIGHT  # Move down for the next player
                                player_rank += 1

                        if not last_winner is None:
                                LEADERBOARD_font = pygame.font.Font(None, LEADERBOARD_font_size + 10)
                                text = f"Last Winner:"
                                LEADERBOARD_text_surface = LEADERBOARD_font.render(text, True, (0, 0, 0))  # Black text
                                LEADERBOARD_screen.blit(LEADERBOARD_text_surface, (10, LEADERBOARD_HEIGHT - LEADERBOARD_LAST_WIN_AREA))

                                text = f"{last_winner}!"
                                LEADERBOARD_text_surface = LEADERBOARD_font.render(text, True, (0, 0, 0))  # Black text
                                LEADERBOARD_screen.blit(LEADERBOARD_text_surface, (10, LEADERBOARD_HEIGHT - LEADERBOARD_LAST_WIN_AREA + LEADERBOARD_LINE_HEIGHT))


                                
                        
                        pygame.display.flip()
                pygame.time.delay(100)  # Add a small delay to reduce CPU usage
                
        pygame.quit()


print("Ladies and gentleman, this script manages the leaderboard.")
run_leaderboard()
