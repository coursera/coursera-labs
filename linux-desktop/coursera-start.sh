# Install font
mkdir -p /home/coder/.local/share/fonts/googlefonts
unzip -d /home/coder/.local/share/fonts/googlefonts/ /tmp/Source_Sans_Pro.zip &> /dev/null
fc-cache -fv &> /dev/null

# For persistence
mkdir -p /home/coder/coursera/.coursera-dotfiles/

# Persist IntelliJ data collection setting
mkdir -p /home/coder/.local/share/JetBrains/consentOptions
touch /home/coder/coursera/.coursera-dotfiles/accepted
ln -s /home/coder/coursera/.coursera-dotfiles/accepted /home/coder/.local/share/JetBrains/consentOptions/

# Persist IntelliJ user agreement setting
mkdir -p /home/coder/.java/
mkdir -p /home/coder/coursera/.coursera-dotfiles/.userPrefs/jetbrains/'_!(!!cg"p!(}!}@"j!(k!|w"w!'\''8!b!"p!'\'':!e@=='
ln -s /home/coder/coursera/.coursera-dotfiles/.userPrefs/ /home/coder/.java/.userPrefs

# Persist user config (recent projects, trust project, etc.)
mkdir -p /home/coder/coursera/.coursera-dotfiles/.config/JetBrains
ln -s /home/coder/coursera/.coursera-dotfiles/.config/JetBrains /home/coder/.config/JetBrains

# Persist VSCode files
mkdir -p /home/coder/coursera/vscode/projects
ln -s /home/coder/coursera/vscode/projects /home/coder/vscode/projects
