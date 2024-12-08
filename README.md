# Wallpaper-Royale
Have you ever wanted to have a list of wallpapers that your wallpaper goes through but you thought that your wallpapers needed to deserve wallpaper-hood?

Now, with Wallpaper Royale, you can have your wallpapers battle each other in order to deserve the state of wallpaper-hood.


The required dependencies can be installed by executing 
pip install -r requirements.txt
in the folder directory that the program is located in.

Run the main.py file for the main game, the leaderboard.py for the leaderboard, and notification.py for the notifications.
The launcher.bat file just runs main.py and leaderboard.py, nothing less, nothing more.

Add the images you want to use into the images folder, and add the win sound effects you want to use into the win_sound_effects folder. While the win sound effects are enabled by default, they can be disabled through the config file, just replace the "true" with "false" under the notification settings.

You can edit most game settings from the config.json file. I don't remember what most of them do, so good luck with that. You can probably guess from the setting name.

PS, if you get an error caused by JSON, make sure to check if the saves.json file is empty. If it is empty, just put "[]" (without the quotes) into the file and save.
