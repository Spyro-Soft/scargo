echo -e '\e[33m'"docker installation"

apt-get update > /dev/null
apt-get -y install \
    apt-transport-https \
    ca-certificates \
    curl \
    gnupg-agent \
    software-properties-common \
    > /dev/null
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
apt-key fingerprint 0EBFCD88
add-apt-repository \
   "deb [arch=amd64] https://download.docker.com/linux/ubuntu \
   $(lsb_release -cs) \
   stable"
apt-get update > /dev/null
apt-get install -y docker-ce docker-ce-cli containerd.io > /dev/null
usermod -aG docker $USER
su -p $USER newgrp docker
groupadd docker || true

echo -e '\e[32m'"\xE2\x9C\x94 docker successfully installed"
