# ----- RUST

FROM rust:1.93.1-slim-bookworm AS rust-tools

RUN apt-get update && apt-get install -y --no-install-recommends build-essential

RUN cargo install --version 2.13.1 feroxbuster

# ----- GOLANG

FROM golang:1.25.0-bookworm AS go-tools

ENV GOBIN=/go/bin

RUN apt-get update && apt-get install -y --no-install-recommends autoconf automake build-essential libtool pkg-config

# ENV CGO_ENABLED=1
# RUN git clone https://github.com/openvenues/libpostal && cd libpostal \
# 	&& ./bootstrap.sh && ./configure --datadir=/usr/local/share/libpostal \
# 	&& make -j $(nproc) && make install \
# 	&& ldconfig

RUN git clone --depth 1 --branch v3.93.8 https://github.com/trufflesecurity/trufflehog && cd trufflehog \
	&& go build -trimpath -o ${GOBIN}/trufflehog

RUN go install github.com/lc/gau/v2/cmd/gau@v2.2.4 \
	&& go install github.com/owasp-amass/amass/v4/cmd/amass@v4.2.0 \
	&& go install github.com/projectdiscovery/asnmap/cmd/asnmap@v1.1.1 \
	&& go install github.com/projectdiscovery/httpx/cmd/httpx@v1.8.1 \
	&& go install github.com/projectdiscovery/nuclei/v3/cmd/nuclei@v3.7.0 \
	&& go install github.com/projectdiscovery/subfinder/v2/cmd/subfinder@v2.12.0 \
	&& go install github.com/projectdiscovery/uncover/cmd/uncover@v1.2.0 \
	&& go install github.com/utkusen/urlhunter@v0.2.0

# ----- PYTHON

FROM python:3.14-slim-bookworm

RUN apt-get update && apt-get install -y --no-install-recommends \
	curl \
	dnsutils \
	git \
	libimage-exiftool-perl \
	nmap \
	openjdk-17-jdk-headless \
	openssl \
	sslscan

RUN python3 -m pip install --upgrade --no-cache-dir playwright && playwright install --with-deps chromium

RUN python3 -m pip install --upgrade --no-cache-dir pip build setuptools wheel \
	git+https://github.com/darkoperator/dnsrecon@1.5.3 \
	git+https://github.com/hannob/snallygaster@v0.0.15 \
	git+https://github.com/ivan-sincek/auto-recon@v1.1.0 \
	git+https://github.com/ivan-sincek/chad@v7.5 \
	git+https://github.com/ivan-sincek/forbidden@v13.4 \
	git+https://github.com/ivan-sincek/scrapy-scraper@v4.0 \
	git+https://github.com/laramies/theHarvester@4.10.0

RUN apt-get purge -y --auto-remove git \
	&& apt-get auto-remove -y \
	&& apt-get clean \
	&& rm -rf /root/.cache/* /tmp/* /var/cache/apt/* /var/lib/apt/lists/* /var/tmp/* 

COPY --from=rust-tools /usr/local/cargo/bin/feroxbuster /usr/local/bin/feroxbuster
COPY --from=go-tools /go/bin/ /usr/local/bin/

# COPY --from=go-tools /usr/local/lib/libpostal* /usr/local/lib/
# COPY --from=go-tools /usr/local/share/libpostal /usr/local/share/libpostal
# ENV LIBPOSTAL_DATA_DIR=/usr/local/share/libpostal
# RUN ldconfig

RUN nuclei -update-templates

RUN groupadd -r auto-recon && useradd -r -m -d /home/auto-recon -g auto-recon auto-recon && chown -R auto-recon:auto-recon /home/auto-recon
USER auto-recon
WORKDIR /home/auto-recon

ENTRYPOINT [ "auto-recon" ]
