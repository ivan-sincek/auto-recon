FROM python:3.14-slim-bookworm

ENV DEBIAN_FRONTEND=noninteractive \
	JDK_VERSION=17 \
	GO_VERSION=1.26.0 \
	RUST_VERSION=1.93.1 \
	PATH="/usr/local/go/bin:/usr/local/cargo/bin:${PATH}"

RUN apt update && apt install -y --no-install-recommends ca-certificates curl dnsutils libimage-exiftool-perl nmap openjdk-${JDK_VERSION}-jdk-headless openssl sslscan

RUN curl -sSLf https://github.com/ivan-sincek/auto-recon/archive/refs/tags/v1.0.0.tar.gz -o auto-recon.tar.gz \
	&& tar -xzf auto-recon.tar.gz \
	&& rm auto-recon.tar.gz \
	&& python3 -m build auto-recon-* \
	&& python3 -m pip install --upgrade --no-cache-dir auto-recon-*/dist/auto_recon-*-py3-none-any.whl \
	&& rm -rf auto-recon-* \
	curl -sSLf https://github.com/laramies/theHarvester/archive/refs/tags/4.10.0.tar.gz -o theHarvester.tar.gz \
	&& tar -xzf theHarvester.tar.gz \
	&& rm theHarvester.tar.gz \
	&& python3 -m build theHarvester-* \
	&& python3 -m pip install --upgrade --no-cache-dir theHarvester-*/dist/auto_recon-*-py3-none-any.whl \
	&& rm -rf theHarvester-* \
	curl -sSLf https://github.com/darkoperator/dnsrecon/archive/refs/tags/1.6.0.tar.gz -o dnsrecon.tar.gz \
	&& tar -xzf dnsrecon.tar.gz \
	&& rm dnsrecon.tar.gz \
	&& python3 -m build dnsrecon-* \
	&& python3 -m pip install --upgrade --no-cache-dir dnsrecon-*/dist/auto_recon-*-py3-none-any.whl \
	&& rm -rf dnsrecon-*

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

CMD ["auto-recon --help"]
