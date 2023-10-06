import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from scargo.config import Config
from scargo.file_generators.base_gen import create_file_from_template

script_dir = Path(__file__).parent
atmel_arxml_path = script_dir / "atmel.xml"

ADDITIONAL_CPU_DATA = {"cortex-m23": ["atsaml10e16a"]}


@dataclass
class AtsamScrips:
    openocd_cfg = "config/openocd_script.cfg"
    gdb_flash = "config/gdb-flash.script"
    gdb_reset = "config/gdb-reset.script"


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


def get_openocd_script_name(chip_label: str) -> Optional[str]:
    if chip_label.startswith("atsamd"):
        return "at91samdXX.cfg"
    elif chip_label.startswith("atsaml1"):
        return "atsaml1x.cfg"
    return None


def get_openocd_flash_driver_name(chip_label: str) -> Optional[str]:
    if chip_label.startswith("atsamd"):
        return "at91samd"
    elif chip_label.startswith("atsaml1"):
        return "at91samd"
    return None


def generate_openocd_script(config: Config) -> None:
    openocd_script_name = get_openocd_script_name(
        config.get_atsam_config().chip.lower()
    )
    chip_name = get_openocd_flash_driver_name(config.get_atsam_config().chip.lower())
    if openocd_script_name and chip_name:
        create_file_from_template(
            "atsam/openocd_script.cfg.j2",
            config.project_root / AtsamScrips.openocd_cfg,
            {"chip_name": chip_name, "script_name": openocd_script_name},
            config,
            True,
        )


def generate_gdb_scripts(config: Config, bin_path: Path) -> None:
    openocd_chip_name = get_openocd_flash_driver_name(
        config.get_atsam_config().chip.lower()
    )
    if openocd_chip_name:
        create_file_from_template(
            "atsam/gdb-reset.script.j2",
            config.project_root / AtsamScrips.gdb_reset,
            {"openocd_chip": openocd_chip_name},
            config,
            True,
        )
        create_file_from_template(
            "atsam/gdb-flash.script.j2",
            config.project_root / AtsamScrips.gdb_flash,
            {"openocd_chip": openocd_chip_name, "bin_path": bin_path},
            config,
            True,
        )
