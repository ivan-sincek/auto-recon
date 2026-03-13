FROM python:3.14-slim-bookworm

ENV DEBIAN_FRONTEND=noninteractive \
	CGO_ENABLED=1 \
	GOBIN=/usr/local/bin \
	RUSTUP_HOME=/usr/local/rustup \
	CARGO_HOME=/usr/local/cargo \
	PATH="${CARGO_HOME}}/bin:${PATH}"

WORKDIR /home/autorecon

RUN apt-get update && apt-get install -y --no-install-recommends \
	autoconf \
	automake \
	build-essential \
	ca-certificates \
	curl \
	dnsutils \
	git \
	libcurl4-gnutls-dev \
	libimage-exiftool-perl \
	librtmp-dev \
	libtool \
	nmap \
	openjdk-17-jdk-headless \
	openssl \
	pkg-config \
	sslscan

RUN python3 -m pip install --upgrade --no-cache-dir pip build setuptools wheel \
	git+https://github.com/darkoperator/dnsrecon@1.5.3 \
	git+https://github.com/hannob/snallygaster@v0.0.15 \
	git+https://github.com/laramies/theHarvester@4.10.0 \
	git+https://github.com/ivan-sincek/auto-recon@v1.1.0 \
	git+https://github.com/ivan-sincek/forbidden@v13.4 \
	git+https://github.com/ivan-sincek/chad@v7.5 \
	git+https://github.com/ivan-sincek/scrapy-scraper@v4.0

RUN playwright install --with-deps chromium

RUN git clone https://github.com/openvenues/libpostal \
	&& cd libpostal \
	&& ./bootstrap.sh && ./configure \
	&& make -j $(nproc) && make install \
	&& ldconfig \
	&& rm -rf libpostal

RUN curl -sSLf https://go.dev/dl/go1.25.0.linux-amd64.tar.gz -o go.tar.gz && tar -C /usr/local -xzf go.tar.gz && rm go.tar.gz \
	&& go install github.com/lc/gau/v2/cmd/gau@v2.2.4 \
	&& go install github.com/owasp-amass/amass/v5/cmd/amass@v5.0.1 \
	&& go install github.com/projectdiscovery/asnmap/cmd/asnmap@v1.1.1 \
	&& go install github.com/projectdiscovery/httpx/cmd/httpx@v1.8.1 \
	&& go install github.com/projectdiscovery/subfinder/v2/cmd/subfinder@v2.12.0 \
	&& go install github.com/projectdiscovery/uncover/cmd/uncover@v1.2.0 \
	&& go install github.com/utkusen/urlhunter@v0.2.0 \
	&& go install github.com/projectdiscovery/nuclei/v3/cmd/nuclei@v3.7.0

RUN nuclei -update-templates

RUN curl -sSLf https://sh.rustup.rs | sh -s -- -y --profile minimal --default-toolchain 1.93.1 && chmod -R a+w ${RUSTUP_HOME} ${CARGO_HOME} \
	&& cargo install feroxbuster --locked --version 2.13.1

RUN groupadd -r autorecon && useradd -r -m -d /home/autorecon -g autorecon autorecon
USER autorecon
WORKDIR /home/autorecon

CMD ["auto-recon", "--help"]
