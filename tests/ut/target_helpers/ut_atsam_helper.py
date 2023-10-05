import pytest

from scargo.target_helpers.atsam_helper import get_atsam_cpu


@pytest.mark.parametrize(
    ("chip_label", "expected_cpu"),
    [
        ("atsamb11g18a", "cortex-m0"),
        ("atsamd10d14am", "cortex-m0plus"),
        ("atsamd20j14", "cortex-m0plus"),
        ("atsamha1e14ab", "cortex-m0plus"),
        ("atsam3n2b", "cortex-m3"),
        ("atsam3s2a", "cortex-m3"),
        ("atsam3s2a", "cortex-m3"),
        ("atsam4s8c", "cortex-m4"),
        ("atsamg55g19", "cortex-m4"),
        ("atsame70q21", "cortex-m7"),
        ("atsamv71j21", "cortex-m7"),
        ("atsaml10e16a", "cortex-m23"),
        ("ATSAML10E16A", "cortex-m23"),
        ("notatsam", None),
        ("atsamnotsupported", None),
    ],
)
def test_atsam_helper(chip_label: str, expected_cpu: str) -> None:
    assert expected_cpu == get_atsam_cpu(chip_label)
