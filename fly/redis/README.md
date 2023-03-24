# Redis on Fly.io

[Project Source](https://redis.io)

## Requirements

* 1 VM
* 1 Volume with 1GB capacity

## Installation

```
fly launch --no-deploy --name <your-app-name>
fly volumes create redis_server --size 1
fly secrets set REDIS_PASSWORD=<your-redis-password>
fly deploy
```
