import math
import json
import os
import time
from win10toast import ToastNotifier
import pygame



toaster = ToastNotifier()
pygame.mixer.init()

def run_notification():
        
        with open("config.json") as json_config_file:
            config = json.load(json_config_file)
            json_config_file.close()

        WIN_SOUND_EFFECT_ENABLED = config['notification_settings']['WIN_SOUND_EFFECT_ENABLED']

        print("Ladies and gentleman, this script manages the notification system.")
        last_winner = None
        prev_data = None

        running = True
        last_load_time = time.time() - 1
        
        while running:
                
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
                                                                toaster.show_toast("",
                                                                        f"{last_winner} wins!",
                                                                        icon_path=None,
                                                                        duration=5,
                                                                        threaded=True)

                                                                if WIN_SOUND_EFFECT_ENABLED and not player['win_sound_effect_path'] == '':
                                                                        sound_effect_path = os.path.dirname(os.path.abspath(__file__)) + '/win_sound_effects/' + player['win_sound_effect_path']
                                                                        pygame.mixer.music.load(sound_effect_path)

                                                                        # Play the sound
                                                                        pygame.mixer.music.play()

                                                                # Wait for threaded notification to finish
                                                                while toaster.notification_active(): time.sleep(0.1)
                                                                break
                                                        
                                    

                            prev_data = data
                    except FileNotFoundError:
                        print("File not found. Please ensure the JSON file exists.")
                        data = []  # Fallback to an empty list if the file is missing

                    last_load_time = time.time()




run_notification()
