#!/usr/bin/env python3

from . import array as __array, config, debug, exclusion, file as __file, grep, ip, jquery, url

'''
def remove_www(text: str):
    """
    Remove the first match from a text using the '^www\.|(?<=\:\/\/)www\.' RegEx pattern.
    """
    return grep.replace(text, r"^www\.|(?<=\:\/\/)www\.", "", 1)

def remove_www_array(text_array: list[str], sort=True):
    """
    Remove the first match from each string in a text array using the '^www\.|(?<=\:\/\/)www\.' RegEx pattern.\n
    Returns a unique [sorted] list.
    """
    tmp = []
    for entry in text_array:
        entry = remove_www(entry)
        if entry:
            tmp.append(entry)
    return __array.unique(tmp, sort)
'''

def remove_wildcards(text: str):
    """
    Remove wildcards and other irregularities from a text.
    """
    text = grep.replace(text, r"\*|\@")
    text = grep.replace(text, r"\.{2,}", ".")
    text = grep.replace(text, r"^\.|(?<=\:\/\/)\.|\.(?=\:)|\.$")
    return text

def remove_wildcards_array(text_array: list[str], sort=True):
    """
    Remove wildcards and other irregularities from each string in a text array.\n
    Returns a unique [sorted] list.
    """
    tmp = []
    for entry in text_array:
        entry = remove_wildcards(entry)
        if entry:
            tmp.append(entry)
    return __array.unique(tmp, sort)

def prepend_asn(text: str):
    """
    Convert text to uppercase and prepend a missing 'AS' prefix.\n
    In other words, normalize ASN numbers.
    """
    text = text.upper()
    if not text.startswith("AS"):
        text = f"AS{text}"
    return text

def prepend_asn_array(text_array: list[str], sort=True):
    """
    Convert each string in a text array to uppercase and prepend a missing 'AS' prefix.\n
    In other words, normalize ASN numbers.\n
    Returns a unique [sorted] list.
    """
    tmp = []
    for entry in text_array:
        tmp.append(prepend_asn(entry))
    return __array.unique(tmp, sort)

def __insert_or_remove(file: __file.SafeFile, array: list[str]):
    """
    Write an array to a file, or remove the file if the array is empty.
    """
    if array:
        __file.insert(__array.unique(array), file)
    else:
        __file.remove_silent(file.path)

# ----------------------------------------

def subdomains(key: config.TXT):
    """
    Filter subdomains.
    """
    valid, invalid, broken, ignored = [], [], [], []; safe_file = __file.file.get(key)
    for entry in __file.read(safe_file):
        if remove_wildcards(entry) != entry:
            broken.append(entry)
        elif not (fqdn := url.extract_fqdn(entry)):
            invalid.append(entry)
        elif not grep.search(fqdn, exclusion.exclusion.get(exclusion.RegEx.SUBDOMAIN)):
            ignored.append(entry)
        else:
            valid.append(entry)
    # ------------------------------------
    __insert_or_remove(safe_file, valid)
    # ------------------------------------
    if broken:
        __file.append(broken, __file.file.get(config.TXT.SUBDOMAIN_BROKEN))
    if invalid:
        debug.debug.log_filter(f"utils.filter.subdomains() > {safe_file.path}", f"Invalid subdomains:\n{chr(10).join(__array.unique(invalid))}")
    if ignored:
        debug.debug.log_filter(f"utils.filter.subdomains() > {safe_file.path}", f"Ignored subdomains:\n{chr(10).join(__array.unique(ignored))}")

def ports(key: config.TXT, port_ignore: int, port_keep: int):
    """
    Filter ports.
    """
    valid, invalid, ignored = [], [], []; safe_file = __file.file.get(key); text = __file.read(safe_file, array=False)
    for entry in __file.read(safe_file):
        domain, port = url.extract_netloc(entry)
        if not domain or not port:
            invalid.append(entry)
        elif port == port_ignore and grep.search(text, f"{domain}:{port_keep}"):
            ignored.append(entry)
        else:
            valid.append(entry)
    # ------------------------------------
    __insert_or_remove(safe_file, valid)
    # ------------------------------------
    if invalid:
        debug.debug.log_filter(f"utils.filter.ports() > {safe_file.path}", f"Invalid subdomains:\n{chr(10).join(__array.unique(invalid))}")
    if ignored:
        debug.debug.log_filter(f"utils.filter.ports() > {safe_file.path}", f"Redundant ports:\n{chr(10).join(__array.unique(ignored))}")

def ips(key: config.TXT):
    """
    Filter IPs.
    """
    valid, invalid, broken, ignored = [], [], [], []
    safe_file = __file.file.get(key)
    for entry in __file.read(safe_file):
        if remove_wildcards(entry) != entry:
            broken.append(entry)
        elif not ip.validate_silent(entry):
            invalid.append(entry)
        elif not grep.search(entry, exclusion.exclusion.get(exclusion.RegEx.IP)):
            ignored.append(entry)
        else:
            valid.append(entry)
    # ------------------------------------
    __insert_or_remove(safe_file, valid)
    # ------------------------------------
    if broken:
        __file.append(broken, __file.file.get(config.TXT.IP_BROKEN))
    if invalid:
        debug.debug.log_filter(f"utils.filter.ips() > {safe_file.path}", f"Invalid IPs:\n{chr(10).join(__array.unique(invalid))}")
    if ignored:
        debug.debug.log_filter(f"utils.filter.ips() > {safe_file.path}", f"Ignored IPs:\n{chr(10).join(__array.unique(ignored))}")

def emails(key: config.TXT):
    """
    Filter emails.
    """
    valid, ignored = [], []; safe_file = __file.file.get(key)
    for entry in __file.read(safe_file):
        if not grep.search(entry, exclusion.exclusion.get(exclusion.RegEx.EMAIL)):
            ignored.append(entry)
        else:
            valid.append(entry)
    # ------------------------------------
    __insert_or_remove(safe_file, valid)
    # ------------------------------------
    if ignored:
        debug.debug.log_filter(f"utils.filter.emails() > {safe_file.path}", f"Ignored emails:\n{chr(10).join(__array.unique(ignored))}")

def asns(key: config.TXT):
    """
    Filter ASNs.
    """
    safe_file = __file.file.get(key)
    __file.insert(prepend_asn_array(__file.read(safe_file)), safe_file)

# ----------------------------------------

SUBDOMAIN_KEYS = {
    config.TXT.SUBDOMAIN,
    config.TXT.SUBDOMAIN_ERROR,
    config.TXT.SUBDOMAIN_LIVE,
    config.TXT.SUBDOMAIN_LIVE_LONG,
    config.TXT.SUBDOMAIN_LIVE_LONG_2XX,
    config.TXT.SUBDOMAIN_LIVE_LONG_2XX_4XX,
    config.TXT.SUBDOMAIN_LIVE_LONG_3XX,
    config.TXT.SUBDOMAIN_LIVE_LONG_401,
    config.TXT.SUBDOMAIN_LIVE_LONG_403,
    config.TXT.SUBDOMAIN_LIVE_LONG_4XX,
    config.TXT.SUBDOMAIN_LIVE_LONG_5XX,
    config.TXT.SUBDOMAIN_LIVE_LONG_HTTP,
    config.TXT.SUBDOMAIN_LIVE_LONG_HTTPS,
    config.TXT.SUBDOMAIN_LIVE_SHORT,
    config.TXT.SUBDOMAIN_LIVE_SHORT_HTTP,
    config.TXT.SUBDOMAIN_LIVE_SHORT_HTTPS,
}
PORT_KEYS = SUBDOMAIN_KEYS - {
    config.TXT.SUBDOMAIN,
    config.TXT.SUBDOMAIN_ERROR,
    config.TXT.SUBDOMAIN_LIVE
}
IP_KEYS = {
    config.TXT.IP
}
EMAIL_KEYS = {
    config.TXT.META_EMAIL
}
ASN_KEYS = {
    config.TXT.WHOIS_ASN
}

def files():
    """
    Filter all files.
    """
    for key in list(config.TXT) + list(config.JSON):
        file(key)

def file(key: config.TXT | config.JSON):
    """
    Filter a file.
    """
    if isinstance(key, config.TXT):
        # --------------------------------
        if key in SUBDOMAIN_KEYS:
            subdomains(key)
            if key in PORT_KEYS:
                ports(key, 80, 443)
            return
        # --------------------------------
        if key in IP_KEYS:
            ips(key)
            return
        # --------------------------------
        if key in EMAIL_KEYS:
            emails(key)
            return
        # --------------------------------
        if key in ASN_KEYS:
            asns(key)
            return
        # --------------------------------
        safe_file = __file.file.get(key)
        __file.insert(__array.unique(__file.read(safe_file)), safe_file)
        # --------------------------------
    elif isinstance(key, config.JSON):
        # --------------------------------
        safe_file = __file.file.get(key)
        data = jquery.jload(safe_file)
        keys = jquery.find(data, ".[0] | keys_unsorted[0]", sort=False)
        if not keys:
            __file.remove_silent(safe_file.path)
        else:
            jquery.find_insert_file(data, safe_file, f"unique_by(.{keys[0]}) | sort_by(.{keys[0]}) | reverse | .[]", sort=False, dump=True)
        # --------------------------------
