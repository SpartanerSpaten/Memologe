#!/bin/bash
set -ex
docker-compose pull
docker-compose up -d
sleep 20
python3 Memologe_Test.py
