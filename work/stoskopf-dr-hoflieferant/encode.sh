#!/usr/bin/env bash

python create_tei.py
python add_characters_to_tei.py

if [ "$#" -ne 1 ]; then
    exit
fi

if [ $1 = dra ]; then
  python dracorizer.py
fi