###
# THIS FILE WAS GENERATED AUTOMATICALLY. DO NOT CHANGE IT.
###

ARG DOCKER_IMAGE_ROOT=ubuntu:22.04
FROM ${DOCKER_IMAGE_ROOT} as base

ENV DEBIAN_FRONTEND noninteractive

RUN apt update --fix-missing && \
    apt -y install python3.8 python3.8-venv python3-pip \
    binutils git wget \
    scons build-essential pkg-config \
    unzip graphviz nano vim && \
    apt -y install sudo && \
    update-alternatives --install /usr/bin/python python /usr/bin/python3 1 && \
    update-alternatives --install /usr/bin/pip pip /usr/bin/pip3 1

FROM base AS cpp

RUN apt -y install cppcheck bzr lib32z1 \
    clang clang-format clang-tidy valgrind \
    gcovr doxygen curl libcurl4-openssl-dev \
    libcmocka0 libcmocka-dev plantuml

FROM cpp AS stm32
WORKDIR /opt/

# pull the gcc-arm-none-eabi tarball, add path to tar file
RUN wget https://armkeil.blob.core.windows.net/developer/Files/downloads/gnu-rm/10.3-2021.10/gcc-arm-none-eabi-10.3-2021.10-x86_64-linux.tar.bz2 && \
    tar -xvf gcc-arm-none-eabi-10.3-2021.10-x86_64-linux.tar.bz2 && \
    rm gcc-arm-none-eabi-10.3-2021.10-x86_64-linux.tar.bz2 && \
    mv gcc-arm-none-eabi-10.3-2021.10 gcc-arm-none-eabi

RUN apt-get update -q -y && \
    apt-get install -y git make cmake libusb-1.0-0-dev bzr libncurses5:amd64 \
                       openocd gdb-multiarch usbutils xterm minicom stlink-tools

# Set up the compiler path
ENV PATH $PATH:/opt/gcc-arm-none-eabi/bin

RUN curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash && \
    apt-get update && \
    apt-get install -y ca-certificates curl apt-transport-https lsb-release gnupg && \
    curl -sL https://packages.microsoft.com/keys/microsoft.asc | \
    gpg --dearmor | \
    tee /etc/apt/trusted.gpg.d/microsoft.gpg > /dev/null && \
    AZ_REPO=$(lsb_release -cs) && \
    echo "deb [arch=amd64] https://packages.microsoft.com/repos/azure-cli/ $AZ_REPO main" | \
    tee /etc/apt/sources.list.d/azure-cli.list && \
    apt-get update && \
    apt-get install azure-cli

ENV LC_ALL=C
WORKDIR /opt

FROM stm32 AS custom_common_scargo_project_stm32
# user can add his docker code below which will be integrated with
# main docker file and not overwritten by scargo update
ENV DEBIAN_FRONTEND noninteractive

FROM custom_common_scargo_project_stm32 AS common_scargo_project_stm32_dev

ARG USER_NAME=user
ARG USER_PASSWORD=user
ARG UID_NUMBER=1000
ARG GID_NUMBER=1000
ARG SSH_PORT=2000

ARG CONAN_LOGIN_USERNAME
ARG CONAN_PASSWORD
ENV CONAN_LOGIN_USERNAME=${CONAN_LOGIN_USERNAME}
ENV CONAN_PASSWORD=${CONAN_PASSWORD}

WORKDIR /opt

# configure ssh
RUN apt install -y openssh-server ssh-askpass && apt install -y rsync grsync && \
    ssh-keygen -A && mkdir -p /run/sshd && \
    echo "Port $SSH_PORT" >> /etc/ssh/sshd_config

EXPOSE $SSH_PORT

RUN printf "\n\nADDING USER $USER_NAME TO SUDOERS - DEV ENV ONLY!\n\n" >&2 && \
    apt -y install sudo && \
    groupadd $USER_NAME -g $GID_NUMBER; \
    useradd -m -s /bin/bash -N -u $UID_NUMBER $USER_NAME -g $GID_NUMBER && \
    echo "$USER_NAME:$USER_PASSWORD" | chpasswd && \
    echo "$USER_NAME ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers

RUN pip3 install scargo

RUN usermod -a -G dialout ${USER_NAME}
USER ${USER_NAME}
RUN az extension add --name azure-iot
WORKDIR /workspace