#!/bin/bash
docker buildx build --platform linux/arm/v7 --push -t ghcr.io/moimart/assistant_server .
