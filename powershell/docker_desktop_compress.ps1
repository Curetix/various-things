# Compress the WSL2 Docker volume to reduce disk space usage

Read-Host -Prompt 'Stop Docker Desktop and press Enter'
wsl --shutdown
sudo Optimize-VHD -Path $env:LOCALAPPDATA\Docker\wsl\data\ext4.vhdx -Mode Full
