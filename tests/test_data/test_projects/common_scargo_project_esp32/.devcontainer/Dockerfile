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

FROM cpp AS esp32
RUN  apt -y install flex bison gperf python3-setuptools ninja-build ccache libffi-dev libssl-dev dfu-util libusb-1.0-0

ARG ESPRESSIF_IDF_TAG="v4.4.3"
ARG ESPRESSIF_IDF_VERSION="${ESPRESSIF_IDF_TAG}"
ARG ESPRESSIF_IDF_PATH="/opt/esp-idf"
ARG ESPRESSIF_IDF_REPO_URL="https://github.com/espressif/esp-idf.git"
ARG ESPRESSIF_TOOLS_PATH="/root/.espressif"
ENV  IDF_TOOLS_PATH ${ESPRESSIF_IDF_PATH}
ENV  IDF_PATH ${ESPRESSIF_IDF_PATH}

WORKDIR /opt

RUN umask 0002 && git clone --single-branch --branch ${ESPRESSIF_IDF_VERSION} --recursive ${ESPRESSIF_IDF_REPO_URL} ${ESPRESSIF_IDF_PATH}
RUN umask 0002 && ${ESPRESSIF_IDF_PATH}/install.sh

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

RUN umask 0002 && mkdir /opt/esp/ && echo '#!/usr/bin/env bash\n\
\n\
set -e\n\
\n\
. $IDF_PATH/export.sh\n\
\n\
exec "$@"' >  /opt/esp/entrypoint.sh && chmod 775 /opt/esp/entrypoint.sh

# Install QEMU
ARG QEMU_VER=esp-develop-20220919
ARG QEMU_DIST=qemu-${QEMU_VER}.tar.bz2
ARG QEMU_SHA256=f6565d3f0d1e463a63a7f81aec94cce62df662bd42fc7606de4b4418ed55f870
RUN : \
  && wget --no-verbose https://github.com/espressif/qemu/releases/download/${QEMU_VER}/${QEMU_DIST} \
  && echo "${QEMU_SHA256} *${QEMU_DIST}" | sha256sum --check --strict - \
  && tar -xf ${QEMU_DIST} -C /opt \
  && rm ${QEMU_DIST} \
  && :
ENV PATH=/opt/qemu/bin:${PATH}
WORKDIR /opt

FROM esp32 AS custom_esp32project
# user can add his docker code below which will be integrated with
# main docker file and not overwritten by scargo update
ENV DEBIAN_FRONTEND noninteractive

FROM custom_esp32project AS esp32project_dev

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
RUN /bin/bash -c "echo 'source $IDF_PATH/export.sh'" >> ~/.bashrc
CMD ["/bin/bash"]
WORKDIR /workspace