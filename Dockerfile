FROM python:3.14-slim-bookworm

ENV DEBIAN_FRONTEND=noninteractive \
	AUTO_RECON_VERSION=1.0.0 \
	GO_VERSION=1.26.0 \
	RUST_VERSION=1.93.1 \
	PATH="/usr/local/go/bin:/usr/local/cargo/bin:${PATH}"

RUN apt update && apt install -y --no-install-recommends ca-certificates curl dnsutils nmap openssl

RUN curl -sSLf https://github.com/ivan-sincek/auto-recon/archive/refs/tags/v${AUTO_RECON_VERSION}.tar.gz -o auto-recon.tar.gz \
	&& tar -xzf auto-recon.tar.gz \
	&& rm auto-recon.tar.gz \
	&& python3 -m build auto-recon-* \
	&& python3 -m pip install --upgrade --no-cache-dir auto-recon-*/dist/auto_recon-*-py3-none-any.whl bot-safe-agents==1.1 forbidden==13.4 google-chad==7.4 scrapy-scraper==4.0 snallygaster==0.0.15 \
	&& rm -rf auto-recon-*

RUN curl -sSLf https://go.dev/dl/go${GO_VERSION}.linux-amd64.tar.gz -o go.linux-amd64.tar.gz \
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

RUN curl -sSLf https://sh.rustup.rs | sh -s -- -y --profile minimal --default-toolchain ${RUST_VERSION} \
	&& rustup default ${RUST_VERSION} \
	&& chmod -R a+w /usr/local/rustup /usr/local/cargo \
	&& cargo install feroxbuster --version 2.13.1

RUN groupadd -r autorecon && useradd -r -g autorecon autorecon
USER autorecon
WORKDIR /home/autorecon
