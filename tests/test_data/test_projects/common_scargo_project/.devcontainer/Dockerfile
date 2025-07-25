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

FROM cpp AS x86
ARG SSH_PORT

ENV DEBIAN_FRONTEND noninteractive

# configure wxWidget
RUN apt update --fix-missing && \
    apt install -y adwaita-icon-theme-full libwxgtk3.0-gtk3-dev dbus-x11 \
    bzr lib32z1 libncurses5:amd64 usbutils xterm minicom
WORKDIR /opt

FROM x86 AS custom_common_scargo_project_path
# user can add his docker code below which will be integrated with
# main docker file and not overwritten by scargo update
ENV DEBIAN_FRONTEND noninteractive

FROM custom_common_scargo_project_path AS common_scargo_project_path_dev

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
WORKDIR /workspace