import tempfile
from pathlib import Path
import sys
from loguru import logger
import subprocess
from typing import List

vbox_path_default = Path("C:/Program Files/Oracle/VirtualBox")
vboxmanage_path = Path(vbox_path_default / "vboxmanage.exe").resolve()

logger.remove()
default_log_format = "<g>{time:MM/DD/YYYY HH:mm:ss}</g> | <lvl>{level}</lvl> | <lvl><b>{message}</b></lvl>"


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


def kill_vm(vm_name: str) -> None:
    """
    Kills a VM.
    :param vm_name: VM name string.
    :return: None
    """
    kill_cmd = f'controlvm "{vm_name}" poweroff'
    logger.info(f"Killing VM: '{vm_name}'")
    run_vboxmanage_command(kill_cmd)


def start_vm(vm: dict) -> None:
    """
    Starts a provided VM.
    :param vm: VM dict.
    :return: None
    """
    vm_name = vm["name"]
    try:
        vm_headless = vm["headless"]
    except KeyError:
        vm_headless = False
    try:
        vm_encrypted = vm["encrypted"]
    except KeyError:
        vm_encrypted = False

    logger.info(f"Starting VM: '{vm_name}'")

    headless = ""
    if vm_headless:
        headless = "--type headless"
    start_cmd = f'startvm "{vm_name}" {headless}'

    run_vboxmanage_command(start_cmd)

    if vm_encrypted:
        try:
            vm_password_file = vm["password_file"]
            # Make sure vm_password_file is a temporary file.
            if not isinstance(vm_password_file, tempfile._TemporaryFileWrapper):
                raise TypeError
            with open(vm_password_file.name, "r") as f:
                vm_password = f.read()
        except KeyError:
            vm_password_file = None
            vm_password = False

        if vm_password:
            add_password_cmd = f'controlvm "{vm_name}" addencpassword "{vm_name}" "{vm_password_file.name}"'
            reset_cmd = f'controlvm "{vm_name}" reset'

            add_pw_return_code = run_vboxmanage_command(add_password_cmd)
            run_vboxmanage_command(reset_cmd)
        else:
            logger.critical(f"No password or password file for '{vm_name}' provided")
            add_pw_return_code = 1

        if add_pw_return_code == 1:
            kill_vm(vm_name)


def kill_all_vms(vms: List[dict]) -> None:
    """
    Kills all VMs.
    :param vms: List of VMs.
    :return: None
    """
    for vm in vms:
        kill_vm(vm["name"])


def start_all_vms(vms: List[dict]) -> None:
    """
    Starts all provided VMs.
    :param vms: List of VMs.
    :return: None
    """
    for vm in vms:
        start_vm(vm)


def enable_logging(log_level: str = "INFO", log_format: str = default_log_format) -> None:
    """
    Enables logging.
    :param log_level: Loguru log level.
    :param log_format: Set a Loguru log format other than default.
    :return: None
    """
    logger.add(sys.stderr, format=log_format, level=log_level, colorize=True)


def run(vms: List[dict]) -> None:
    """
    Basic main sequence for starting all vms.
    :param vms: List of VMs.
    :return: None
    """
    start_all_vms(vms)
    usr_input = input("Kill VMS? Y/n")
    if usr_input.lower().strip() != "n":
        kill_all_vms(vms)

    input("Done, press enter to continue")
