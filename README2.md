country=US  # Change this to your country code
ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
update_config=1

network={
    ssid="HARRY"
    psk="1231231237"
    key_mgmt=WPA-PSK
    priority=1
}