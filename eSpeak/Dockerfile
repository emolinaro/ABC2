ARG     BASE_CONTAINER=centos:7

FROM    $BASE_CONTAINER

MAINTAINER Emiliano Molinaro <molinaro@imada.sdu.dk>

LABEL   authors="Jonathan Duddington, Martin Avison, Reece Dunn, Valdis Vitolins" \
        version="1.47.11" \
        description="Text to Speech engine for English and many other languages." 

RUN   \
    set -x \
    yum update -y && \
    yum install -y \
    wget zip unzip \
    which espeak && \
    yum clean all

