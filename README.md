# Auto Recon

A custom-built OSINT framework, which is designed to streamline and automate various reconnaissance tasks.

This tool requires significant setup and configuration and will likely not work out of the box unless you install the Docker image from [https://hub.docker.com](https://hub.docker.com).

The following information is collected:

* [TXT files](https://github.com/ivan-sincek/auto-recon/blob/main/src/auto_recon/utils/config.py#L32)
* [JSON files](https://github.com/ivan-sincek/auto-recon/blob/main/src/auto_recon/utils/config.py#L93)

The list of tools used can be found [here](https://github.com/ivan-sincek/auto-recon/blob/main/src/auto_recon/utils/config.py#L156).

## Table of Contents

* [How to Install](#how-to-install)
    * [Build and Install From Dockerfile](#build-and-install-from-dockerfile)
* [Usage](#usage)
* [Images](#images)

## How to Install

### Build and Install From Dockerfile

On Linux, run:

```fundamental
docker build --build-arg OS=linux --build-arg ARCH=amd64 -t autorecon:1.1.0 .
```

---

Windows OS is not supported.

---

On macOS, run:

```fundamental
docker build --build-arg OS=darwin --build-arg ARCH=arm64 -t autorecon:1.1.0 .
```

## Usage

```fundamental
Auto Recon v1.1.0 ( github.com/ivan-sincek/auto-recon )

Usage:   auto-recon -d domain      -o out     [-s subdomains    ] [-r resolvers    ] [-w wordlist    ]
Example: auto-recon -d example.com -o results [-s subdomains.txt] [-r resolvers.txt] [-w wordlist.txt]

DESCRIPTION
    Not another auto-reconnaissance framework
DOMAIN
    Fully qualified domain name to search
    -d, --domain = example.com | etc.
EXCLUSIONS
    File containing [wildcard] domains, subdomains, and IPs to exclude from the scope
    If restoring a session, the exclusions file from the output directory has priority over the specified file
    -e, --exclusions = exclusions.txt | etc.
NO FILTERING
    Do not limit the scope to the FQDN
    Exclusions are still being respected
    -nf, --no-filtering
SUBDOMAINS
    File containing subdomains to brute force DNS records
    -s, --subdomains = subdomains.txt | etc.
RESOLVERS
    File containing trusted DNS resolvers to resolve DNS records
    -r, --resolvers = resolvers.txt | etc.
WORDLIST
    Wordlist to brute force URL paths
    -w, --wordlist = wordlist.txt | etc.
COLLABORATOR
    Collaborator URL
    -c, --collaborator = https://xyz.interact.sh | https://xyz.burpcollaborator.net | etc.
THREADS
    Number of parallel tools to run per stage
    Default: 5
    -th, --threads = 10 | etc.
OUT
    Output directory
    -o, --out = results | etc.
RESTORE SESSION
    Restore the session from the last breakpoint
    -rs, --restore-session
```

## Images

<p align="center"><img src="https://github.com/ivan-sincek/auto-recon/blob/main/img/runtime.png" alt="Runtime"></p>

<p align="center">Figure 1 - Runtime</p>

<p align="center"><img src="https://github.com/ivan-sincek/auto-recon/blob/main/img/collected_results.png" alt="Collected Results"></p>

<p align="center">Figure 2 - Collected Results</p>

<p align="center"><img src="https://github.com/ivan-sincek/auto-recon/blob/main/img/specific_results_example.png" alt="Specific Results Example"></p>

<p align="center">Figure 3 - Specific Results Example</p>
