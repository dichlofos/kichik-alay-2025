#!/usr/bin/env bash

# convert original images to scaled versions

mkdir -p scaled
cd original
for i in $(find . -size +1M -name '*.jpg'); do
    convert $i -resize 25% ../scaled/$i
    echo $i
done
