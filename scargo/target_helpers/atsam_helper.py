import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from scargo.config import Config
from scargo.file_generators.base_gen import write_template

script_dir = Path(__file__).parent
atmel_arxml_path = script_dir / "atmel.xml"

ADDITIONAL_CPU_DATA = {"cortex-m23": ["atsaml10e16a"]}


@dataclass
class AtsamScrips:
    openocd_cfg = "openocd-script.cfg"
    gdb_flash = "atsam-gdb.script"


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
    if chip_label.startswith("atsaml1"):
        return "atsaml1x.cfg"  # Not sure about this
    return None


def get_openocd_flash_driver_name(chip_label: str) -> Optional[str]:
    # https://openocd.org/doc-release/html/Flash-Commands.html
    # This should probably be done differently
    if chip_label.startswith("atsamd"):
        return "at91samd"
    if chip_label.startswith("atsaml1"):
        return "at91samd"
    return None


def generate_openocd_script(outdir: Path, config: Config) -> None:
    openocd_script_name = get_openocd_script_name(
        config.get_atsam_config().chip.lower()
    )
    flash_driver = get_openocd_flash_driver_name(config.get_atsam_config().chip.lower())
    if openocd_script_name and openocd_script_name:
        write_template(
            outdir / AtsamScrips.openocd_cfg,
            "docker/atsam-openocd.cfg.j2",
            {
                "config": config,
                "flash_driver": flash_driver,
                "script_name": openocd_script_name,
            },
        )


def generate_gdb_script(outdir: Path, config: Config, bin_path: Path) -> None:
    flash_driver = get_openocd_flash_driver_name(config.get_atsam_config().chip.lower())
    if flash_driver:
        write_template(
            outdir / AtsamScrips.gdb_flash,
            "docker/atsam-gdb.script.j2",
            {"flash_driver": flash_driver, "bin_path": bin_path},
        )
