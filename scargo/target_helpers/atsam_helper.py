import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Optional

script_dir = Path(__file__).parent
atmel_arxml_path = script_dir / "atmel.xml"

ADDITIONAL_CPU_DATA = {"cortex-m23": ["atsaml10e16a"]}


def get_atsam_cpu(chip_label: str) -> Optional[str]:
    cpu = None
    chip_label = chip_label.lower()

    if not chip_label.startswith("atsam"):
        return None

    # Check in dict
    for cpu, chip_list in ADDITIONAL_CPU_DATA.items():
        if chip_label in chip_list:
            return cpu

    # Check in xml
    tree = ET.parse(atmel_arxml_path)
    root = tree.getroot()
    for element in root.iter():
        name = element.attrib.get("name", "")
        if name.startswith("cortex"):
            cpu = name
        if chip_label in name:
            return cpu
    return None
