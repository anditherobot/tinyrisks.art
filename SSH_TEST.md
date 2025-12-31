# SSH Connection Test

This document explains how to test SSH connectivity to the tinyrisks.art deployment server.

## Quick Start

### Using the Shell Script (Recommended)

The easiest way to test SSH connectivity:

```bash
# Run with default configuration
./test_ssh_connection.sh

# Run with custom SSH key
SSH_KEY=/path/to/your/key ./test_ssh_connection.sh

# With all custom settings
SERVER_HOST=yourserver.com SERVER_USER=ubuntu SSH_KEY=~/.ssh/custom_key ./test_ssh_connection.sh
```

### Using Python Tests

For integration with the test suite:

```bash
# Run SSH connectivity tests
pytest tests/test_ssh_connection.py -v

# Run with custom configuration
SERVER_HOST=yourserver.com SSH_KEY=~/.ssh/custom_key pytest tests/test_ssh_connection.py -v

# Run all tests (SSH tests auto-skip if no key found)
pytest -v
```

## What Gets Tested

Both the shell script and Python tests verify:

1. **SSH Key Exists**: Checks that your SSH private key file exists
2. **Key Permissions**: Verifies key has secure permissions (600)
3. **Connection**: Tests actual SSH connection to the server
4. **Server Status**: Retrieves OS info, hostname, and uptime
5. **Deployment Directory**: Checks if `/var/www/tinyrisks.art` exists
6. **Git Repository**: Verifies git is initialized and shows latest commit

## Default Configuration

If you don't specify environment variables, these defaults are used:

- **SERVER_HOST**: `anditherobot.com` 
- **SERVER_USER**: `ubuntu`
- **SSH_KEY**: `~/.ssh/id_rsa`

These match the deployment configuration in `.github/workflows/deploy.yml`.

## Troubleshooting

### "SSH key not found"

Your SSH key doesn't exist at the expected location.

**Solution**: 
```bash
# Specify your key location
SSH_KEY=/path/to/your/key ./test_ssh_connection.sh
```

### "SSH connection failed"

The SSH connection couldn't be established.

**Common causes**:
1. SSH key not authorized on server
2. Server unreachable
3. Incorrect hostname/username
4. Firewall blocking connection

**Solutions**:

1. **Authorize your key** (most common issue):
   ```bash
   ssh-copy-id -i ~/.ssh/id_rsa ubuntu@anditherobot.com
   ```

2. **Test basic SSH manually**:
   ```bash
   ssh -i ~/.ssh/id_rsa ubuntu@anditherobot.com
   ```

3. **Check server is reachable**:
   ```bash
   ping anditherobot.com
   ```

### "Permission denied (publickey)"

Your SSH key is not authorized on the server.

**Solution**:
```bash
# Copy your public key to the server
ssh-copy-id -i ~/.ssh/id_rsa ubuntu@anditherobot.com

# Or manually add it (if you have password access)
cat ~/.ssh/id_rsa.pub | ssh ubuntu@anditherobot.com "mkdir -p ~/.ssh && cat >> ~/.ssh/authorized_keys"
```

### "WARNING: SSH key has incorrect permissions"

Your private key is too permissive and SSH won't use it.

**Solution**:
```bash
chmod 600 ~/.ssh/id_rsa
```

## Integration with GitHub Actions

The same SSH configuration is used by GitHub Actions for deployment. If your local test passes, it confirms:

- Your SSH key works (same key should be in GitHub secrets)
- Server is accessible
- Deployment directory is properly configured

### Checking GitHub Secrets

Verify your deployment secrets are set:

```bash
gh secret list
```

You should see:
- `SSH_PRIVATE_KEY`
- `SERVER_HOST`
- `SERVER_USER`  
- `REMOTE_PATH`

### Updating GitHub Secrets

If needed, update the SSH key in GitHub:

```bash
gh secret set SSH_PRIVATE_KEY < ~/.ssh/id_rsa
```

## Examples

### Test with verbose output

```bash
# Shell script
./test_ssh_connection.sh

# Python with detailed output
pytest tests/test_ssh_connection.py -v -s
```

### Quick diagnostic test

```bash
# Run the quick diagnostic test (skipped by default)
pytest tests/test_ssh_connection.py::TestSSHConnectionQuick::test_quick_ssh_check -v -s
```

This shows detailed SSH connection information useful for debugging.

### CI/CD Usage

In a CI/CD pipeline:

```yaml
- name: Test SSH Connection
  env:
    SSH_KEY: ${{ secrets.SSH_PRIVATE_KEY }}
    SERVER_HOST: ${{ secrets.SERVER_HOST }}
    SERVER_USER: ${{ secrets.SERVER_USER }}
  run: |
    echo "$SSH_KEY" > /tmp/ssh_key
    chmod 600 /tmp/ssh_key
    SSH_KEY=/tmp/ssh_key ./test_ssh_connection.sh
```

## Security Notes

- **Never commit private keys** to the repository
- Private keys should have **600** permissions (readable only by owner)
- Public keys (`.pub` files) can be shared safely
- GitHub Secrets are encrypted and only accessible during workflow runs

## See Also

- [INFRASTRUCTURE.md](INFRASTRUCTURE.md) - Complete infrastructure documentation
- [DEPLOYMENT.md](DEPLOYMENT.md) - Deployment guide
- [.github/workflows/deploy.yml](.github/workflows/deploy.yml) - Deployment workflow
- [tests/README.md](tests/README.md) - Test suite documentation
