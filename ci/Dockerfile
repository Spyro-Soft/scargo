# #
# @copyright Copyright (C) 2022 SpyroSoft Solutions S.A. All rights reserved.
# #

ARG DOCKER_IMAGE_ROOT
FROM ${DOCKER_IMAGE_ROOT} as base

ENV DEBIAN_FRONTEND=noninteractive

RUN apt update --fix-missing && \
    apt -y install python3.8 python3.8-venv python3-pip \
    binutils git wget \
    scons build-essential pkg-config \
    unzip texlive-latex-base graphviz nano vim \
    libgtk2.0-0 libgtk-3-0 libxss1 libasound2 plantuml && \
    apt -y install sudo && \
    update-alternatives --install /usr/bin/python python /usr/bin/python3 1 && \
    update-alternatives --install /usr/bin/pip pip /usr/bin/pip3 1

ADD https://github.com/plantuml/plantuml/releases/download/v1.2022.13/plantuml-1.2022.13.jar /usr/local/share/
ADD ./scripts/plantuml /usr/local/bin/
RUN chmod 755 /usr/local/share/plantuml-1.2022.13.jar /usr/local/bin/plantuml

FROM base AS cpp

RUN apt-get update && apt-get -y install cppcheck bzr lib32z1 \
    clang clang-format clang-tidy valgrind \
    gcovr doxygen curl libcurl4-openssl-dev \
    libcmocka0 libcmocka-dev

FROM cpp AS python

# Set up a reports generation tool
RUN apt-get update --fix-missing && \
    wget https://github.com/allure-framework/allure2/releases/download/2.13.7/allure_2.13.7-1_all.deb && \
    apt install -y ./allure_2.13.7-1_all.deb && \
    rm allure_2.13.7-1_all.deb && \
    chmod 777 /usr/bin/allure && \
    apt-get clean && \
    apt-get autoremove --yes && \
    rm -rf /var/lib/{cache,log} && \
    rm -rf /var/lib/apt/lists/*

# for end-to-end testing puprose
RUN apt update --fix-missing && apt -y install cppcheck bzr lib32z1 \
    clang clang-format clang-tidy valgrind \
    gcovr doxygen curl libcurl4-openssl-dev \
    libcmocka0 libcmocka-dev

WORKDIR /opt

FROM python AS scargo

ARG USER_NAME
ARG USER_PASSWORD
ARG UID_NUMBER
ARG GID_NUMBER
ARG SSH_PORT

ARG CONAN_USERNAME
ARG CONAN_PASS_KEY
ENV CONAN_USERNAME=${CONAN_USERNAME}
ENV CONAN_PASS_KEY=${CONAN_PASS_KEY}

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

# install scargo from spyro rep (temporarly before pip repo will be available)
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt && \
    rm requirements.txt

RUN usermod -a -G dialout ${USER_NAME}
USER ${USER_NAME}
WORKDIR /repo