from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from scargo.config import Config, Stm32Config
from scargo.file_generators.base_gen import write_template

script_dir = Path(__file__).parent
atmel_arxml_path = script_dir / "atmel.xml"

ADDITIONAL_CPU_DATA = {"cortex-m23": ["atsaml10e16a"]}


@dataclass
class STM32Scrips:
    openocd_cfg = "openocd-script.cfg"


def create_stm32_config(chip: Optional[str]) -> Optional[Stm32Config]:
    if chip is None:
        return None
    return Stm32Config(chip=chip)


def generate_openocd_script(outdir: Path, config: Config) -> None:
    chip = config.get_stm32_config().chip

    chip_script = f"target/{chip[:7].lower()}x.cfg"
    if not Path("/usr/share/openocd/scripts", chip_script).exists():
        chip_script = f"target/{chip[:7].lower()}.cfg"

    write_template(
        outdir / STM32Scrips.openocd_cfg,
        "docker/stm32-openocd.cfg.j2",
        {"chip_script": chip_script},
    )
