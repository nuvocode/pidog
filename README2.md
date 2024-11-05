country=US  # Change this to your country code
ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
update_config=1

network={
    ssid="HARRY"
    psk="1231231237"
    key_mgmt=WPA-PSK
    priority=1
}

# update_config
sudo raspi-config

# SSH
ssh pasha@192.168.0.80

# PiDog Development Setup

## Initial Setup
- Clone repo on Windows/VS Code:  
  ```bash
  git clone https://github.com/nuvocode/pidog.git

## Pull Pi updates
cd ~/pidog
git pull

# Reset utility
cd ~/pidog/utils
sudo python3 reset_pidog.py

