#!/bin/bash
docker buildx build --no-cache --platform linux/arm/v7 --push -t ghcr.io/moimart/remote_broadcaster .
