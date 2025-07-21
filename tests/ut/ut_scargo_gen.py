import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional
from unittest.mock import MagicMock

import pytest
from pytest_mock import MockerFixture
from pytest_subprocess import FakeProcess, fake_popen

from scargo.commands.gen import scargo_gen
from tests.ut.utils import get_test_project_config


@pytest.fixture
def mock_prepare_config(tmpdir: Path, mocker: MockerFixture) -> MagicMock:
    os.chdir(tmpdir)

    x86_config = get_test_project_config("x86")
    x86_config.project_root = Path(tmpdir)

    return mocker.patch(f"{scargo_gen.__module__}.prepare_config", return_value=x86_config)


@pytest.fixture
def mock_prepare_config_esp32(tmpdir: Path, mocker: MockerFixture) -> MagicMock:
    os.environ["IDF_PATH"] = "idf_path"
    os.chdir(tmpdir)

    esp_config = get_test_project_config("esp32")
    esp_config.project_root = Path(tmpdir)

    return mocker.patch(f"{scargo_gen.__module__}.prepare_config", return_value=esp_config)


# -------------- Gen unit_tests tests --------------
def test_gen_ut(mock_prepare_config: MagicMock, mocker: MockerFixture) -> None:
    # This test just checks that generator is called
    # Unit tests for unit test generator should be in seperate file

    mocked_generate_ut = mocker.patch(f"{scargo_gen.__module__}.generate_ut")
    path_to_srcs = Path("path_not_none")

    scargo_gen(
        profile="Debug",
        gen_ut=path_to_srcs,
        gen_mock=None,
        certs=None,
        certs_mode=None,
        certs_input=None,
        certs_passwd=None,
        fs=False,
        single_bin=False,
    )

    mocked_generate_ut.assert_called_once_with(path_to_srcs, mock_prepare_config.return_value)


# -------------- Gen mocks tests --------------
def test_gen_mocknot_header(mock_prepare_config: MagicMock, caplog: pytest.LogCaptureFixture) -> None:
    some_path = Path("not_header_file")

    with pytest.raises(SystemExit):
        scargo_gen(
            profile="Debug",
            gen_ut=None,
            gen_mock=some_path,
            certs=None,
            certs_mode=None,
            certs_input=None,
            certs_passwd=None,
            fs=False,
            single_bin=False,
        )

    assert "Not a header file. Please chose .h or .hpp file." in caplog.text


def test_gen_mock(
    mock_prepare_config: MagicMock,
    mocker: MockerFixture,
    caplog: pytest.LogCaptureFixture,
) -> None:
    # This test just checks that generator is called
    # Unit tests for mock generator should be in seperate file

    mocked_generate_ut = mocker.patch(f"{scargo_gen.__module__}.generate_mocks")
    path_to_hdr = Path("header.h")

    scargo_gen(
        profile="Debug",
        gen_ut=None,
        gen_mock=path_to_hdr,
        certs=None,
        certs_mode=None,
        certs_input=None,
        certs_passwd=None,
        fs=False,
        single_bin=False,
    )

    mocked_generate_ut.assert_called_once_with(path_to_hdr, mock_prepare_config.return_value)
    assert f"Generated: {path_to_hdr}" in caplog.text


def test_gen_mock_fails(
    mock_prepare_config: MagicMock,
    mocker: MockerFixture,
    caplog: pytest.LogCaptureFixture,
) -> None:
    mocked_generate_ut = mocker.patch(f"{scargo_gen.__module__}.generate_mocks", return_value=False)
    path_to_hdr = Path("header.h")

    scargo_gen(
        profile="Debug",
        gen_ut=None,
        gen_mock=path_to_hdr,
        certs=None,
        certs_mode=None,
        certs_input=None,
        certs_passwd=None,
        fs=False,
        single_bin=False,
    )

    mocked_generate_ut.assert_called_once_with(path_to_hdr, mock_prepare_config.return_value)
    assert f"Skipping: {path_to_hdr}" in caplog.text


# -------------- Gen certs tests --------------
TEST_DEVICE_ID = r"com.example.my.solution:gw-01:da:device:ZWave:CA0D6357%2F4"


def mock_create_certs(process: fake_popen.FakePopen, certs_dir: Path) -> None:
    cert_files = [
        certs_dir / "certs/iot-device.cert.pem",
        certs_dir / "private/iot-device.key.pem",
        certs_dir / "ca.pem",
        certs_dir / "certs/azure-iot-test-only.root.ca.cert.pem",
    ]
    for cert_file in cert_files:
        cert_file.parent.mkdir(parents=True, exist_ok=True)
        cert_file.touch()


def test_gen_certs_files_not_exist(fp: FakeProcess, mock_prepare_config: MagicMock) -> None:
    fp.register([fp.any()])

    with pytest.raises(SystemExit):
        scargo_gen(
            profile="Debug",
            gen_ut=None,
            gen_mock=None,
            certs=TEST_DEVICE_ID,
            certs_mode=None,
            certs_input=None,
            certs_passwd=None,
            fs=False,
            single_bin=False,
        )


@dataclass
class GenCertTestData:
    mode_argument: Optional[str]
    expeced_mode_argument: str
    intermediate_dir: Optional[Path] = None
    certs_password: Optional[str] = None


@pytest.mark.parametrize(
    "test_data",
    [
        GenCertTestData(None, "All-certificates"),
        GenCertTestData("all", "All-certificates", Path("dir1"), "4321"),
        GenCertTestData("device", "Device-certificate", Path("dir2"), "0123"),
    ],
)
def test_gen_certs(
    fp: FakeProcess,
    mock_prepare_config: MagicMock,
    test_data: GenCertTestData,
) -> None:
    certs_dir = Path("build/certs").absolute()
    scargo_root = Path(__file__).parent.parent.parent
    script_path = scargo_root / "scargo/certs/generateAllCertificates.sh"

    fp.register(
        [
            str(script_path),
            "--name",
            TEST_DEVICE_ID,
            "--mode",
            test_data.expeced_mode_argument,
            "--output",
            certs_dir,
            "--input",
            test_data.intermediate_dir or certs_dir,
            "--passwd",
            test_data.certs_password or "1234",
        ],
        callback=mock_create_certs,
        callback_kwargs={"certs_dir": certs_dir},
    )

    scargo_gen(
        profile="Debug",
        gen_ut=None,
        gen_mock=None,
        certs=TEST_DEVICE_ID,
        certs_mode=test_data.mode_argument,
        certs_input=test_data.intermediate_dir,
        certs_passwd=test_data.certs_password,
        fs=False,
        single_bin=False,
    )

    assert Path("build/fs/device_cert.pem").is_file()
    assert Path("build/fs/device_priv_key.pem").is_file()
    assert Path("build/fs/ca.pem").is_file()
    assert Path(certs_dir, f"azure/{TEST_DEVICE_ID}-root-ca.pem").is_file()


# -------------- Gen fs tests --------------
def test_gen_fs_unsupored_target(caplog: pytest.LogCaptureFixture, mock_prepare_config: MagicMock) -> None:
    scargo_gen(
        profile="Debug",
        gen_ut=None,
        gen_mock=None,
        certs=None,
        certs_mode=None,
        certs_input=None,
        certs_passwd=None,
        fs=True,
        single_bin=False,
    )

    assert "Gen --fs command not supported for this target yet." in caplog.text


def test_gen_fs_esp32(fp: FakeProcess, mock_prepare_config_esp32: MagicMock) -> None:
    fp.register([fp.any()])

    scargo_gen(
        profile="Debug",
        gen_ut=None,
        gen_mock=None,
        certs=None,
        certs_mode=None,
        certs_input=None,
        certs_passwd=None,
        fs=True,
        single_bin=False,
    )


# -------------- Gen single bin tests --------------
def test_gen_single_bin_unsupored_target(caplog: pytest.LogCaptureFixture, mock_prepare_config: MagicMock) -> None:
    scargo_gen(
        profile="Debug",
        gen_ut=None,
        gen_mock=None,
        certs=None,
        certs_mode=None,
        certs_input=None,
        certs_passwd=None,
        fs=False,
        single_bin=True,
    )

    assert "Gen --bin command not supported for this target yet." in caplog.text


def test_gen_single_bin_esp32(
    fp: FakeProcess,
    mock_prepare_config_esp32: MagicMock,
) -> None:
    build_profile = "Debug"
    flash_args_path = Path(f"build/{build_profile}/flash_args")
    flash_args_path.parent.mkdir(parents=True)
    flash_args_path.touch()
    fp.register([fp.any()])

    scargo_gen(
        profile=build_profile,
        gen_ut=None,
        gen_mock=None,
        certs=None,
        certs_mode=None,
        certs_input=None,
        certs_passwd=None,
        fs=False,
        single_bin=True,
    )
