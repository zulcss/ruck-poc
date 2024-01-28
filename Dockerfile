FROM debian:testing

RUN apt-get update && \
    apt-get install -y mmdebstrap \
		       systemd \
		       python3-pip \
		       git
RUN mkdir -p usr/src

