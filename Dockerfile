FROM python:3.14-slim-bookworm

ENV DEBIAN_FRONTEND=noninteractive \
	PATH="/usr/local/go/bin:/usr/local/cargo/bin:${PATH}"

WORKDIR /home/autorecon

RUN apt-get update && apt-get install -y --no-install-recommends \
	ca-certificates \
	curl \
	dnsutils \
	git \
	libcurl4-gnutls-dev \
	libimage-exiftool-perl \
	librtmp-dev \
	nmap \
	openjdk-17-jdk-headless \
	openssl \
	sslscan \
	&& rm -rf /var/lib/apt/lists/*

RUN python3 -m pip install --no-cache-dir --upgrade \
	pip \
	buil \
	setuptools \
	wheel \
	git+https://github.com/ivan-sincek/auto-recon@v1.0.0 \
	git+https://github.com/darkoperator/dnsrecon@1.6.0 \
	git+https://github.com/laramies/theHarvester@4.10.0

RUN curl -sSLf https://go.dev/dl/go1.26.0.linux-amd64.tar.gz -o go.linux-amd64.tar.gz \
	&& tar -C /usr/local -xzf go.linux-amd64.tar.gz \
	&& rm go.linux-amd64.tar.gz \
	&& go install github.com/lc/gau/v2/cmd/gau@v2.2.4 \
	&& go install github.com/owasp-amass/amass/v5/cmd/amass@v5.0.1 \
	&& go install github.com/projectdiscovery/asnmap/cmd/asnmap@v1.1.1 \
	&& go install github.com/projectdiscovery/httpx/cmd/httpx@v1.8.1 \
	&& go install github.com/projectdiscovery/nuclei/v3/cmd/nuclei@v3.7.0 \
	&& go install github.com/projectdiscovery/subfinder/v2/cmd/subfinder@v2.12.0 \
	&& go install github.com/projectdiscovery/uncover/cmd/uncover@v1.2.0 \
	&& go install github.com/trufflesecurity/trufflehog/v3@v3.93.6 \
	&& go install github.com/utkusen/urlhunter@v0.2.0

RUN curl -sSLf https://sh.rustup.rs | sh -s -- -y --profile minimal --default-toolchain 1.93.1 \
	&& rustup default 1.93.1 \
	&& chmod -R a+w /usr/local/rustup /usr/local/cargo \
	&& cargo install feroxbuster --version 2.13.1

RUN groupadd -r autorecon && useradd -r -g autorecon autorecon
USER autorecon

CMD ["auto-recon", "--help"]
