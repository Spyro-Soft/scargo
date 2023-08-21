# Overview

<Add project overview here>

# Set docker environment

`scargo update`

# Run docker environment

`scargo docker run`

# Basic work with project

scargo clean -> scargo build -> scargo check -> scargo test

- `build`: Compile project.
- `clean`: Clean build directory.
- `check`: Check sources.
- `fix`: Fix problems reported by chosen checkers in source directory.
- `doc`: Generate project documentation.
- `docker`: Manage docker environment for you project.
- `publish`: Publish lib or binary to conan artifactory.
- `update`: Read scargo.toml and generate CMakeLists.txt.
- `gen`: Generate certificate and other artifacts for chosen targets
- `flash`: flash microcontroller board

First position yourself into working directory.

IMPORTANT! if you make any changes of configuration in scargo.toml file then `scargo update` command need to be trigger to apply those changes into the project.

## Publish lib or bin using conan

Please set the `CONAN_LOGIN_USERNAME=""` and `CONAN_PASSWORD=""` parameter in .devcontainer/.env file with you conan credential.
and run:

`scargo docker build`
or
`cd .devcontainer && docker-compose build`

to update the environment with your credential.

# Project dependencies

## Working with docker (recommended)

- python3
- pip
- scargo
- docker
- docker-compose

# ESP32 configure
On the beginning of project is strongly recommended to configure the project using `idf.py menuconfig`
In console please run `idf.py menuconfig` and configure at least fallowing options:
- Bootloader config -> Bootloader Optimization Level ...  (O2 is recommended)
- Serial Flasher Config -> Flash Size ... (e.g. For wroom is 4MB)
- Partition Table -> Partition Table ... -> Custom Partition Table CSV

## Simulation with qemu
To use qemu single image with all partition is needed. You can generated with following command:

`scargo gen -b`

or it can be generated base on data from build/flasher_args.json but spiffs partition need to be added manually to the file

`esptool.py --chip esp32 merge_bin --fill-flash-size 4MB -o build/flash_image.bin @flash_args`

Then run qemu simulation:

`qemu-system-xtensa -nographic -machine esp32 -drive file=build/flash_image.bin,if=mtd,format=raw`

Stop qemu using `pkill qemu` command in the terminal

## Working directly with IDF

(0) idf.py fullclean

1. idf.py all
2. idf.py flash
3. idf.py monitor

idf.py clean
idf.py build
or
idf.py app
idf.py app-flash

idf.py menuconfig

## Create fs and manage image

Create image:
`scargo gen --fs`
or
`$IDF_PATH/components/spiffs/spiffsgen.py 24576 main/fs build/spiffs.bin`

Write to partition 'spiffs' the contents of a file named 'spiffs.bin':
`scargo flash --fs`
or
`parttool.py write_partition --partition-name=spiffs --input "build/spiffs.bin"`

Erase partition with name 'storage':
`parttool.py erase_partition --partition-name=spiffs`

Read partition with type 'data' and subtype 'spiffs' and save to file 'spiffs.bin':
`parttool.py read_partition --partition-type=data --partition-subtype=spiffs --output "build/spiff.bin"`

Print the size of default boot partition:
`parttool.py get_partition_info --partition-boot-default --info size`

## Potential issues

idf.py set-target esp32c3 - set up esp32 uC target example with esp32c3


## Debug

### debug in console

idf.py flash monitor openocd gdbgui

### debug in vsc

- run `idf.py openocd` or `openocd -c \"set ESP_RTOS none\" -f board/esp32-wrover-kit-3.3v.cfg`
- run debug in vscode

