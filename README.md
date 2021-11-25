# vbox-vm-multistart

This script allows you to easily launch multiple encrypted VMs in VirtualBox.

##### Installation:
```python
pip install -r requirements.txt
```

##### Usage:
```python
from pathlib import Path
import tempfile, os
from getpass import getpass
import vbox_vm_multistart

# Set a VBoxManage.exe path other than default (this is the default)
vbox_path = Path("C:/Program Files/Oracle/VirtualBox")
vbox_vm_multistart.vboxmanage_path = Path(vbox_path / "vboxmanage.exe").resolve()

# Enable logging and set Loguru log level. Log format can also be defined with log_format=.
# https://loguru.readthedocs.io/en/stable/api/logger.html#levels
vbox_vm_multistart.enable_logging(log_level="DEBUG")

# Obtain password
password = getpass()

# Create temp file, write password to it.
temp_file = tempfile.NamedTemporaryFile(delete=False)
temp_file.write(bytes(password, encoding="UTF-8"))
temp_file.close()

# List of VMs.
vms = [
    {
        "name": "vm-1",
        "headless": True,
        "encrypted": True,
        "password_file": temp_file
    },
    {
        "name": "vm-2",
        "headless": False,
        "encrypted": True,
        "password_file": temp_file
    },
    {
        "name": "vm-3",
        # "headless" defaults to False.
        # Other options are optional.
    }
]

try:
    vbox_vm_multistart.run(vms=vms)

except Exception as e:
    raise e

finally:
    # Delete temp file if successful or exception.
    os.unlink(temp_file.name)
```
Other potentially useful functions:
```python
vbox_vm_multistart.start_all_vms(vms=vms)
vbox_vm_multistart.kill_all_vms(vms=vms)

vbox_vm_multistart.start_vm(vms[0])
vbox_vm_multistart.kill_vm(vms[0]["name"])
```
Example output:
```commandline
Password:
11/25/2021 07:09:15 | INFO | Starting VM: 'vm-1'
11/25/2021 07:09:15 | DEBUG | "C:\Program Files\Oracle\VirtualBox\VBoxManage.exe" startvm "vm-1" --type headless
11/25/2021 07:09:23 | INFO | VBoxManage.exe: Waiting for VM "vm-1" to power on...
VM "vm-1" has been successfully started.
11/25/2021 07:09:23 | DEBUG | "C:\Program Files\Oracle\VirtualBox\VBoxManage.exe" controlvm "vm-1" addencpassword "vm-1" "%TEMP%\tmpf_iu9sol"
11/25/2021 07:09:23 | DEBUG | "C:\Program Files\Oracle\VirtualBox\VBoxManage.exe" controlvm "vm-1" reset
11/25/2021 07:09:23 | INFO | Starting VM: 'vm-2'
11/25/2021 07:09:23 | DEBUG | "C:\Program Files\Oracle\VirtualBox\VBoxManage.exe" startvm "vm-2" 
11/25/2021 07:09:32 | INFO | VBoxManage.exe: Waiting for VM "vm-2" to power on...
VM "vm-2" has been successfully started.
11/25/2021 07:09:33 | DEBUG | "C:\Program Files\Oracle\VirtualBox\VBoxManage.exe" controlvm "vm-2" addencpassword "vm-2" "%TEMP%\tmpf_iu9sol"
11/25/2021 07:09:33 | DEBUG | "C:\Program Files\Oracle\VirtualBox\VBoxManage.exe" controlvm "vm-2" reset
Kill VMS? Y/n
> n
Done, press enter to continue
```
No log output:
```commandline
Password:
Kill VMS? Y/n
> n
Done, press enter to continue
```
