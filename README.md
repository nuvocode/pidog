# Connect via ssh
ssh pasha@pashaPi.local

Or 

ssh pasha@192.168.0.80

# Pidog

Pidog Python library for Raspberry Pi.

Quick Links:

- [Pidog](#pidog)
  - [Docs](#docs)
  - [Installation](#installation)
  - [About SunFounder](#about-sunfounder)
  - [Contact us](#contact-us)
  - [Credit](#credit)

----------------------------------------------

## Docs

- <https://docs.sunfounder.com/projects/pidog/en/latest/>

----------------------------------------------

## Installation

- <https://docs.sunfounder.com/projects/pidog/en/latest/python/python_start/install_all_modules.html>

### install tool

```bash
sudo apt install git python3-pip python3-setuptools python3-smbus
```

### robot-hat library

```bash
cd ~/
git clone -b v2.0 https://github.com/sunfounder/robot-hat.git
cd robot-hat
sudo python3 setup.py install

```

### vilib library

```bash
cd ~/
git clone -b picamera2 https://github.com/sunfounder/vilib.git
cd vilib
sudo python3 install.py
```

### pidog library

```bash
cd ~/
git clone https://github.com/sunfounder/pidog.git
cd pidog
sudo python3 setup.py install
```

### i2samp

```
cd ~/pidog
sudo bash i2samp.sh
```

----------------------------------------------

## About SunFounder

SunFounder is a technology company focused on Raspberry Pi and Arduino open source community development. Committed to the promotion of open source culture, we strives to bring the fun of electronics making to people all around the world and enable everyone to be a maker. Our products include learning kits, development boards, robots, sensor modules and development tools. In addition to high quality products, SunFounder also offers video tutorials to help you make your own project. If you have interest in open source or making something cool, welcome to join us!

----------------------------------------------

## Contact us

website:
    www.sunfounder.com

E-mail:
    service@sunfounder.com, support@sunfounder.com

## Credit

Most sound effect are from [Zapsplat.com](https://www.zapsplat.com)


## Now you can make changes to your local files, commit them and push to your repo:
git add .
git commit -m "your changes description"
git push origin main
# If you need to get updates from the original sunfounder repo:
git fetch upstream
git merge upstream/main