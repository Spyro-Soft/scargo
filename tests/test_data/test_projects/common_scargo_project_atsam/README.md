# Overview

<Add project overview here>

# Getting started

## Development with devcontainer in visual studio code
### Devcontainer
1. Install Visual Studio Code Dev Containers.
2. Install docker engine [https://docs.docker.com/get-docker/](https://docs.docker.com/get-docker/)
3. Development environment is defined as docker image defined inside .devcontainer directory so no additional installations are required (It is also used by CI so you use is what CI use).

### Linux (debian/ubuntu) issues: docker compose is not installed by default
docker-compose is not installed by default with docker engine so below might be required

```bash
#!/bin/bash

sudo apt install docker-compose
```

### Windows 11 issues: Usb is not available in container
If you use windows and would like to have device access. You would be forced to forward them. It can be done via usbip tool (usb over ip). So

1. Put your Docker Desktop into WSL2 mode (Best during installation, in version v4.18 it is default option).
2. Change default Docker desktop WSL image to UbuntuDistribution (default one is not debian based and will NOT work with usbip instructions). Best  way is to switch it from docker desktop GUI
    1. Go to DockerDesktopTrayIcon (right click) -> Setting -> Resources -> WSL Integration
    2. Find option described as *Enable integration with additional distros* And mark ubuntu 22.04 option
3. Change default WSL image to Ubuntu 22.04
    ```powershell
    wsl -l -v                      # check the names
    wsl --set-default Ubuntu-22.04 # set default distribution
    ```
4. Install usbip on windows and inside WSL Ubuntu-22.04
5. Attach device
    ```
    usbipd list                   # print all usb devices
    usbipd wsl attach --busid 4-2	# attach device 4-2 to docker run env
    ```

### Sources
1. [https://learn.microsoft.com/en-us/windows/wsl/connect-usb](https://learn.microsoft.com/en-us/windows/wsl/connect-usb)
2. [https://github.com/dorssel/usbipd-win](https://github.com/dorssel/usbipd-win)
3. [https://devblogs.microsoft.com/commandline/connecting-usb-devices-to-wsl/](https://devblogs.microsoft.com/commandline/connecting-usb-devices-to-wsl/)


## Configuration of conan
Project relies on internal conan package repository. Compilation work only when you configure credentials.
Add to `.devcontainer/.env` variables with conan credentials. (File might not exist as it is ignored by git - it contains local settings of developer machine):

```bash
CONAN_LOGIN_USERNAME="<gitlab_user>"            # Usually three letters
CONAN_PASSWORD="<gitlab_personal_access_token>" # Access token generated in gitlab  gui EditProfile -> Access Tokens
```

Remember that changing .env file **REQUIRE REBUILD OF DEVCONTAINER**.
Variables should be visible inside containers.

```bash
#!/bin/bash
printenv | grep CONAN # In case of correct config this should print your user and password as system variables
```

## Work with project (compilation)

### Scargo flow (local development)
```bash
#!/bin/bash
scargo clean;                 # Clean build directory.
scargo update;                # GENERATE files using toml file as instruction (scargo is code generator). IT IS REQUIRED AFTER CHANGES IN *.toml FILE
scargo build --profile Debug; # Compile project with debug profile
scargo test -v;               # Run tests with verbose output
```

### Scargo full flow (tools and checks)
```bash
#!/bin/bash
scargo clean;                 # Clean build directory.
scargo update;                # GENERATE files using toml file as instruction (scargo is code generator). IT IS REQUIRED AFTER CHANGES IN scargo.toml FILE
scargo test -v;               # Run tests with verbose output
scargo build --profile Debug; # Compile project with debug profile
scargo check --clang-format;  # Check sources with clang format (autoformatter)
scargo check --cppcheck;      # Check sources with cppcheck (static analysis)
scargo check --clang-tidy;    # Check sources with clang format (naming convention and light static analysis)
scargo check --todo;          # Check for todo comments
scargo check --cyclomatic;    # Calculate cyclomatic complexity
scargo check --pragma;        # Check for existence of pragma directive in headers
scargo check --copyright;     # Check for existence of copyright in files
scargo fix --clang-format;    # Run automate clang formatting for files with issues
scargo fix --copyright;       # Add copyright notice at start of source files (if missing)
scargo fix --pragma;          # Add pragma directive in headers if missing
scargo doc;                   # Generate documentation
scargo publish;               # Publish conan package to artifacts repository
scargo flash;                 # Flash microcontroller board
```

### Other scargo commands (not mandatory for all projects)

```bash
#!/bin/bash
scargo gen #Generate certificate and other artifacts for chosen targets
```


