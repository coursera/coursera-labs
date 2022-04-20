import json
import os.path

settings_file_path = "/home/coder/.local/share/code-server/User/settings.json"
launch_button_settings_path = "/home/coder/coursera/launchButtonSettings.json"

# If launchButtonSettings.json file exists, add the action button settings
if os.path.exists(launch_button_settings_path):
    with open(settings_file_path) as settings_file:
        with open(launch_button_settings_path) as launch_button_settings_file:
            settings = json.load(settings_file)
            launch_button_settings = json.load(launch_button_settings_file)
        settings["launchButtons"] = launch_button_settings["launchButtons"]
        with open(settings_file_path, 'w') as new_settings_file:
            json.dump(settings, new_settings_file)
