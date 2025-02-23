#!/usr/bin/env python

#
# Lenovo Legion 5 Pro 2021 keyboard light controller
# Shara, 2021, MIT
#
# Add udev rule as "/etc/udev/rules.d/10-kblight.rules" if you want control light as user
# SUBSYSTEM=="usb", ATTR{idVendor}=="048d", ATTR{idProduct}=="c975", MODE="0666"
#
# Payload description
#
# HEADER ........... cc
# HEADER ........... 16
# EFFECT ........... 01 - static / 03 - breath / 04 - wave / 06 - hue
# SPEED ............ 01 / 02 / 03 / 04
# BRIGHTNESS ....... 01 / 02
# RED SECTION 1 .... 00-ff
# GREEN SECTION 1 .. 00-ff
# BLUE SECTION 1 ... 00-ff
# RED SECTION 2 .... 00-ff
# GREEN SECTION 2 .. 00-ff
# BLUE SECTION 2 ... 00-ff
# RED SECTION 3 .... 00-ff
# GREEN SECTION 3 .. 00-ff
# BLUE SECTION 3 ... 00-ff
# RED SECTION 4 .... 00-ff
# GREEN SECTION 4 .. 00-ff
# BLUE SECTION 4 ... 00-ff
# UNUSED ........... 00
# WAVE MODE RTL .... 00 / 01
# WAVE MODE LTR .... 00 / 01
# UNUSED ........... 00
# UNUSED ........... 00
# UNUSED ........... 00
# UNUSED ........... 00
# UNUSED ........... 00
# UNUSED ........... 00
# UNUSED ........... 00
# UNUSED ........... 00
# UNUSED ........... 00
# UNUSED ........... 00
# UNUSED ........... 00
# UNUSED ........... 00
# UNUSED ........... 00
#

import argparse
import functools
import usb.core

# Knoen keyboard light devices.
# Integrated Technology Express, Inc. ITE Device(8295)
_KNOWN_DEVICES = [
    (0x048D, 0xC985, 0xFF89, 0x00CC),  # 2023
    (0x048D, 0xC984, 0xFF89, 0x00CC),  # 2023
    (0x048D, 0xC983, 0xFF89, 0x00CC),  # 2023 LOQ
    (0x048D, 0xC975, 0xFF89, 0x00CC),  # 2022 (16ARH7H)
    (0x048D, 0xC973, 0xFF89, 0x00CC),  # 2022 Ideapad
    (0x048D, 0xC965, 0xFF89, 0x00CC),  # 2021
    (0x048D, 0xC963, 0xFF89, 0x00CC),  # 2021 Ideapad
    (0x048D, 0xC955, 0xFF89, 0x00CC),  # 2020
]


@functools.lru_cache
def _get_device() -> usb.core.Device:
    for vendor, product, _, _ in _KNOWN_DEVICES:
        device = usb.core.find(idVendor=vendor, idProduct=product)
        if device is not None:
            assert isinstance(device, usb.core.Device)
            print(f"Found device: {vendor:04x}:{product:04x}")
            return device
    raise RuntimeError("No valid devices found.")


class LedController:
    EFFECT = {"static": 1, "breath": 3, "wave": 4, "hue": 6}

    def __init__(self):
        device = _get_device()

        if device is None:
            raise ValueError("Light device not found")

        # Prevent usb.core.USBError: [Errno 16] Resource busy
        if device.is_kernel_driver_active(0):
            device.detach_kernel_driver(0)

        self.device = device

    # Build light device control string
    def build_control_string(
        self,
        effect,
        hex_colors: list[str] | None,
        speed=1,
        brightness=1,
        wave_direction=None,
    ):
        data = [204, 22]

        if effect == "off":
            data.append(self.EFFECT["static"])
            data += [0] * 30
            return data

        data.append(self.EFFECT[effect])
        data.append(speed)
        data.append(brightness)

        data += [0] * 12
        if effect in ["static", "breath"] and hex_colors is not None:
            assert isinstance(hex_colors, list)
            for section_index in range(4):
                color = hex_colors[section_index % len(hex_colors)]
                # HEX model.
                section_rgb = [
                    int(color[i : i + 2], 16) for i in range(0, len(color), 2)
                ]
                data_index = 5 + section_index * 3
                data[data_index : data_index + 3] = section_rgb

        # Unused
        data += [0]

        # Wave direction
        if wave_direction == "rtl":
            data += [1, 0]
        elif wave_direction == "ltr":
            data += [0, 1]
        else:
            data += [0, 0]

        # Unused
        data += [0] * 13

        print("Payload: " + " ".join(f"{x:02X}" for x in data))
        return data

    # Send command to device
    def send_control_string(self, data):
        self.device.ctrl_transfer(
            bmRequestType=0x21,
            bRequest=0x9,
            wValue=0x03CC,
            wIndex=0x00,
            data_or_wLength=data,
        )


def main():
    # Parse arguments
    argparser = argparse.ArgumentParser(
        description="Lenovo Legion 5 Pro 2021 keyboard light controller"
    )

    effect_subparsers = argparser.add_subparsers(help="Light effect", dest="effect")

    # Global options
    global_parser = argparse.ArgumentParser(add_help=False)
    global_parser.add_argument(
        "--brightness",
        type=int,
        choices=range(1, 3),
        default=1,
        help="Light brightness",
    )

    # Options for custom color settings only
    custom_parser = argparse.ArgumentParser(add_help=False)
    custom_parser.add_argument(
        "colors",
        nargs="+",
        help="Hexadecimal colors, upto 4 for each of the 4 sections.",
    )

    # Options for wave effect
    wave_parser = argparse.ArgumentParser(add_help=False)
    wave_parser.add_argument(
        "direction",
        type=str,
        choices=["ltr", "rtl"],
        help="Direction of wave",
    )

    # Options for animated effects
    animated_parser = argparse.ArgumentParser(add_help=False)
    animated_parser.add_argument(
        "--speed", type=int, choices=range(1, 5), default=1, help="Animation speed"
    )

    # Effects
    effect_subparsers.add_parser(
        "static", help="Static color", parents=[global_parser, custom_parser]
    )

    effect_subparsers.add_parser(
        "breath",
        help="Fade light in and out",
        parents=[global_parser, custom_parser, animated_parser],
    )

    effect_subparsers.add_parser(
        "hue",
        help="Transition across hue circle",
        parents=[global_parser, animated_parser],
    )

    effect_subparsers.add_parser(
        "wave",
        help="Rainbow wawe",
        parents=[global_parser, animated_parser, wave_parser],
    )

    effect_subparsers.add_parser("off", help="Turn light off")

    args = argparser.parse_args()

    # Use controller
    controller = LedController()
    data = controller.build_control_string(
        effect=args.effect,
        hex_colors=getattr(args, "colors", None),
        speed=getattr(args, "speed", 1),
        brightness=getattr(args, "brightness", 1),
        wave_direction=getattr(args, "direction", None),
    )
    controller.send_control_string(data)


if __name__ == "__main__":
    main()
