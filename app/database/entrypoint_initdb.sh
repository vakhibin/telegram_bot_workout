#!/bin/bash

set -x  # Включить вывод команд
echo "Starting database initialization..."
python -m database.init_db
echo "Initialization script finished with exit code $?"