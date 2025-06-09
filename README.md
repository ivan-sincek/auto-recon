# Auto Recon

This is my personal, custom-built OSINT framework, designed to streamline and automate various reconnaissance tasks.

This tool requires significant setup and configuration, so it likely won't work out of the box for you.

I plan to containerize the framework and provide a Docker image in the future.

The following information is being collected: [TXT files](https://github.com/ivan-sincek/auto-recon/blob/main/src/auto_recon/utils/config.py#L32) and [JSON files](https://github.com/ivan-sincek/auto-recon/blob/main/src/auto_recon/utils/config.py#L90).

The list of tools used can be found [here](https://github.com/ivan-sincek/auto-recon/blob/main/src/auto_recon/utils/config.py#L156).

## Table of Contents

* [How to Install](#how-to-install)
    * [Build and Install From the Source](#build-and-install-from-the-source)
* [Usage](#usage)
* [Images](#images)

## How to Install

### Build and Install From the Source

```bash
git clone https://github.com/ivan-sincek/auto-recon && cd auto-recon

python3 -m pip install --upgrade build

python3 -m build

python3 -m pip install dist/auto_recon-1.0-py3-none-any.whl
```

## Usage

```fundamental
Auto Recon v1.0 ( github.com/ivan-sincek/auto-recon )

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

<p align="center"><img src="https://github.com/ivan-sincek/auto-recon/blob/main/img/results.png" alt="Results"></p>

<p align="center">Figure 2 - Results</p>

<p align="center"><img src="https://github.com/ivan-sincek/auto-recon/blob/main/img/results_specific.png" alt="Results Specific"></p>

<p align="center">Figure 3 - Results Specific</p>
