import paramiko
from typing import Tuple, Optional
from . import models
from .config import settings

# List of dangerous commands to block
DANGEROUS_COMMANDS = [
    "rm -rf /",
    "shutdown",
    "reboot",
    "halt",
    "poweroff",
    "init 0",
    "init 6",
    "dd if=/dev/zero",
    ":(){ :|:& };:",
    "mkfs",
    "format",
    "fdisk",
]

def is_dangerous_command(command: str) -> bool:
    """Check if a command is in the dangerous commands list."""
    return any(dangerous in command.lower() for dangerous in DANGEROUS_COMMANDS)

def execute_ssh_command(
    server: models.RemoteServer,
    command: str
) -> Tuple[str, Optional[str], int]:
    """
    Execute a command on a remote server using SSH.
    Returns (output, error, exit_status)
    """
    if is_dangerous_command(command):
        raise ValueError("Dangerous command detected and blocked")

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        # Create a temporary file for the private key
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as key_file:
            key_file.write(server.private_key)
            key_file.flush()
            
            # Connect to the server
            ssh.connect(
                hostname=server.ip_address,
                username=server.username,
                key_filename=key_file.name,
                port=server.port
            )
            
            # Execute the command
            stdin, stdout, stderr = ssh.exec_command(command)
            
            # Get the output and error
            output = stdout.read().decode()
            error = stderr.read().decode()
            exit_status = stdout.channel.recv_exit_status()
            
            return output, error if error else None, exit_status
            
    except Exception as e:
        return "", str(e), -1
    finally:
        ssh.close() 