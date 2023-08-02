#!/bin/bash
# #
# @copyright Copyright (C) 2023 SpyroSoft Solutions S.A. All rights reserved.
# #


RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'
DEVICE_NAME=""

HELP_MESSAGE=\
"usage: $(basename "$0") [--help] [--name  <iot_hub_device_name>] [--output  <path>]

Creates docker image specified for user with it's user id and group id settings.
The parameters can be overridden by config option.

The following flags can be used to alter the defaults:
    -h or --help                    Print this help message.
    --name  <iot_hub_device_name>     Sets device name that is known for iot hub.
    --output  <path>                  Output dir.\n"

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
OUTPUT_DIR=$SCRIPT_DIR
INPUT_DIR=""
MODE=""
PASSWD="1234"

while (( "$#" )); do
    case "$1" in
    -h|--help)
        echo -e "${YELLOW}${HELP_MESSAGE}${NC}" >&1
        exit 0
        ;;

    --name) # device name in the IoT Hub
        DEVICE_NAME=$2
        echo -e "${GREEN}Cert generated for device name: ${DEVICE_NAME} ${NC}" >&1
        shift 2
        ;;

    --mode)
        MODE=$2
        echo -e "${GREEN}Mode: ${MODE} ${NC}" >&1
        shift 2
        ;;

    --input) #directory of root_ca, depending if we want to generate all certificates or only device certificate
        INPUT_DIR=$2
        echo -e "${GREEN}Input dir: ${INPUT_DIR} ${NC}" >&1
        shift 2
        ;;

    --output)
        OUTPUT_DIR=$2
        echo -e "${GREEN}Output dir: ${OUTPUT_DIR} ${NC}" >&1
        shift 2
        ;;

    --passwd)
        PASSWD=$2
        echo -e "${GREEN}Set password: ${PASSWD} ${NC}" >&1
        shift 2
        ;;

    -*) # unsupported flags
        echo -e "${RED}Error: Unsupported flag $1" >&2
        echo -e "Use --help for more information${NC}" >&2
        exit 1
        ;;

    *) # wrong input
        echo -e "${RED}Error: Wrong input $1" >&2
        echo -e "Use --help for more information${NC}" >&2
        exit 1
        ;;
    esac
done

if [ -z "$DEVICE_NAME" ]
    then
    echo -e "${RED}Error: No device name $1" >&2
    exit
    fi


mkdir -p ${OUTPUT_DIR}

#Download CA certificate for IoT Hub
DIGIROOT_CERT=${OUTPUT_DIR}/digiroot.pem
CA_PEM=${OUTPUT_DIR}/ca.pem

rm -f ${CA_PEM}

if [ -f "$DIGIROOT_CERT" ]; then
    echo "$DIGIROOT_CERT already exists."
else
    wget https://cacerts.digicert.com/DigiCertGlobalRootG2.crt.pem -O ${DIGIROOT_CERT}
    if [ $? -ne 0 ]; then
        echo -e "${RED} Failed to download Digiroot certificate" >&2
        rm -f ${DIGIROOT_CERT}
        exit 1
    fi
fi

cp ${DIGIROOT_CERT} ${CA_PEM}

if [ ${MODE} == "Device-certificate" ]; then
    #Generate only device cert
    CERT_DIR=${INPUT_DIR:="/workspace/build/certs"}
    ${SCRIPT_DIR}/certGen.sh --create_device_certificate_from_intermediate ${DEVICE_NAME} ${CERT_DIR} \
        --output ${OUTPUT_DIR} \
        --password ${PASSWD}
elif [ ${MODE} == "All-certificates" ]; then
    #Generate all certificates
    CERT_DIR=${INPUT_DIR:="/workspace/build/certs"}
    ${SCRIPT_DIR}/certGen.sh --create_root_and_intermediate --output ${OUTPUT_DIR} --password ${PASSWD}
    ${SCRIPT_DIR}/certGen.sh --create_device_certificate ${DEVICE_NAME} ${CERT_DIR} --output ${OUTPUT_DIR} --password ${PASSWD}
else
    echo "Wrong input directory"
fi

echo -e \
"${RED}/**********************************************************************************************************************************************************************************${NC}";
echo -e \
"${RED}Go to Azure IoT Hub (https://portal.azure.com/) and navigate to Certificates. Add a new certificate, providing the root CA file: ${SCRIPT_DIR}/certs/azure-iot-test-only.root.ca.cert.pem${NC}";
echo -e \
"${RED}/**********************************************************************************************************************************************************************************${NC}";

echo -e \
"${YELLOW}/**********************************************************************************************************************************************************************************${NC}";
echo -e \
"${YELLOW} If you have no device to work with x509  authentication. ${NC}";
echo -e \
"${YELLOW}On Azure IoT Hub, navigate to the IoT Devices section, or launch Azure IoT Explorer. Add a new device (${DEVICE_NAME}), and for its authentication type chose \"X.509 CA Signed\". ${NC}";
echo -e \
"${YELLOW}/**********************************************************************************************************************************************************************************${NC}";
