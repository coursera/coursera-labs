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

# Install vscode extensions
code --install-extension formulahendry.code-runner &
# Set up Java Extension
code --install-extension redhat.java &
code --install-extension vscjava.vscode-java-debug &
# Lock in this version to maintain documented testing UI
code --install-extension vscjava.vscode-java-test &
code --install-extension vscjava.vscode-maven &
# Set up Scala Extension
code --install-extension scala-lang.scala &
code --install-extension scalameta.metals &
# Set up Go Extension
code --install-extension golang.go &
# Set up Python Extension
code --install-extension ms-python.python &
# Set up HTML/CSS Extension
code --install-extension ecmel.vscode-html-css &
# Set up Ruby Extension
code --install-extension rebornix.Ruby &
# Set up Rust Extension
code --install-extension rust-lang.rust &
# Set up JavaScript/Node Extensions
code --install-extension xabikos.JavaScriptSnippets &
code --install-extension ms-vscode.node-debug2 &
code --install-extension esbenp.prettier-vscode &
# Set up Vue.js Tooling
code --install-extension octref.vetur &
# Set up PHP Extension
code --install-extension bmewburn.vscode-intelephense-client &
# Set up Chrome Extension
code --install-extension ritwickdey.liveServer &
# Set up React Extensions
code --install-extension dsznajder.es7-react-js-snippets &
code --install-extension dbaeumer.vscode-eslint &
