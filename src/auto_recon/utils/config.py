#!/usr/bin/env python3

import dataclasses, enum

APP_VERSION = "v1.0"

HEADING = f"Auto Recon {APP_VERSION} ( github.com/ivan-sincek/auto-recon )"

# ----------------------------------------

class Directory(enum.Enum):
	"""
	Enum containing directory keys.\n
	Edit or add more directories here.
	"""
	CONFIG = "config"
	TOOLS  = "tools"
	LOGS   = "logs"

# ----------------------------------------

class Wordlist(enum.Enum):
	"""
	Enum containing wordlist keys.\n
	Edit or add more wordlists here.
	"""
	LEAKY_PATHS                      = "leaky_paths"
	RAFT_SMALL_DIRECTORIES_LOWERCASE = "raft_small_directories_lowercase"

# ----------------------------------------

class TXT(enum.Enum):
	"""
	Enum containing TXT file keys.\n
	Edit or add more TXT files here.
	"""
	CERT_OPENSSL_HEARTBLEED     = "cert_openssl_heartbleed"
	CERT_SUBJECT_COMMON_NAME    = "cert_subject_common_name"
	CNAME                       = "cname"
	CSP                         = "csp"
	DIRECTORY                   = "directory"
	DIRECTORY_2XX               = "directory_2xx"
	DIRECTORY_2XX_4XX           = "directory_2xx_4xx"
	DIRECTORY_3XX               = "directory_3xx"
	DIRECTORY_401               = "directory_401"
	DIRECTORY_403               = "directory_403"
	DIRECTORY_LISTING           = "directory_listing"
	DIRECTORY_SENSITIVE         = "directory_sensitive"
	DNS_MAIL_EXCHANGE           = "dns_mail_exchange"
	DNS_NAME_SERVER             = "dns_name_server"
	DNS_TEXT                    = "dns_text"
	IP                          = "ip"
	IP_BROKEN                   = "ip_broken"
	IP_SUBDOMAIN                = "ip_subdomain"
	IP_SUBDOMAIN_LIVE           = "ip_subdomain_live"
	LEAKY_PATHS                 = "leaky_paths"
	LEAKY_PATHS_2XX             = "leaky_paths_2xx"
	LEAKY_PATHS_2XX_4XX         = "leaky_paths_2xx_4xx"
	LEAKY_PATHS_3XX             = "leaky_paths_3xx"
	LEAKY_PATHS_401             = "leaky_paths_401"
	LEAKY_PATHS_403             = "leaky_paths_403"
	META_EMAIL                  = "meta_email"
	META_PEOPLE                 = "meta_people"
	SUBDOMAIN                   = "subdomain"
	SUBDOMAIN_BROKEN            = "subdomain_broken"
	SUBDOMAIN_ERROR             = "subdomain_error"
	LINK                        = "link"
	SECRET                      = "secret"
	SUBDOMAIN_LIVE              = "subdomain_live"
	SUBDOMAIN_LIVE_LONG         = "subdomain_live_long"
	SUBDOMAIN_LIVE_LONG_2XX     = "subdomain_live_long_2xx"
	SUBDOMAIN_LIVE_LONG_2XX_4XX = "subdomain_live_long_2xx_4xx"
	SUBDOMAIN_LIVE_LONG_3XX     = "subdomain_live_long_3xx"
	SUBDOMAIN_LIVE_LONG_401     = "subdomain_live_long_401"
	SUBDOMAIN_LIVE_LONG_403     = "subdomain_live_long_403"
	SUBDOMAIN_LIVE_LONG_4XX     = "subdomain_live_long_4xx"
	SUBDOMAIN_LIVE_LONG_5XX     = "subdomain_live_long_5xx"
	SUBDOMAIN_LIVE_LONG_HTTP    = "subdomain_live_long_http"
	SUBDOMAIN_LIVE_LONG_HTTPS   = "subdomain_live_long_https"
	SUBDOMAIN_LIVE_SHORT        = "subdomain_live_short"
	SUBDOMAIN_LIVE_SHORT_HTTP   = "subdomain_live_short_http"
	SUBDOMAIN_LIVE_SHORT_HTTPS  = "subdomain_live_short_https"
	URL                         = "url"
	WHOIS_ASN                   = "whois_asn"
	WHOIS_CIDR                  = "whois_cidr"
	WHOIS_ORG                   = "whois_org"

# ----------------------------------------

class JSON(enum.Enum):
	"""
	Enum containing JSON file keys.\n
	Edit or add more JSON files here.
	"""
	CERT_SUBJECT_COMMON_NAME_TO_IP = "cert_subject_common_name_to_ip"
	IP_TO_SUBDOMAIN                = "ip_to_subdomain"
	IP_TO_WHOIS_ASN                = "ip_to_whois_asn"
	SUBDOMAIN_ERROR_TO_CNAME       = "subdomain_error_to_cname"
	SUBDOMAIN_TO_CERT              = "subdomain_to_cert"
	SUBDOMAIN_TO_CNAME             = "subdomain_to_cname"
	SUBDOMAIN_TO_CSP               = "subdomain_to_csp"
	SUBDOMAIN_TO_IP                = "subdomain_to_ip"
	SUBDOMAIN_TO_STATUS            = "subdomain_to_status"

# ----------------------------------------

class DNS(enum.Enum):
	"""
	Enum containing DNS query keys.\n
	Edit or add more DNS queries here.
	"""
	A     = "A"
	AAAA  = "AAAA"
	CNAME = "CNAME"
	MX    = "MX"
	NS    = "NS"
	PTR   = "PTR"
	SRV   = "SRV"
	TXT   = "TXT"

# ----------------------------------------

class Intrusive(str, enum.Enum):
	"""
	Enum containing intrusiveness Levels.
	"""
	NOT    = ""
	LOW    = "low"
	MEDIUM = "medium"
	HIGH   = "high"

@dataclasses.dataclass
class Tool:
	"""
	Class for storing tool details.\n
	Use 'args' attribute to specify additional arguments for the tool.
	"""
	name     : str
	args     : dict[str | int | float] = dataclasses.field(default_factory = dict)
	active   : bool                    = False
	intrusive: Intrusive               = Intrusive.NOT

# ----------------------------------------

THREADS_LOW    = 5
THREADS_MEDIUM = 15
THREADS_HIGH   = 30

TIMEOUT_LOW    = 5
TIMEOUT_MEDIUM = 15
TIMEOUT_HIGH   = 30

RETRIES_MIN = 1
RETRIES_MAX = 3

RUNTIME = {
	"S-01": [
		Tool(
			name = "chad",
			args = {"total": 200, "min_queries": 120, "max_queries": 200, "min_pages": 25, "max_pages": 45, "threads": THREADS_MEDIUM}
		),
		Tool(
			name = "theharvester",
			args = {"total": 200}
		),
		Tool(
			name = "assetfinder"
		),
		Tool(
			name = "subfinder",
			args = {"threads": THREADS_MEDIUM, "timeout": TIMEOUT_HIGH}
		),
		Tool(
			name = "amass"
		)
	],
	"S-02": [
		Tool(
			name = "dnsrecon",
			args = {"threads": THREADS_HIGH, "timeout": TIMEOUT_LOW},
			intrusive = Intrusive.LOW
		)
	],
	"S-03": [
		Tool(
			name = "dig",
			args = {"threads": THREADS_HIGH, "timeout": TIMEOUT_LOW}
		)
	],
	"S-04": [
		Tool(
			name = "host",
			args = {"threads": THREADS_HIGH, "timeout": TIMEOUT_LOW}
		)
	],
	"S-05": [
		Tool(
			name = "httpx",
			args = {"threads": THREADS_HIGH, "timeout": TIMEOUT_MEDIUM, "retries": RETRIES_MIN},
			active = True
		)
	],
	"S-06": [
		Tool(
			name = "cleanup"
		)
	],
	"S-07": [
		Tool(
			name = "eyewitness",
			args = {"threads": THREADS_LOW, "timeout": TIMEOUT_MEDIUM, "retries": RETRIES_MIN},
			active = True
		),
		Tool(
			name = "getallurls",
			args = {"threads": THREADS_LOW, "retries": RETRIES_MAX}
		),
		Tool(
			name = "asnmap",
			args = {"threads": THREADS_LOW}
		),
		Tool(
			name = "openssl",
			args = {"threads": THREADS_LOW},
			active = True
		),
		Tool(
			name = "keytool",
			args = {"threads": THREADS_LOW},
			active = True
		),
		Tool(
			name = "sslscan",
			args = {"threads": THREADS_LOW, "connect_timeout": TIMEOUT_HIGH, "timeout": TIMEOUT_LOW},
			active = True
		),
		Tool(
			name = "scrapy_scraper",
			args = {"rate_limit": 150, "threads": THREADS_LOW, "timeout": TIMEOUT_MEDIUM, "retries": RETRIES_MIN},
			active = True,
			intrusive = Intrusive.LOW
		)
	],
	"S-08": [
		Tool(
			name = "uncover",
			args = {"total": 200, "threads": THREADS_LOW, "timeout": TIMEOUT_HIGH, "retries": RETRIES_MIN}
		),
		Tool(
			name = "snallygaster",
			args = {"threads": THREADS_MEDIUM},
			active = True,
			intrusive = Intrusive.LOW
		),
		Tool(
			name = "trufflehog",
			args = {"threads": THREADS_MEDIUM},
		)
	],
	"S-09": [
		Tool(
			name = "leaky_paths",
			args = {"threads": THREADS_HIGH, "subthreads": THREADS_MEDIUM, "timeout": TIMEOUT_MEDIUM},
			active = True,
			intrusive = Intrusive.HIGH
		)
	],
	"S-10": [
		Tool(
			name = "urlhunter"
		)
	],
	"S-11": [
		Tool(
			name = "feroxbuster",
			args = {"threads": THREADS_HIGH, "subthreads": THREADS_MEDIUM, "timeout": TIMEOUT_MEDIUM},
			active = True,
			intrusive = Intrusive.HIGH
		)
	],
	"S-12": [
		Tool(
			name = "nmap",
			active = True,
			intrusive = Intrusive.MEDIUM
		)
	],
	"S-13": [
		Tool(
			name = "forbidden",
			args = {"threads": THREADS_HIGH, "subthreads": THREADS_MEDIUM, "timeout": TIMEOUT_MEDIUM},
			active = True,
			intrusive = Intrusive.HIGH
		)
	],
	"S-14": [
		Tool(
			name = "nuclei",
			args = {"threads": THREADS_HIGH, "subthreads": THREADS_MEDIUM, "timeout": TIMEOUT_MEDIUM, "retries": RETRIES_MIN},
			active = True,
			intrusive = Intrusive.HIGH
		)
	],
	"S-15": [
		Tool(
			name = "cleanup"
		)
	]
}
