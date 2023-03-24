# Uptime Kuma on Fly.io

[Project Source](https://github.com/louislam/uptime-kuma)

## Requirements

* 1 VM
* 1 Volume with 1GB capacity

## Installation

```
fly launch --no-deploy --name uptime-kuma
fly volumes create uptime_kuma --size 1
fly deploy
```