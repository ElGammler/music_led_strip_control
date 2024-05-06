#!/usr/bin/env bash

# Setup script for MLSC
# https://github.com/TobKra96/music_led_strip_control


INST_DIR="/share" # Installation location
PROJ_DIR="music_led_strip_control" # Project location
PROJ_NAME="MLSC" # Project abbreviation
VENV_NAME="venv" # Virtualenv name
ASOUND_DIR="/etc/asound.conf" # Asound config location
ALSA_DIR="/usr/share/alsa/alsa.conf" # Alsa config location
SERVICE_DIR="/etc/systemd/system/mlsc.service" # MLSC systemd service location
SERVICE_NAME="mlsc.service" # MLSC systemd service name
GIT_BRANCH="master"


# Colors
CDEF="\033[0m"          # Default color
CCIN="\033[0;36m"       # Info color
CGSC="\033[0;32m"       # Success color
CRER="\033[0;31m"       # Error color
CWAR="\033[0;33m"       # Warning color
b_CDEF="\033[1;37m"     # Bold default color
b_CCIN="\033[1;36m"     # Bold info color
b_CGSC="\033[1;32m"     # Bold success color
b_CRER="\033[1;31m"     # Bold error color
b_CWAR="\033[1;33m"     # Bold warning color


# Print message with flag type to change message color.
function prompt {
    arg1=$1
    all=$@
    shift
    case $arg1 in
        "-s"|"--success")
        echo -e "${b_CGSC}${@}${CDEF}";;  # Print success message
        "-e"|"--error")
        echo -e "${b_CRER}${@}${CDEF}";;  # Print error message
        "-w"|"--warning")
        echo -e "${b_CWAR}${@}${CDEF}";;  # Print warning message
        "-i"|"--info")
        echo -e "${b_CCIN}${@}${CDEF}";;  # Print info message
        *)
        echo -e "$all";;                  # Print generic message
    esac
}


# Confirm action before proceeding.
function confirm {
    while true; do
        read -rp "$(prompt -w "$*? [y/N] ")" yn </dev/tty
        case $yn in
            [Yy]*) prompt -s "Proceeding..."; return 0;;
            [Nn]*) prompt -i "Skipped."; return 1;;
            [Qq]*) prompt -e "Setup exited."; exit 0;;
            '') prompt -i "Skipped."; return 1;;
        esac
    done
}


# Output help information.
function usage {
    if [ -n "$1" ]; then
        echo -e "${CRER}$1${CDEF}\n";
    fi
    prompt -i "Usage:"
    prompt -i "  sudo bash $0 [options]"
    echo ""
    prompt -i "OPTIONS"
    prompt -i "  -b, --branch        git branch to use (master, dev_2.3)"
    prompt -i "  -h, --help          show this list of command-line options"
    echo ""
    prompt -i "Example:"
    prompt -i "  sudo bash $0 --branch dev_2.3"
    if [ -n "$1" ]; then
        exit 1
    fi
    exit 0
}

# Parse arguments.
while [[ "$#" > 0 ]]; do case $1 in
    -b|--branch) GIT_BRANCH="$2"; shift;shift;;
    -h|--help) usage;shift;;
    *) usage "Unknown argument passed: $1";shift;shift;;
esac; done


case $GIT_BRANCH in
    master|dev_2.3);;
    *) GIT_BRANCH="master";;
esac


echo
prompt -s "\t          *********************"
prompt -s "\t          *  Installing $PROJ_NAME  *"
prompt -s "\t          *********************"
echo

# Update packages:
prompt -i "\n[1/4] Updating and installing required packages..."
sudo apt-get update -qq && sudo apt-get upgrade -qqy

# Install required packages:
# git: For cloning the MLSC repository.
# libatlas-base-dev: Required for Numpy module.
# portaudio19-dev: Audio drivers.
sudo apt-get -y --no-install-recommends install git libatlas-base-dev portaudio19-dev python3 python3-dev python3-pip python3-venv

prompt -s "\nPackages updated and installed."

# Install MLSC:
prompt -i "\n[2/4] Installing $PROJ_NAME..."
if [[ ! -d $INST_DIR ]]; then
	sudo mkdir $INST_DIR
fi
cd $INST_DIR

# Create virtual environment in the installation directory.
if [[ ! -d $VENV_NAME ]]; then
	sudo python3 -m venv $VENV_NAME
    prompt -s "\nVirtual environment ${VENV_NAME} created."
fi

# Upgrade Pip to the latest version.
sudo ${VENV_NAME}/bin/pip3 install --no-cache-dir --no-input --upgrade pip


if [[ -d $PROJ_DIR ]]; then
    confirm "${PROJ_NAME} is already installed. Do you want to reinstall it"
    if [[ $? -eq 0 ]]; then
        if [[ -f $SERVICE_DIR ]]; then
            systemctl_status=$(sudo systemctl is-active $SERVICE_NAME)
            if [[ $systemctl_status == 'active' ]]; then
                sudo systemctl stop ${SERVICE_NAME}
                prompt -s "\nAutostart for ${PROJ_NAME} stopped."
            fi
        fi
        if [[ -d "${PROJ_DIR}_bak" ]]; then
            sudo rm -r "${PROJ_DIR}_bak"
            prompt -s "\nPrevious ${PROJ_NAME} backup deleted."
        fi
	    sudo mv -T $PROJ_DIR "${PROJ_DIR}_bak"
        prompt -s "\nNew backup of ${PROJ_NAME} created."
        sudo git clone --depth 1 --branch $GIT_BRANCH https://github.com/TobKra96/music_led_strip_control.git
        prompt -s "\nConfig is stored in .mlsc, in the same directory as the MLSC installation."
        if [[ -f $SERVICE_DIR ]]; then
            if [[ $systemctl_status == 'active' ]]; then
                sudo systemctl start ${SERVICE_NAME}
                prompt -s "\nAutostart for ${PROJ_NAME} restarted."
            fi
        fi
    fi
else
    sudo git clone --depth 1 --branch $GIT_BRANCH https://github.com/TobKra96/music_led_strip_control.git
fi

# Install/update modules from requirements.txt.
sudo ${VENV_NAME}/bin/pip3 install --no-cache-dir --no-input --upgrade -r ${PROJ_DIR}/requirements.txt


# Setup microphone:
prompt -i "\n[3/4] Configuring microphone settings..."
if [[ ! -f $ASOUND_DIR ]]; then
    sudo touch $ASOUND_DIR
    prompt -s "\n$ASOUND_DIR created."
else
    sudo mv $ASOUND_DIR "$ASOUND_DIR.bak"
    prompt -s "\nBackup of existing $ASOUND_DIR created."
fi
sudo echo -e 'pcm.!default {\n    type hw\n    card 1\n}\nctl.!default {\n    type hw\n    card 1\n}' > $ASOUND_DIR
prompt -s "\nNew configuration for $ASOUND_DIR saved."

if [[ ! -f $ALSA_DIR ]]; then
    sudo touch $ALSA_DIR
    prompt -s "\n$ALSA_DIR created."
else
    sudo cp $ALSA_DIR "$ALSA_DIR.bak"
    prompt -s "\nBackup of existing $ALSA_DIR created."
fi
sed -i -e '/defaults.ctl.card 0/c\defaults.ctl.card 1' \
    -i -e '/defaults.pcm.card 0/c\defaults.pcm.card 1' \
    -e '/pcm.front cards.pcm.front/ s/^#*/#/' \
    -e '/pcm.rear cards.pcm.rear/ s/^#*/#/' \
    -e '/pcm.center_lfe cards.pcm.center_lfe/ s/^#*/#/' \
    -e '/pcm.side cards.pcm.side/ s/^#*/#/' \
    -e '/pcm.surround21 cards.pcm.surround21/ s/^#*/#/' \
    -e '/pcm.surround40 cards.pcm.surround40/ s/^#*/#/' \
    -e '/pcm.surround41 cards.pcm.surround41/ s/^#*/#/' \
    -e '/pcm.surround50 cards.pcm.surround50/ s/^#*/#/' \
    -e '/pcm.surround51 cards.pcm.surround51/ s/^#*/#/' \
    -e '/pcm.surround71 cards.pcm.surround71/ s/^#*/#/' \
    -e '/pcm.iec958 cards.pcm.iec958/ s/^#*/#/' \
    -e '/pcm.spdif iec958/ s/^#*/#/' \
    -e '/pcm.hdmi cards.pcm.hdmi/ s/^#*/#/' \
    -e '/pcm.dmix cards.pcm.dmix/ s/^#*/#/' \
    -e '/pcm.dsnoop cards.pcm.dsnoop/ s/^#*/#/' \
    -e '/pcm.modem cards.pcm.modem/ s/^#*/#/' \
    -e '/pcm.phoneline cards.pcm.phoneline/ s/^#*/#/' $ALSA_DIR

prompt -s "\nNew configuration for $ALSA_DIR saved."


# Create systemd service:
prompt -i "\n[4/4] Creating autostart service for ${PROJ_NAME}..."
if [[ ! -f $SERVICE_DIR ]]; then
    sudo touch ${SERVICE_DIR}
echo "[Unit]
Description=Music LED Strip Control
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=${INST_DIR}/music_led_strip_control/server
ExecStart=${INST_DIR}/${VENV_NAME}/bin/python3 main.py
Restart=on-abnormal
RestartSec=10
KillMode=control-group

[Install]
WantedBy=multi-user.target" | sudo tee -a ${SERVICE_DIR} > /dev/null
    prompt -s "\nAutostart script for ${PROJ_NAME} created in '${SERVICE_DIR}'."
else
    prompt -s "\nAutostart script for ${PROJ_NAME} already exists in '${SERVICE_DIR}'."
fi


# Enable systemd service:
if [[ -f $SERVICE_DIR ]]; then
    systemctl_status=$(sudo systemctl is-enabled $SERVICE_NAME)
    if [[ $systemctl_status == 'disabled' ]]; then
        confirm "Do you want to enable autostart for ${PROJ_NAME}"
        if [[ $? -eq 0 ]]; then
            sudo systemctl enable ${SERVICE_NAME}
            prompt -s "\nAutostart for ${PROJ_NAME} enabled."
        fi
    fi
fi


echo
prompt -s "\t          ********************************************"
prompt -s "\t          *       ${PROJ_NAME} installation completed!       *"
prompt -s "\t          * Please reboot your system (sudo reboot). *"
prompt -s "\t          ********************************************"

exit 0
