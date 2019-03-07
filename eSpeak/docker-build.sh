#!/usr/bin/env bash

SOFTWARE="espeak"
VERSION="1.47.11"

echo " "
echo "  building docker image...."
echo " " 
docker build -t $SOFTWARE:$VERSION --force-rm .

echo " "
echo "  docker image created."
