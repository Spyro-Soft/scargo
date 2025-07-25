###
# THIS FILE WAS GENERATED AUTOMATICALLY. DO NOT CHANGE IT.
###

ARG DOCKER_IMAGE_ROOT=ubuntu:22.04
FROM ${DOCKER_IMAGE_ROOT} as base

ENV DEBIAN_FRONTEND noninteractive

RUN apt update --fix-missing && \
    apt -y install --no-install-recommends python3 python3-pip \
    git build-essential pkg-config graphviz && \
    apt -y install sudo && \
    rm -rf /var/lib/apt/lists/* && \
    update-alternatives --install /usr/bin/python python /usr/bin/python3 1

FROM base AS cpp

RUN apt update --fix-missing && apt -y --no-install-recommends install cppcheck lib32z1 \
    make cmake clang clang-format clang-tidy gcovr doxygen libcmocka0 libcmocka-dev gdb screen wget && \
    rm -rf /var/lib/apt/lists/*


FROM cpp AS atsam
WORKDIR /opt/


RUN apt-get update -q -y && \
    apt-get install -y --no-install-recommends curl wget openocd gdb-multiarch  && \
    rm -rf /var/lib/apt/lists/*

# pull the gcc-arm-none-eabi tarball, add path to tar file
RUN wget https://developer.arm.com/-/media/Files/downloads/gnu-rm/10.3-2021.10/gcc-arm-none-eabi-10.3-2021.10-x86_64-linux.tar.bz2 && \
    tar -xvf gcc-arm-none-eabi-10.3-2021.10-x86_64-linux.tar.bz2 && \
    rm gcc-arm-none-eabi-10.3-2021.10-x86_64-linux.tar.bz2 && \
    mv gcc-arm-none-eabi-10.3-2021.10 gcc-arm-none-eabi

# Set up the compiler path
ENV PATH $PATH:/opt/gcc-arm-none-eabi/bin

ENV LC_ALL=C
WORKDIR /opt

FROM atsam AS custom_common_scargo_project_atsam
# user can add his docker code below which will be integrated with
# main docker file and not overwritten by scargo update
FROM custom_common_scargo_project_atsam AS common_scargo_project_atsam_dev

ARG USER_NAME=user
ARG USER_PASSWORD=user
ARG UID_NUMBER=1000
ARG GID_NUMBER=1000
ARG SSH_PORT=2000
ARG CONAN_LOGIN_USERNAME=""
ARG CONAN_PASSWORD=""

ENV CONAN_LOGIN_USERNAME=${CONAN_LOGIN_USERNAME}
ENV CONAN_PASSWORD=${CONAN_PASSWORD}

WORKDIR /opt

# configure ssh
RUN apt update --fix-missing && apt install -y --no-install-recommends openssh-server && \
    rm -rf /var/lib/apt/lists/* && \
    ssh-keygen -A && mkdir -p /run/sshd && \
    echo "Port $SSH_PORT" >> /etc/ssh/sshd_config

EXPOSE $SSH_PORT

RUN printf "\n\nADDING USER $USER_NAME TO SUDOERS - DEV ENV ONLY!\n\n" >&2 && \
    apt -y install sudo && \
    groupadd $USER_NAME -g $GID_NUMBER; \
    useradd -m -s /bin/bash -N -u $UID_NUMBER $USER_NAME -g $GID_NUMBER && \
    echo "$USER_NAME:$USER_PASSWORD" | chpasswd && \
    echo "$USER_NAME ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers

RUN pip3 install scargo==2.1.1

RUN usermod -a -G dialout ${USER_NAME}
USER ${USER_NAME}
WORKDIR /workspace