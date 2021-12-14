import tempfile
from pathlib import Path
import sys
from loguru import logger
import subprocess
from typing import List
from dataclasses import dataclass

vbox_path_default = Path("C:/Program Files/Oracle/VirtualBox")
vboxmanage_path = Path(vbox_path_default / "vboxmanage.exe").resolve()

logger.remove()
default_log_format = "<g>{time:MM/DD/YYYY HH:mm:ss}</g> | <lvl>{level}</lvl> | <lvl><b>{message}</b></lvl>"


@dataclass
class VBoxVM:
    name: str
    headless: bool = False
    encrypted: bool = False
    password_file: tempfile._TemporaryFileWrapper = None

    def start(self):
        """
        Starts self
        :return: None
        """

        logger.info(f"Starting VM: '{self.name}'")

        headless = ""
        if self.headless:
            headless = "--type headless"
        start_cmd = f'startvm "{self.name}" {headless}'

        run_vboxmanage_command(start_cmd)

        if not self.encrypted:
            return None

        if self.password_file:
            # Make sure vm_password_file is a temporary file.
            if not isinstance(self.password_file, tempfile._TemporaryFileWrapper):
                raise TypeError
            with open(self.password_file.name, "r") as f:
                vm_password = f.read()
        else:
            vm_password = False

        if vm_password:
            add_password_cmd = f'controlvm "{self.name}" addencpassword "{self.name}" "{self.password_file.name}"'
            reset_cmd = f'controlvm "{self.name}" reset'

            add_pw_return_code = run_vboxmanage_command(add_password_cmd)
            run_vboxmanage_command(reset_cmd)
        else:
            logger.critical(f"No password or password file for '{self.name}' provided")
            add_pw_return_code = 1

        if add_pw_return_code == 1:
            self.kill()

    def kill(self):
        """
        Kills self
        :return: None
        """
        kill_cmd = f'controlvm "{self.name}" poweroff'
        logger.info(f"Killing VM: '{self.name}'")
        run_vboxmanage_command(kill_cmd)


def run_vboxmanage_command(command: str) -> int:
    """
    Runs a command through VBoxManage.exe.
    :param command: Command string to run.
    :return: Subprocess status code.
    """
    return_code = 0
    command = f'"{vboxmanage_path}" {command}'
    logger.debug(command)
    try:
        cmd_output = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as e:
        cmd_output = e.output
        return_code = e.returncode
    cmd_output = cmd_output.decode("UTF-8").strip()
    if return_code == 1:
        logger.error(cmd_output)
    elif cmd_output != "":
        logger.info(f"VBoxManage.exe: {cmd_output}")
    return return_code


def kill_all_vms(vms: List[VBoxVM]):
    """
    Kills all VMs.
    :param vms: List of VBoxVM.
    :return: None
    """
    for vm in vms:
        vm.kill()


def start_all_vms(vms: List[VBoxVM]):
    """
    :param vms: List of VBoxVM.
    :param vms: List of VMs.
    :return: None
    """
    for vm in vms:
        vm.start()


def enable_logging(log_level: str = "INFO", log_format: str = default_log_format):
    """
    Enables logging.
    :param log_level: Loguru log level.
    :param log_format: Set a Loguru log format other than default.
    :return: None
    """
    logger.add(sys.stderr, format=log_format, level=log_level, colorize=True)


def run(vms: List[VBoxVM]):
    """
    Basic main sequence for starting all vms.
    :param vms: List of VBoxVM.
    :return: None
    """
    start_all_vms(vms)
    usr_input = input("Kill VMS? Y/n")
    if usr_input.lower().strip() != "n":
        kill_all_vms(vms)

    input("Done, press enter to continue")
