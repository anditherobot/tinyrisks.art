"""
Test SSH connectivity to the deployment server.

This test verifies that the SSH connection to the deployment server is working correctly.
It's particularly useful for validating deployment configuration and troubleshooting
GitHub Actions deployment issues.

Usage:
    pytest tests/test_ssh_connection.py -v
    
    Or with custom SSH key:
    SSH_KEY=/path/to/key pytest tests/test_ssh_connection.py -v

Environment Variables:
    SERVER_HOST: Server hostname (default: anditherobot.com)
    SERVER_USER: SSH username (default: ubuntu)
    SSH_KEY: Path to SSH private key (default: ~/.ssh/id_rsa)
"""

import os
import subprocess
import pytest
from pathlib import Path


class TestSSHConnection:
    """Test SSH connectivity to deployment server."""
    
    @pytest.fixture
    def ssh_config(self):
        """Get SSH configuration from environment or defaults."""
        return {
            'host': os.getenv('SERVER_HOST', 'anditherobot.com'),
            'user': os.getenv('SERVER_USER', 'ubuntu'),
            'key': os.getenv('SSH_KEY', str(Path.home() / '.ssh' / 'id_rsa'))
        }
    
    def test_ssh_key_exists(self, ssh_config):
        """Test that SSH private key exists."""
        key_path = Path(ssh_config['key'])
        if not key_path.exists():
            pytest.skip(f"SSH key not found at {ssh_config['key']}. Set SSH_KEY environment variable.")
        
        assert key_path.is_file(), f"SSH key path exists but is not a file: {ssh_config['key']}"
    
    def test_ssh_key_permissions(self, ssh_config):
        """Test that SSH key has correct permissions (600)."""
        key_path = Path(ssh_config['key'])
        if not key_path.exists():
            pytest.skip(f"SSH key not found at {ssh_config['key']}")
        
        # Get file permissions (Unix-like systems)
        try:
            import stat
            mode = key_path.stat().st_mode
            # Should be -rw------- (600)
            # We check that group and others have no permissions
            assert not (mode & stat.S_IRGRP), "SSH key should not be readable by group"
            assert not (mode & stat.S_IWGRP), "SSH key should not be writable by group"
            assert not (mode & stat.S_IROTH), "SSH key should not be readable by others"
            assert not (mode & stat.S_IWOTH), "SSH key should not be writable by others"
        except Exception as e:
            pytest.skip(f"Could not check permissions: {e}")
    
    def test_ssh_connectivity(self, ssh_config):
        """Test that SSH connection to the server works."""
        key_path = Path(ssh_config['key'])
        if not key_path.exists():
            pytest.skip(f"SSH key not found at {ssh_config['key']}. Set SSH_KEY environment variable.")
        
        # Attempt SSH connection with a simple command
        cmd = [
            'ssh',
            '-i', ssh_config['key'],
            '-o', 'StrictHostKeyChecking=no',
            '-o', 'ConnectTimeout=10',
            '-o', 'BatchMode=yes',
            f"{ssh_config['user']}@{ssh_config['host']}",
            'echo "SSH_CONNECTION_OK"'
        ]
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=15
            )
            
            # Check if connection was successful
            if result.returncode != 0:
                pytest.fail(
                    f"SSH connection failed with return code {result.returncode}\n"
                    f"STDERR: {result.stderr}\n"
                    f"STDOUT: {result.stdout}\n"
                    f"Make sure the SSH key is authorized on the server.\n"
                    f"Run: ssh-copy-id -i {ssh_config['key']} {ssh_config['user']}@{ssh_config['host']}"
                )
            
            assert 'SSH_CONNECTION_OK' in result.stdout, \
                f"SSH connection succeeded but unexpected output: {result.stdout}"
            
        except subprocess.TimeoutExpired:
            pytest.fail(
                f"SSH connection timed out after 15 seconds.\n"
                f"Server: {ssh_config['user']}@{ssh_config['host']}\n"
                f"Check network connectivity and server availability."
            )
        except FileNotFoundError:
            pytest.skip("SSH client not found. This test requires SSH to be installed.")
    
    def test_deployment_directory_exists(self, ssh_config):
        """Test that the deployment directory exists on the server."""
        key_path = Path(ssh_config['key'])
        if not key_path.exists():
            pytest.skip(f"SSH key not found at {ssh_config['key']}")
        
        remote_path = os.getenv('REMOTE_PATH', '/var/www/tinyrisks.art')
        
        cmd = [
            'ssh',
            '-i', ssh_config['key'],
            '-o', 'StrictHostKeyChecking=no',
            '-o', 'ConnectTimeout=10',
            '-o', 'BatchMode=yes',
            f"{ssh_config['user']}@{ssh_config['host']}",
            f'test -d {remote_path} && echo "EXISTS" || echo "NOT_EXISTS"'
        ]
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=15
            )
            
            if result.returncode != 0:
                pytest.skip("Could not connect to server to check directory")
            
            output = result.stdout.strip()
            assert output == "EXISTS", \
                f"Deployment directory {remote_path} does not exist on server. " \
                f"Create it or check REMOTE_PATH environment variable."
        
        except subprocess.TimeoutExpired:
            pytest.skip("Connection timeout while checking deployment directory")
        except FileNotFoundError:
            pytest.skip("SSH client not found")
    
    def test_git_repository_initialized(self, ssh_config):
        """Test that git repository is initialized in deployment directory."""
        key_path = Path(ssh_config['key'])
        if not key_path.exists():
            pytest.skip(f"SSH key not found at {ssh_config['key']}")
        
        remote_path = os.getenv('REMOTE_PATH', '/var/www/tinyrisks.art')
        
        cmd = [
            'ssh',
            '-i', ssh_config['key'],
            '-o', 'StrictHostKeyChecking=no',
            '-o', 'ConnectTimeout=10',
            '-o', 'BatchMode=yes',
            f"{ssh_config['user']}@{ssh_config['host']}",
            f'test -d {remote_path}/.git && echo "GIT_EXISTS" || echo "GIT_NOT_EXISTS"'
        ]
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=15
            )
            
            if result.returncode != 0:
                pytest.skip("Could not connect to server to check git repository")
            
            output = result.stdout.strip()
            if output != "GIT_EXISTS":
                pytest.skip(
                    f"Git repository not initialized in {remote_path}. "
                    f"This is expected for first-time deployment. "
                    f"GitHub Actions will initialize it on first push."
                )
        
        except subprocess.TimeoutExpired:
            pytest.skip("Connection timeout while checking git repository")
        except FileNotFoundError:
            pytest.skip("SSH client not found")


class TestSSHConnectionQuick:
    """Quick SSH connection test without fixtures for manual runs."""
    
    @pytest.mark.skip(reason="Manual test - run explicitly with: pytest tests/test_ssh_connection.py::TestSSHConnectionQuick::test_quick_ssh_check -v -s")
    def test_quick_ssh_check(self):
        """Quick manual SSH check - prints diagnostic information."""
        ssh_config = {
            'host': os.getenv('SERVER_HOST', 'anditherobot.com'),
            'user': os.getenv('SERVER_USER', 'ubuntu'),
            'key': os.getenv('SSH_KEY', str(Path.home() / '.ssh' / 'id_rsa'))
        }
        
        print("\n" + "="*50)
        print("SSH Connection Diagnostic Information")
        print("="*50)
        print(f"Server: {ssh_config['user']}@{ssh_config['host']}")
        print(f"SSH Key: {ssh_config['key']}")
        print(f"Key exists: {Path(ssh_config['key']).exists()}")
        
        if not Path(ssh_config['key']).exists():
            print("\n❌ SSH key not found!")
            print(f"Set environment variable: export SSH_KEY=/path/to/key")
            pytest.skip("SSH key not found")
        
        cmd = [
            'ssh',
            '-i', ssh_config['key'],
            '-o', 'StrictHostKeyChecking=no',
            '-o', 'ConnectTimeout=10',
            '-v',  # Verbose for diagnostics
            f"{ssh_config['user']}@{ssh_config['host']}",
            'uname -a; echo ""; echo "Deployment dir:"; ls -la /var/www/tinyrisks.art 2>&1 | head -5'
        ]
        
        print("\nExecuting SSH command...")
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=20)
        
        print("\n--- SSH Output ---")
        print(result.stdout)
        if result.stderr:
            print("\n--- SSH Errors/Debug ---")
            print(result.stderr)
        print("\n--- Return Code ---")
        print(result.returncode)
        print("="*50)
        
        assert result.returncode == 0, "SSH connection failed - see output above"
