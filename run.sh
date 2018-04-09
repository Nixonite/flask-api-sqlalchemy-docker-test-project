#!/usr/bin/env bash

gunicorn --config /etc/gunicorn/config.py app:app
