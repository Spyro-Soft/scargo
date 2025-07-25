import json
import subprocess
import sys
from pathlib import Path
from typing import Optional, Set

from scargo.config_utils import prepare_config
from scargo.logger import get_logger

logger = get_logger()


def scargo_license_check(scan_path: Optional[Path]) -> None:
    config = prepare_config()

    # set scan path
    if scan_path:
        effective_scan_path = scan_path
    else:
        effective_scan_path = config.source_dir_path
    if not effective_scan_path.exists():
        effective_scan_path = config.project_root / "main"
    if not effective_scan_path.exists():
        logger.error(f"No valid source directory found: {effective_scan_path}")
        sys.exit(1)

    # set outpu dir
    output_dir = config.project_root / "build" / "license_checker"
    output_dir.mkdir(parents=True, exist_ok=True)

    report_json = output_dir / "license_report.json"
    sbom_spdx = output_dir / "sbom.spdx"

    # get rules from toml
    if config.check.license is None:
        logger.error("Missing [check.license] section in scargo.toml")
        sys.exit(1)

    blacklisted_licenses: Set[str] = set(config.check.license.blacklist)
    whitelisted_licenses: Set[str] = set(config.check.license.whitelist)
    allowed_copyrights: Set[str] = set(config.check.license.allow_no_license_if_copyright_match)

    logger.info(f"Blacklist: {blacklisted_licenses}")
    logger.info(f"Whitelist: {whitelisted_licenses}")
    logger.info(f"Allowed copyrights: {allowed_copyrights}")

    # RUN SCAN
    license_scanner("scancode", effective_scan_path, report_json, sbom_spdx)

    # RUN CHECK
    check_licenses(
        report_json_path=report_json,
        blacklisted_licenses=blacklisted_licenses,
        whitelisted_licenses=whitelisted_licenses,
    )

    logger.info("License check completed.")
    logger.info(f"License report saved to {report_json}")
    logger.info(f"SBOM saved to {sbom_spdx}")


def license_scanner(scancode_repo_path: str, path: Path, report_json: Path, sbom_spdx: Path) -> None:
    """Runs license check and generates report"""
    logger.info(f"Scanning: {path}, result: {report_json}, sbom: {sbom_spdx}")
    try:
        subprocess.run(
            [
                scancode_repo_path,
                "--license",
                "--copyright",
                "--spdx-tv",
                str(sbom_spdx),
                "--json-pp",
                str(report_json),
                str(path),
            ],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        )
    except subprocess.CalledProcessError as e:
        logger.error("Error occurred during scancode execution:")
        logger.error(e.output)
        sys.exit(1)

    # Check if the files were created
    if report_json.exists():
        logger.info(f"Report JSON file '{report_json}' created successfully.")
    else:
        logger.error(f"Failed to create report JSON file '{report_json}'.")

    if sbom_spdx.exists():
        logger.info(f"SBOM SPDX file '{sbom_spdx}' created successfully.")
    else:
        logger.error(f"Failed to create SBOM SPDX file '{sbom_spdx}'.")


def check_licenses(
    report_json_path: Path,
    blacklisted_licenses: Set[str],
    whitelisted_licenses: Set[str],
) -> None:
    """
    Enforces a license policy:
    - Blacklisted licenses
    - Missing licenses
    - Whitelisted licenses
    - All others
    """
    with report_json_path.open("r") as f:
        report_data = json.load(f)

    flagged_files = []
    for file_info in report_data.get("files", []):
        file_path = file_info.get("path", "")

        # Skip directories
        if file_info.get("type") == "directory":
            continue

        detected_licenses: Set[str] = set()

        # Collect licenses from 'detected_license_expression'
        if file_info.get("detected_license_expression"):
            detected_licenses.add(file_info["detected_license_expression"])

        # Collect licenses from 'license_detections'
        for detection in file_info.get("license_detections", []):
            if detection.get("license_expression"):
                detected_licenses.add(detection["license_expression"])

        # Classify file status
        matched_blacklist = detected_licenses.intersection(blacklisted_licenses)
        matched_whitelist = detected_licenses.intersection(whitelisted_licenses)

        if matched_blacklist:
            status = "Forbidden"
        elif not detected_licenses:
            status = "No License Detected"
        elif matched_whitelist and not matched_blacklist:
            status = "Whitelisted"
        else:
            status = "Unknown License"

        flagged_files.append(
            {
                "path": file_path,
                "licenses_detected": (list(detected_licenses) if detected_licenses else ["NO LICENSE DETECTED"]),
                "status": status,
            }
        )

    logger.info("License Checker Report:")
    for item in flagged_files:
        logger.info(f"{item['status']}: {item['path']} | Licenses: {', '.join(item['licenses_detected'])}")
