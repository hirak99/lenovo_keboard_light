![Lenovo Laptop RGB Keyboard Light Controller](https://i.imgur.com/FhBMS9W.jpg)

# Lenovo Laptop RGB Keyboard Light Controller

This util allows to drive RGB keyboard light on Lenovo Laptops.

Forked from https://github.com/imShara/l5p-kbl

## Requirements

* pyusb

## Unprivileged usage

Run `lsusb -vt` to find the vendor id e.g. -

```
$ lsusb -vt

/:  Bus 005.Port 001: Dev 001, Class=root_hub, Driver=xhci_hcd/1p, 480M
    ID 1d6b:0002 Linux Foundation 2.0 root hub
    |__ Port 001: Dev 002, If 0, Class=Human Interface Device, Driver=[none], 12M
        ID 048d:c975 Integrated Technology Express, Inc.
    |__ Port 001: Dev 002, If 1, Class=Human Interface Device, Driver=usbhid, 12M
        ID 048d:c975 Integrated Technology Express, Inc.
```

Add udev rule if you want to swith light as unprivileged user
```
# /etc/udev/rules.d/99-kblight.rules
SUBSYSTEM=="usb", ATTR{idVendor}=="048d", ATTR{idProduct}=="c975", MODE="0666"
```

Reload rules
```
sudo udevadm control --reload-rules && sudo udevadm trigger
```

## Usage

### Colors

I'ts possible to set color for 4 sections of keyboard separately like `COLOR COLOR COLOR COLOR`, but you can set single color for whole keyboard with just `COLOR`. Last color will be repeated for other sections.

Colors should be 6-digit base 16 input like `ffffff`

### Light effect

#### statiс
Static color

```
usage: l5p_kbl.py static [-h] [--brightness {1,2}] colors [colors ...]

positional arguments:
  colors              Colors of sections

optional arguments:
  -h, --help          show this help message and exit
  --brightness {1,2}  Light brightness
```

Turn 100% red
```sh
./l5p_kbl.py static ff0000
```

At full brightness, turn 100% red for 1 section, 100% green for 2 section, 100% blue for 3 section an 100% white for 4 section
```sh
./l5p_kbl.py static ff0000 00ff00 0000ff ffffff --brightness 2
```

Dimmed warm orange like wire heater.
```sh
./l5p_kbl.py static 330200
```

#### breath
Fade light in and out
```
usage: l5p_kbl.py breath [-h] [--brightness {1,2}] [--speed {1,2,3,4}] colors [colors ...]

positional arguments:
  colors              Colors of sections

optional arguments:
  -h, --help          show this help message and exit
  --brightness {1,2}  Light brightness
  --speed {1,2,3,4}   Animation speed
```

Fast white blink at full brightness
```sh
./l5p_kbl.py breath ffffff --speed 4 --brightness 2
```

#### hue
Transition across hue circle. You can't set custom colors here.
```
usage: l5p_kbl.py hue [-h] [--brightness {1,2}] [--speed {1,2,3,4}]

optional arguments:
  -h, --help          show this help message and exit
  --brightness {1,2}  Light brightness
  --speed {1,2,3,4}   Animation speed
```

Rotate HUE slowly
```sh
./l5p_kbl.py hue --speed 1
```


#### wave
Rainbow wawe effect. Wow. Cool. Useles.
```
usage: l5p_kbl.py wave [-h] [--brightness {1,2}] [--speed {1,2,3,4}] {ltr,rtl}

positional arguments:
  {ltr,rtl}           Direction of wave

optional arguments:
  -h, --help          show this help message and exit
  --brightness {1,2}  Light brightness
  --speed {1,2,3,4}   Animation speed
```

Wheeee, left to right
```sh
./l5p_kbl.py wave ltr
```

Pew-pew-pew, right to left
```sh
./l5p_kbl.py wave rtl --speed 4
```

#### off
Turn light off. Nuff said.
```
usage: l5p_kbl.py off [-h]

optional arguments:
  -h, --help  show this help message and exit
```


## Recommendations
Set `Super+Space` keystroke to turn light on and turn it off with single `fn+Space` press


## Payload description
Device vendor = 048d, product = c965

```
HEADER ........... cc
HEADER ........... 16
EFFECT ........... 01 - static / 03 - breath / 04 - wave / 06 - hue
SPEED ............ 01 / 02 / 03 / 04
BRIGHTNESS ....... 01 / 02
RED SECTION 1 .... 00-ff
GREEN SECTION 1 .. 00-ff
BLUE SECTION 1 ... 00-ff
RED SECTION 2 .... 00-ff
GREEN SECTION 2 .. 00-ff
BLUE SECTION 2 ... 00-ff
RED SECTION 3 .... 00-ff
GREEN SECTION 3 .. 00-ff
BLUE SECTION 3 ... 00-ff
RED SECTION 4 .... 00-ff
GREEN SECTION 4 .. 00-ff
BLUE SECTION 4 ... 00-ff
UNUSED ........... 00
WAVE MODE RTL .... 00 / 01
WAVE MODE LTR .... 00 / 01
UNUSED ........... 00
UNUSED ........... 00
UNUSED ........... 00
UNUSED ........... 00
UNUSED ........... 00
UNUSED ........... 00
UNUSED ........... 00
UNUSED ........... 00
UNUSED ........... 00
UNUSED ........... 00
UNUSED ........... 00
UNUSED ........... 00
UNUSED ........... 00
```

For another implementation see the `build_payload()` method here -
https://github.com/4JX/L5P-Keyboard-RGB/blob/main/driver/src/lib.rs#L52
