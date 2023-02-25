#!/bin/bash

set -e

level=$1
if [ -z "$level" ]
then
  echo "Complexity level has not been defined. It must be between 'a' e 'f'."
  exit 1
fi
cyclomatic_complexity_result=$(radon cc -n$level --exclude "venv*" .)
if [ -z "$cyclomatic_complexity_result" ]
then
  echo "All files have low cyclomatic complexity."
else
  echo "Some files were identified with complexity higher than '$level'."
  printf "$cyclomatic_complexity_result\n"
  exit 1
fi
