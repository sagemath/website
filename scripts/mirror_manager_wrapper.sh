#!/usr/bin/env bash

cd `dirname "$0"`

flock -xn ./mirror_manager.lock python3 mirror_manager.py RUNME

