ARG DOCKER_IMAGE_ROOT
FROM ${DOCKER_IMAGE_ROOT} as base

ENV DEBIAN_FRONTEND=noninteractive

RUN apt update --fix-missing && \
    apt -y install python3.8 python3-pip git build-essential pkg-config graphviz plantuml && \
    update-alternatives --install /usr/bin/python python /usr/bin/python3 1

ADD https://github.com/plantuml/plantuml/releases/download/v1.2022.13/plantuml-1.2022.13.jar /usr/local/share/
ADD ./scripts/plantuml /usr/local/bin/
RUN chmod 755 /usr/local/share/plantuml-1.2022.13.jar /usr/local/bin/plantuml

FROM base AS cpp

RUN apt-get update && apt-get -y install cppcheck lib32z1 \
    clang clang-format clang-tidy doxygen libcmocka0 libcmocka-dev

WORKDIR /opt

FROM cpp AS scargo

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
RUN apt install -y openssh-server && \
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