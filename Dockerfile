FROM python:3.14-slim-bookworm

ARG OS
ARG ARCH

RUN if [ "$OS" != "linux" ] && [ "$OS" != "darwin" ]; then \
	echo "Unsupported operating system: $OS"; \
	exit 1; \
	fi

RUN if [ "$ARCH" != "amd64" ] && [ "$ARCH" != "darwin64" ]; then \
	echo "Unsupported architecture: $ARCH"; \
	exit 1; \
	fi

ENV DEBIAN_FRONTEND=noninteractive \
	RUSTUP_HOME=/usr/local/rustup \
	CARGO_HOME=/usr/local/cargo \
	PATH="/usr/local/cargo/bin:/usr/local/go/bin:${PATH}"

WORKDIR /home/autorecon

RUN apt-get update && apt-get install -y --no-install-recommends \
	build-essential \
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

RUN python3 -m pip install --upgrade --no-cache-dir \
	pip build setuptools wheel \
	git+https://github.com/darkoperator/dnsrecon@1.5.3 \
	git+https://github.com/hannob/snallygaster@v0.0.15 \
	git+https://github.com/ivan-sincek/chad@v7.5 \
	git+https://github.com/ivan-sincek/forbidden@v13.4 \
	git+https://github.com/ivan-sincek/scrapy-scraper@v4.0 \
	git+https://github.com/laramies/theHarvester@4.10.0

RUN playwright install --with-deps chromium

RUN curl -sSLf https://sh.rustup.rs | sh -s -- -y --profile minimal --default-toolchain 1.93.1 \
	&& chmod -R a+w ${RUSTUP_HOME} ${CARGO_HOME} \
	&& cargo install feroxbuster --locked --version 2.13.1 \
	&& rm -rf ${CARGO_HOME}/git ${CARGO_HOME}/registry /root/.cargo

RUN curl -sSLf https://go.dev/dl/go1.25.0.${OS}-${ARCH}.tar.gz -o go.tar.gz \
	&& tar -C /usr/local -xzf go.tar.gz \
	&& rm go.tar.gz \
	&& curl -sSLf https://github.com/trufflesecurity/trufflehog/releases/download/v3.93.8/trufflehog_3.93.8_${OS}_${ARCH}.tar.gz -o trufflehog.tar.gz \
	&& tar -C /usr/local/bin -xzf trufflehog.tar.gz \
	&& chmod +x /usr/local/bin/trufflehog \
	&& rm trufflehog.tar.gz \
	&& go install github.com/lc/gau/v2/cmd/gau@v2.2.4 \
	&& go install github.com/owasp-amass/amass/v5/cmd/amass@v5.0.1 \
	&& go install github.com/utkusen/urlhunter@v0.2.0 \
	&& go install github.com/projectdiscovery/asnmap/cmd/asnmap@v1.1.1 \
	&& go install github.com/projectdiscovery/httpx/cmd/httpx@v1.8.1 \
	&& go install github.com/projectdiscovery/subfinder/v2/cmd/subfinder@v2.12.0 \
	&& go install github.com/projectdiscovery/uncover/cmd/uncover@v1.2.0 \
	&& go install github.com/projectdiscovery/nuclei/v3/cmd/nuclei@v3.7.0 \
	&& nuclei -update-templates

RUN apt-get purge -y --auto-remove build-essential git && apt-get autoremove -y && apt-get clean \
	&& rm -rf /root/.cache/* /tmp/* /var/cache/apt/* /var/lib/apt/lists/* /var/tmp/*

RUN groupadd -r autorecon && useradd -r -m -d /home/autorecon -g autorecon autorecon
USER autorecon
WORKDIR /home/autorecon

CMD ["auto-recon", "--help"]
