#!/bin/bash
echo 'Running black'
black .

echo 'Running flake8'
flake8
