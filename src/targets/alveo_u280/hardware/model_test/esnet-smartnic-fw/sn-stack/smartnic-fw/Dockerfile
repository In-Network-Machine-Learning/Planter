ARG DOCKERHUB_PROXY
FROM ${DOCKERHUB_PROXY}library/ubuntu:focal

ENV DEBIAN_FRONTEND noninteractive
ENV LC_ALL C.UTF-8
ENV LANG C.UTF-8

# Configure local ubuntu mirror as package source
COPY sources.list /etc/apt/sources.list

RUN \
  ln -fs /usr/share/zoneinfo/UTC /etc/localtime && \
  apt-get update -y && \
  apt-get upgrade -y && \
  apt-get install -y --no-install-recommends \
    coreutils \
    jq \
    libgmp10 \
    libgrpc++1 \
    libprotobuf17 \
    locales \
    lsb-release \
    pciutils \
    python3 \
    python3-click \
    python3-jinja2 \
    python3-pip \
    python3-yaml \
    vim-tiny \
    && \
  apt-get autoclean && \
  apt-get autoremove && \
  locale-gen en_US.UTF-8 && \
  update-locale LANG=en_US.UTF-8 && \
  rm -rf /var/lib/apt/lists/*

# RUN \
#   pip3 install \
#     pyyaml-include \
#     yq

CMD ["/bin/bash", "-l"]
