#!/bin/bash

set -e -x

coverage run --branch -m pytest tests
coverage xml
coverage erase