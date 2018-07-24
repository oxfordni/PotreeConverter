#!/bin/bash -ex
if [ -d "build/conda" ]; then
  make clean
fi

make condaVenv
source build/conda/bin/activate
pip install -r ./PoTreeReader/requirements.txt