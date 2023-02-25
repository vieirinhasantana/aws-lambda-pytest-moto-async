#!/bin/bash

for folder in src/*; do
  if [ "$folder" != "src/aws" ] && [ "$folder" != "src/tests" ] && [ "$folder" != "src/__init__.py" ] && [ "$folder" != "src/scripts" ] && [ "$folder" != "src/tests@tmp" ] && [ "$folder" != "src/__pycache__" ] && [ "$folder" != "src/scripts@tmp" ]; then
    cd "$folder"
    set -e;
    set -x;
    echo "Testing $folder"
    pytest --cov=app --cov-report term-missing --cov-fail-under 70 test/ -v;
    cd ..;
    cd ..;
  fi
done

# pytest --cov=app --cov-report term-missing --cov-fail-under 70 test/
# radon cc -na --exclude "venv*" .
# pytest -o log_cli=true --log-cli-level=10
