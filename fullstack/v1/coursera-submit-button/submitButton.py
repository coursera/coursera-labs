import json
import os.path

settings_file_path = "/home/coder/.local/share/code-server/User/settings.json"
submit_button_path = "/home/coder/coursera/actionButtonSettings.json"

# If actionButtonSettings.json file exists, add the action button settings
if os.path.exists(submit_button_path):
    with open(settings_file_path) as settings_file:
        with open(submit_button_path) as action_button_settings_file:
            settings = json.load(settings_file)
            action_button_settings = json.load(action_button_settings_file)
        settings["actionButtons"] = action_button_settings["actionButtons"]
        with open(settings_file_path, 'w') as new_settings_file:
            json.dump(settings, new_settings_file)
