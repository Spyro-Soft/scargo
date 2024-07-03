# #
# @copyright Copyright (C) 2024 SpyroSoft Solutions S.A. All rights reserved.
# #

import atexit
import os
import signal
import sys
import threading
from types import FrameType
from typing import Optional

import serial  # type: ignore

from scargo.logger import get_logger

logger = get_logger()

AT_EOF = "\r\n"


class CmdLoop:
    def __init__(self, ser: serial.Serial) -> None:  # type: ignore[no-any-unimported]
        """Init of the command loop

        Args:
            ser (serial.Serial): serial instance
        """
        self.ser = ser
        self.running = True

    def run(self) -> None:
        """Infinit keyboard input loop"""
        while self.running:
            cmd = input()
            if not self.parse_cmd(cmd):
                break

    def parse_cmd(self, cmd: str) -> bool:
        """Parse command to the device


        Args:
            cmd (str): command

        Returns:
            bool: send successfully to the device
        """
        try:
            self.ser.write(str.encode(cmd + AT_EOF))
        except Exception as e:  # pylint: disable=broad-except
            logger.error("Unexpected error: %s", e)
            return False

        return True

    def stop(self) -> None:
        """Stop the infinit loop"""
        self.running = False


class SerialReadThread(threading.Thread):
    def __init__(self, ser: serial.Serial, read_block_size: int = 1000) -> None:  # type: ignore[no-any-unimported]
        """Init the serial data

        Args:
            ser (serial.Serial): _description_
            read_block_size (int, optional): _description_. Defaults to 1000.

        Returns:
            Any: _description_
        """
        super().__init__()
        self.ser = ser
        self.read_block_size = read_block_size
        self.running = True

    def run(self) -> None:
        """Infinite serial read/write loop"""
        while self.running:
            if self.ser.closed:
                break
            self.read_serial()

    def read_serial(self) -> None:
        """Read data from the serial interface"""
        if not self.running or self.ser.closed:
            return
        try:
            s = self.ser.read(self.read_block_size)
            if s:
                print(s.decode())
        except Exception as e:  # pylint: disable=broad-except
            if "Attempting to use a port that is not open" in str(e):
                logger.error("Unexpected error: %s", e)
                os._exit(1)
            else:
                logger.error("Unexpected error: %s", e)

    def stop(self) -> None:
        """Stop the infinit loop"""
        self.running = False


class _ScargoMonitor:
    DEFAULT_BAUDRATE = 115200

    def __init__(
        self,
        port: Optional[str],
        baudrate: Optional[int],
    ) -> None:
        self._port = port
        self._baudrate = baudrate or self.DEFAULT_BAUDRATE
        self.read_thread: Optional[SerialReadThread] = None
        self.cmd_loop: Optional[CmdLoop] = None
        self.ser = None

    def serial_monitor(self) -> None:
        self.ser = serial.Serial(self._port, self._baudrate, timeout=2)
        self.read_thread = SerialReadThread(self.ser)
        if self.read_thread is not None:
            self.read_thread.start()

        self.cmd_loop = CmdLoop(self.ser)
        self.setup_signal_handler()
        if self.cmd_loop is not None:
            self.cmd_loop.run()

        if self.read_thread is not None:
            self.read_thread.join()

    def setup_signal_handler(self) -> None:
        def cleanup() -> None:
            if self.cmd_loop:
                self.cmd_loop.stop()
            if self.read_thread and self.read_thread.running:
                self.read_thread.stop()
            if self.ser and not self.ser.closed:
                self.ser.close()

        def signal_handler(_sig: int, _frame: Optional[FrameType]) -> None:
            """handle CTRL+C

            Args:
                _sig (int): Signal number.
                _frame (FrameType): Current stack frame.
            """
            cleanup()
            sys.exit(0)

        atexit.register(cleanup)
        signal.signal(signal.SIGINT, signal_handler)
        sys.stdin.flush()


def scargo_monitor(
    port: Optional[str],
    baudrate: Optional[int],
) -> None:
    monitor = _ScargoMonitor(port, baudrate)
    monitor.serial_monitor()
