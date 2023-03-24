# ArchiSteamFarm on Fly.io

[Project Source](https://github.com/JustArchiNET/ArchiSteamFarm)

## Requirements

* 1 VM with at least 1GB RAM (256MB will probably cause OOM issues)
* 1 Volume with 1GB capacity

## Installation

```
fly launch --no-deploy --name <your-app-name>
fly volumes create asf --size 1
fly deploy
fly scale memory 1024
```
