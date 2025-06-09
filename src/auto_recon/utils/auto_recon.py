#!/usr/bin/env python3

from . import cert, config, debug, directory, exclusion, file, filter, general, grep, jquery, run, session, wordlist

import argparse, concurrent.futures, os

class AutoRecon:

	def __init__(self, args: argparse.Namespace):
		"""
		Initialize a class for managing the main tool.
		"""
		self.__args = args

	def setup(self):
		"""
		Setup the main tool.
		"""
		success = True
		message = ""
		directory.directory.initialize(self.__args.out)
		success, message = directory.directory.setup()
		if success:
			debug.debug.initialize(self.__args.out)
			session.session.initialize(self.__args.out)
			success, message = session.session.restore() if self.__args.restore_session else session.session.new()
			if success:
				file.file.initialize(self.__args.out)
				exclusion.exclusion.initialize(self.__args.out, self.__args.exclusions, "" if self.__args.no_filtering else self.__args.domain)
		return success, message

	def run(self):
		"""
		Run the main tool.
		"""
		with concurrent.futures.ThreadPoolExecutor(max_workers = self.__args.threads) as executor:
			try:
				for stage in session.session.get_stages():
					subprocesses = []
					for tool in session.session.get_stage_tools(stage):
						subprocesses.append(executor.submit(getattr(self, tool.base.name), tool))
					for subprocess in concurrent.futures.as_completed(subprocesses):
						identifier: int = subprocess.result()
						session.session.update(identifier, completed = True)
			except KeyboardInterrupt:
				executor.shutdown(wait = False, cancel_futures = True)

	# ------------------------------------

	def chad(self, tool: session.Tool):
		session.session.update(tool.identifier)
		# --------------------------------
		out   = directory.directory.init_tools_file("chad_subdomain", "json")
		query = f"site:*.{self.__args.domain} -www"
		run.single(
			cmd = [
				"chad -nsos -a random",
				run.set_opt(tool.base.args["total"      ], "-tr"   ),
				run.set_opt(tool.base.args["min_queries"], "-min-q"),
				run.set_opt(tool.base.args["max_queries"], "-max-q"),
				run.set_opt(tool.base.args["min_pages"  ], "-min-p"),
				run.set_opt(tool.base.args["max_pages"  ], "-max-p"),
				run.set_opt(query                        , "-q"    ),
				run.set_opt(out.path                     , "-o"    )
			]
		)
		urls = ("\n").join(jquery.find(jquery.jload(out), '.[].urls[]'))
		grep.find_append_file(urls, file.file.get(config.TXT.SUBDOMAIN), r"(?<=\:\/\/)[^\s\:\/\?\&\#\%]+")
		# --------------------------------
		dir   = directory.directory.init_tools_subdirectory("chad_download")
		out   = directory.directory.init_tools_file("chad_download", "json")
		query = f"*.{self.__args.domain} {(' OR ').join(f'ext:{ext}' for ext in ['txt', 'json', 'yml', 'pdf', 'doc', 'docx', 'xls', 'xlsx', 'zip', 'tar', 'rar', 'gzip', '7z'])}"
		run.single(
			cmd = [
				"chad -a random",
				run.set_opt(tool.base.args["total"      ], "-tr"   ),
				run.set_opt(tool.base.args["min_queries"], "-min-q"),
				run.set_opt(tool.base.args["max_queries"], "-max-q"),
				run.set_opt(tool.base.args["min_pages"  ], "-min-p"),
				run.set_opt(tool.base.args["max_pages"  ], "-max-p"),
				run.set_opt(tool.base.args["threads"    ], "-th"   ),
				run.set_opt(query                        , "-q"    ),
				run.set_opt(out.path                     , "-o"    ),
				run.set_opt(dir                          , "-dir"  )
			]
		)
		if directory.listdir(dir):
			out = directory.directory.init_tools_file("chad_download_exiftool")
			run.single(
				out = out,
				cmd = [
					"exiftool -S",
					run.set_opt(dir)
				]
			)
			result = file.read(out, array = False)
			grep.find_append_file(result, file.file.get(config.TXT.META_PEOPLE), r"(?<=Author\:\ ).+")
		# --------------------------------
		out   = directory.directory.init_tools_file("chad_directory_listing", "json")
		query = f'site:*.{self.__args.domain} intitle:"index of /" intext:"parent directory"'
		run.single(
			cmd = [
				"chad -a random",
				run.set_opt(tool.base.args["total"      ], "-tr"   ),
				run.set_opt(tool.base.args["min_queries"], "-min-q"),
				run.set_opt(tool.base.args["max_queries"], "-max-q"),
				run.set_opt(tool.base.args["min_pages"  ], "-min-p"),
				run.set_opt(tool.base.args["max_pages"  ], "-max-p"),
				run.set_opt(query                        , "-q"    ),
				run.set_opt(out.path                     , "-o"    )
			]
		)
		urls = jquery.find(jquery.jload(out), '.[].urls[]')
		file.append(urls, file.file.get(config.TXT.DIRECTORY_LISTING))
		# --------------------------------
		return tool.identifier

	def theharvester(self, tool: session.Tool):
		session.session.update(tool.identifier)
		# --------------------------------
		out = directory.directory.init_tools_file("theharvester", "json")
		run.single(
			cmd = [
				"theHarvester -b baidu,brave,certspotter,crtsh,dnsdumpster,duckduckgo,hackertarget,otx,rapiddns,sitedossier,subdomaincenter,subdomainfinderc99,threatminer,urlscan,virustotal,yahoo",
				run.set_opt(tool.base.args["total"], "-l"),
				run.set_opt(self.__args.resolvers  , "-r"),
				run.set_opt(self.__args.domain     , "-d"),
				run.set_opt(out.path               , "-f")
			]
		)
		res = jquery.jload(out)
		jquery.find_append_file(res, file.file.get(config.TXT.IP        ), '.ips    // empty | .[]                                              ')
		jquery.find_append_file(res, file.file.get(config.TXT.IP        ), '.hosts  // empty | .[] | select(contains(":")      ) | split(":")[1]')
		jquery.find_append_file(res, file.file.get(config.TXT.META_EMAIL), '.emails // empty | .[]                                              ')
		jquery.find_append_file(res, file.file.get(config.TXT.SUBDOMAIN ), '.hosts  // empty | .[] | select(contains(":") | not)                ')
		jquery.find_append_file(res, file.file.get(config.TXT.SUBDOMAIN ), '.hosts  // empty | .[] | select(contains(":")      ) | split(":")[0]')
		"""
		jquery.find_append_file(res, file.file.get(config.TXT.WHOIS_ASN ), '.asns   // empty | .[]                                              ')
		"""
		# --------------------------------
		return tool.identifier

	def assetfinder(self, tool: session.Tool):
		session.session.update(tool.identifier)
		# --------------------------------
		out = directory.directory.init_tools_file("assetfinder")
		run.single(
			out = out,
			cmd = [
				"assetfinder --subs-only",
				run.set_opt(self.__args.domain)
			]
		)
		file.copy_append(out, file.file.get(config.TXT.SUBDOMAIN))
		# --------------------------------
		return tool.identifier

	def subfinder(self, tool: session.Tool):
		session.session.update(tool.identifier)
		# --------------------------------
		out = directory.directory.init_tools_file("subfinder")
		run.single(
			cmd = [
				"subfinder -silent -nc -all -nW",
				run.set_opt(tool.base.args["threads"], "-t"      ),
				run.set_opt(tool.base.args["timeout"], "-timeout"),
				run.set_opt(self.__args.resolvers    , "-rL"     ),
				run.set_opt(self.__args.domain       , "-d"      ),
				run.set_opt(out.path                 , "-o"      )
			]
		)
		file.copy_append(out, file.file.get(config.TXT.SUBDOMAIN))
		# --------------------------------
		return tool.identifier

	def amass(self, tool: session.Tool):
		session.session.update(tool.identifier)
		# --------------------------------
		out = directory.directory.init_tools_file("amass")
		run.single(
			cmd = [
				"amass enum -silent -nocolor",
				run.set_opt(self.__args.resolvers, "-trf"),
				run.set_opt(self.__args.domain   , "-d"  ),
				run.set_opt(out.path             , "-o"  )
			]
		)
		res = file.read(out, array = False)
		grep.find_append_file(res, file.file.get(config.TXT.CNAME            ), r"(?<=cname_record\ \-\-\>\ )[^\s]+"                       )
		grep.find_append_file(res, file.file.get(config.TXT.DNS_MAIL_EXCHANGE), r"(?<=mx_record\ \-\-\>\ )[^\s]+"                          )
		grep.find_append_file(res, file.file.get(config.TXT.DNS_NAME_SERVER  ), r"(?<=ns_record\ \-\-\>\ )[^\s]+"                          )
		grep.find_append_file(res, file.file.get(config.TXT.IP               ), r"(?<=(?:a_record|contains)\ \-\-\>\ )[^\s]+"              )
		grep.find_append_file(res, file.file.get(config.TXT.SUBDOMAIN        ), r"^[^\s]+(?=\ \(FQDN\))"                                   )
		grep.find_append_file(res, file.file.get(config.TXT.SUBDOMAIN        ), r"(?<=ptr_record\ \-\-\>\ )[^\s]+"                         )
		"""
		grep.find_append_file(res, file.file.get(config.TXT.WHOIS_ASN        ), r"^\d+(?=\ \(ASN\))"                                       )
		grep.find_append_file(res, file.file.get(config.TXT.WHOIS_CIDR       ), r"^[^\s]+(?=\ \(Netblock\))|(?<=announces\ \-\-\>\ )[^\s]+")
		"""
		# --------------------------------
		return tool.identifier

	def dnsrecon(self, tool: session.Tool):
		session.session.update(tool.identifier)
		# --------------------------------
		if not self.__dnsrecon_axfr(tool):
			self.__dnsrecon_std(tool)
			self.__dnsrecon_brt(tool)
		# --------------------------------
		return tool.identifier

	def __dnsrecon_axfr(self, tool: session.Tool):
		out = directory.directory.init_tools_file("dnsrecon_axfr", "json")
		run.single(
			cmd = [
				"dnsrecon -t axfr",
				run.set_opt(tool.base.args["threads"], "--threads" ),
				run.set_opt(tool.base.args["timeout"], "--lifetime"),
				run.set_opt(self.__args.domain       , "-d"        ),
				run.set_opt(out.path                 , "-j"        )
			]
		)
		if zone_transfer := bool(jquery.find(jquery.jload(out), 'select(.[].zone_transfer == "success")')):
			self.__dnsrecon_parse_result(out)
		return zone_transfer

	def __dnsrecon_std(self, tool: session.Tool):
		out = directory.directory.init_tools_file("dnsrecon_std", "json")
		run.single(
			cmd = [
				"dnsrecon -t std",
				run.set_opt(tool.base.args["threads"], "--threads" ),
				run.set_opt(tool.base.args["timeout"], "--lifetime"),
				run.set_opt(self.__args.domain       , "-d"        ),
				run.set_opt(out.path                 , "-j"        )
			]
		)
		self.__dnsrecon_parse_result(out)

	def __dnsrecon_brt(self, tool: session.Tool):
		if self.__args.subdomains:
			out = directory.directory.init_tools_file("dnsrecon_brt", "json")
			res = run.single(
				cmd = [
					"dnsrecon -t brt --iw -f",
					run.set_opt(tool.base.args["threads"], "--threads" ),
					run.set_opt(tool.base.args["timeout"], "--lifetime"),
					run.set_opt(self.__args.subdomains   , "-D"        ),
					run.set_opt(self.__args.domain       , "-d"        ),
					run.set_opt(out.path                 , "-j"        )
				]
			)
			exclusion.exclusion.update(grep.find(res.response, r"(?<=It\ is\ resolving\ to\ )[^\s]+"))
			# NOTE: Excludes any IP address that appears more than 100 times.
			exclusion.exclusion.update(jquery.find(jquery.jload(out), 'group_by(.address) | map({address: .[0].address, count: length}) | map(select(.count > 100)) | .[].address'))
			self.__dnsrecon_parse_result(out)

	def __dnsrecon_parse_result(self, out: file.SafeFile | str):
		res = jquery.find(jquery.jload(out), exclusion.exclusion.get(exclusion.JQ.DNSRECON)) if exclusion.exclusion.should_filter() else jquery.jload(out)
		jquery.find_append_file(res, file.file.get(config.TXT.DNS_MAIL_EXCHANGE), '.[] | select(.type | test("^MX$"             )) | .exchange // empty                  ')
		jquery.find_append_file(res, file.file.get(config.TXT.DNS_NAME_SERVER  ), '.[] | select(.type | test("^NS$"             )) | .target   // empty                  ')
		jquery.find_append_file(res, file.file.get(config.TXT.DNS_TEXT         ), '.[] | select(.type | test("^TXT$"            )) | .strings  // empty                  ')
		jquery.find_append_file(res, file.file.get(config.TXT.IP               ), '.[] | select(.type | test("^A$|^CNAME$|^PTR$")) | .address  // empty                  ')
		jquery.find_append_file(res, file.file.get(config.TXT.SUBDOMAIN        ), '.[] | select(.type | test("^A$|^CNAME$"      )) | .name     // empty, .target // empty')
		jquery.find_append_file(res, file.file.get(config.TXT.SUBDOMAIN        ), '.[] | select(.type | test("^SRV$"            )) | .target   // empty                  ')
		jquery.find_append_file(res, file.file.get(config.TXT.CNAME            ), '.[] | select(.type | test("^CNAME$"          )) | .target   // empty                  ')

	def dig(self, tool: session.Tool):
		session.session.update(tool.identifier)
		# --------------------------------
		filter.file(config.TXT.SUBDOMAIN)
		out = directory.directory.init_tools_file("dig")
		res = run.multiple(
			threads = tool.base.args["threads"],
			out     = out,
			key     = config.TXT.SUBDOMAIN,
			cmd     = [
				f"dig -t A +noall +comments",
				run.set_opt(tool.base.args["timeout"], "+timeout="),
				run.set_opt(run.PLACEHOLDER)
			]
		)
		res = grep.results(res, "subdomain", "status", r"(?<=status\:\ )[^\s]+(?<!\,)")
		res = jquery.find_insert_file(res, file.file.get(config.JSON.SUBDOMAIN_TO_STATUS), 'group_by(.status[]) | map({status: .[0].status[0], subdomain: map(.subdomain)}) | .[]', dump = True)
		jquery.find_append_file(res, file.file.get(config.TXT.SUBDOMAIN      ), '.[] | select(.status == "NOERROR").subdomain[]')
		jquery.find_append_file(res, file.file.get(config.TXT.SUBDOMAIN_ERROR), '.[] | select(.status != "NOERROR").subdomain[]')
		# --------------------------------
		return tool.identifier

	def host(self, tool: session.Tool):
		session.session.update(tool.identifier)
		# --------------------------------
		self.__host(
			tool          = tool,
			primary_key   = config.TXT.SUBDOMAIN_ERROR,
			secondary_key = config.TXT.CNAME,
			type          = config.DNS.CNAME,
			regex         = r"(?<=is\ an\ alias\ for\ )[^\s]+(?<!\.)"
		)
		self.__host(
			tool          = tool,
			primary_key   = config.TXT.SUBDOMAIN,
			secondary_key = config.TXT.IP,
			type          = config.DNS.A,
			regex         = r"(?<=has\ address\ )[^\s]+(?<!\.)"
		)
		self.__host(
			tool          = tool,
			primary_key   = config.TXT.IP,
			secondary_key = config.TXT.SUBDOMAIN,
			type          = config.DNS.PTR,
			regex         = r"(?<=domain\ name\ pointer\ )[^\s]+(?<!\.)"
		)
		self.__host(
			tool          = tool,
			primary_key   = config.TXT.SUBDOMAIN,
			secondary_key = config.TXT.CNAME,
			type          = config.DNS.CNAME,
			regex         = r"(?<=is\ an\ alias\ for\ )[^\s]+(?<!\.)"
		)
		jquery.find_append_file(jquery.jload(file.file.get(config.JSON.SUBDOMAIN_TO_IP)), file.file.get(config.TXT.IP_SUBDOMAIN), '.[].ip[]')
		# --------------------------------
		return tool.identifier

	def __host(self, tool: session.Tool, primary_key: config.TXT, secondary_key: config.TXT, type: config.DNS, regex: str):
		filter.file(primary_key)
		out = directory.directory.init_tools_file("host")
		res = run.multiple(
			threads = tool.base.args["threads"],
			out     = out,
			key     = primary_key,
			cmd     = [
				f"host -s -t {type.value}",
				run.set_opt(tool.base.args["timeout"], "-W"),
				run.set_opt(run.PLACEHOLDER)
			]
		)
		res = grep.results(res, primary_key.value, secondary_key.value, regex)
		res = jquery.find(res, exclusion.JQ.replace_key(exclusion.exclusion.get(exclusion.JQ.HOST), secondary_key.value)) if exclusion.exclusion.should_filter() else res
		jquery.find_append_file(res, file.file.get(secondary_key), f'.[].{secondary_key.value}[]')
		file.insert(jquery.jdump(res), file.file.get(config.JSON(f"{primary_key.value}_to_{secondary_key.value}")))

	def httpx(self, tool: session.Tool):
		session.session.update(tool.identifier)
		# --------------------------------
		filter.file(config.TXT.SUBDOMAIN)
		out   = directory.directory.init_tools_file("httpx", "json")
		input = file.file.get(config.TXT.SUBDOMAIN)
		run.single(
			cmd = [
				"httpx-toolkit -silent -nc -random-agent -p 80,81,443,4443,8000,8008,8080,8081,8403,8443,8888,9000,9008,9080,9081,9403,9443",
				run.set_opt(tool.base.args["threads"], "-t"      ),
				run.set_opt(tool.base.args["timeout"], "-timeout"),
				run.set_opt(tool.base.args["retries"], "-retries"),
				run.set_opt(self.__args.resolvers    , "-r"      ),
				run.set_opt(input.path               , "-l"      ),
				run.set_opt(out.path                 , "-json -o")
			]
		)
		res = jquery.jload_array(out)
		jquery.find_append_file(res, file.file.get(config.TXT.SUBDOMAIN_LIVE_LONG        ), '.[] | select(."status-code" | tostring | test("^2|^3|^4")).url')
		jquery.find_append_file(res, file.file.get(config.TXT.SUBDOMAIN_LIVE_LONG_2XX    ), '.[] | select(."status-code" | tostring | test("^2"      )).url')
		jquery.find_append_file(res, file.file.get(config.TXT.SUBDOMAIN_LIVE_LONG_2XX_4XX), '.[] | select(."status-code" | tostring | test("^2|^4"   )).url')
		jquery.find_append_file(res, file.file.get(config.TXT.SUBDOMAIN_LIVE_LONG_3XX    ), '.[] | select(."status-code" | tostring | test("^3"      )).url')
		jquery.find_append_file(res, file.file.get(config.TXT.SUBDOMAIN_LIVE_LONG_401    ), '.[] | select(."status-code" | tostring | test("^401$"   )).url')
		jquery.find_append_file(res, file.file.get(config.TXT.SUBDOMAIN_LIVE_LONG_403    ), '.[] | select(."status-code" | tostring | test("^403$"   )).url')
		jquery.find_append_file(res, file.file.get(config.TXT.SUBDOMAIN_LIVE_LONG_4XX    ), '.[] | select(."status-code" | tostring | test("^4"      )).url')
		jquery.find_append_file(res, file.file.get(config.TXT.SUBDOMAIN_LIVE_LONG_5XX    ), '.[] | select(."status-code" | tostring | test("^5"      )).url')
		# --------------------------------
		res = jquery.find_insert_file(res, file.file.get(config.JSON.SUBDOMAIN_TO_CSP), 'group_by(.url) | map({subdomain: .[0].url, csp: map(.csp.domains // empty | .[])}) | map(select(.csp | length > 0)) | .[]', dump = True)
		jquery.find_append_file(res, file.file.get(config.TXT.CSP), '.[].csp[]')
		# --------------------------------
		filter.file(config.TXT.SUBDOMAIN_LIVE_LONG)
		subdomains = file.read(file.file.get(config.TXT.SUBDOMAIN_LIVE_LONG), array = False)
		grep.find_append_file(subdomains, file.file.get(config.TXT.SUBDOMAIN_LIVE_LONG_HTTP  ), r"http\:\/\/[^\s\/\?\&\#\%]+"      )
		grep.find_append_file(subdomains, file.file.get(config.TXT.SUBDOMAIN_LIVE_LONG_HTTPS ), r"https\:\/\/[^\s\/\?\&\#\%]+"     )
		grep.find_append_file(subdomains, file.file.get(config.TXT.SUBDOMAIN_LIVE_SHORT      ), r"(?<=\:\/\/)[^\s\/\?\&\#\%]+"     )
		grep.find_append_file(subdomains, file.file.get(config.TXT.SUBDOMAIN_LIVE_SHORT_HTTP ), r"(?<=http\:\/\/)[^\s\/\?\&\#\%]+" )
		grep.find_append_file(subdomains, file.file.get(config.TXT.SUBDOMAIN_LIVE_SHORT_HTTPS), r"(?<=https\:\/\/)[^\s\/\?\&\#\%]+")
		grep.find_append_file(subdomains, file.file.get(config.TXT.SUBDOMAIN_LIVE            ), r"(?<=\:\/\/)[^\s\:\/\?\&\#\%]+"   )
		# --------------------------------
		return tool.identifier

	def eyewitness(self, tool: session.Tool):
		session.session.update(tool.identifier)
		# --------------------------------
		dir        = directory.directory.init_tools_subdirectory("eyewitness")
		log        = directory.directory.init_tools_file("eyewitness", "log", dir)
		input      = file.file.get(config.TXT.SUBDOMAIN_LIVE_LONG)
		user_agent = general.get_random_user_agent()
		run.single(
			cmd = [
				"eyewitness --no-prompt --no-dns",
				run.set_opt(tool.base.args["threads"], "--threads"          ),
				run.set_opt(tool.base.args["timeout"], "--timeout"          ),
				run.set_opt(tool.base.args["retries"], "--max-retries"      ),
				run.set_opt(user_agent               , "--user-agent"       ),
				run.set_opt(input.path               , "-f"                 ),
				run.set_opt(log.path                 , "--selenium-log-path"),
				run.set_opt(dir                      , "-d"                 )
			]
		)
		if not directory.listdir(os.path.join(dir, "screens")):
			directory.remove(dir)
		# --------------------------------
		return tool.identifier

	def getallurls(self, tool: session.Tool):
		session.session.update(tool.identifier)
		# --------------------------------
		out = directory.directory.init_tools_file("getallurls")
		run.multiple(
			threads = tool.base.args["threads"],
			out     = out,
			key     = config.TXT.SUBDOMAIN_LIVE,
			cmd     = [
				"getallurls -random-agent",
				run.set_opt(tool.base.args["retries"], "-retries"),
				run.set_opt(run.PLACEHOLDER)
			]
		)
		res = file.read(out, array = False)
		file.append(res, file.file.get(config.TXT.URL))
		# --------------------------------
		return tool.identifier

	def asnmap(self, tool: session.Tool):
		session.session.update(tool.identifier)
		# --------------------------------
		out = directory.directory.init_tools_file("asnmap", "json")
		run.multiple(
			threads = tool.base.args["threads"],
			out     = out,
			key     = config.TXT.IP,
			cmd     = [
				"asnmap -silent -j",
				run.set_opt(self.__args.resolvers, "-r"),
				run.set_opt(run.PLACEHOLDER      , "-i")
			]
		)
		res = jquery.find_insert_file(jquery.jload_array(out), file.file.get(config.JSON.IP_TO_WHOIS_ASN), 'map({ip: .input, asn: .as_number, org: .as_name, cidr: .as_range}) | .[]', dump = True)
		jquery.find_append_file(res, file.file.get(config.TXT.WHOIS_ASN ), '.[].asn   ')
		jquery.find_append_file(res, file.file.get(config.TXT.WHOIS_CIDR), '.[].cidr[]')
		jquery.find_append_file(res, file.file.get(config.TXT.WHOIS_ORG ), '.[].org   ')
		# --------------------------------
		return tool.identifier

	def openssl(self, tool: session.Tool):
		session.session.update(tool.identifier)
		# --------------------------------
		out = directory.directory.init_tools_file("openssl")
		res = run.multiple(
			threads = tool.base.args["threads"],
			out     = out,
			key     = config.TXT.SUBDOMAIN_LIVE_SHORT_HTTPS,
			cmd     = [
				"echo Q | openssl s_client",
				run.set_opt(run.PLACEHOLDER, "-connect")
			]
		)
		res = grep.results(res, "subdomain", "heartbleed", r"server\ extension\ \"heartbeat\"\ \(id\=15\)")
		jquery.find_append_file(res, file.file.get(config.TXT.CERT_OPENSSL_HEARTBLEED), '.[].subdomain')
		# --------------------------------
		return tool.identifier

	def keytool(self, tool: session.Tool):
		session.session.update(tool.identifier)
		# --------------------------------
		out = directory.directory.init_tools_file("keytool")
		res = run.multiple(
			threads = tool.base.args["threads"],
			out     = out,
			key     = config.TXT.SUBDOMAIN_LIVE_SHORT_HTTPS,
			cmd     = [
				"keytool -printcert -rfc",
				run.set_opt(run.PLACEHOLDER, "-sslserver")
			]
		)
		dir = directory.directory.init_tools_subdirectory("certificates")
		tmp = []
		for result in res:
			out = directory.directory.init_tools_file(result.data.replace(".", "_").replace(":", "_"), "txt", dir)
			tmp.append(cert.Certificate(result.data, result.response, out).to_dict())
		res = jquery.jdump(tmp)
		jquery.find_append_file(res, file.file.get(config.TXT.CERT_SUBJECT_COMMON_NAME), '.[].subject_common_name // empty | .[]')
		file.insert(res, file.file.get(config.JSON.SUBDOMAIN_TO_CERT))
		# --------------------------------
		return tool.identifier

	def sslscan(self, tool: session.Tool):
		session.session.update(tool.identifier)
		# --------------------------------
		out   = directory.directory.init_tools_file("sslscan", "xml")
		input = file.file.get(config.TXT.SUBDOMAIN_LIVE_SHORT_HTTPS)
		run.single(
			cmd = [
				f"sslscan --no-colour -4",
				run.set_opt(tool.base.args["connect_timeout"], "--connect-timeout="),
				run.set_opt(tool.base.args["timeout"        ], "--timeout="        ),
				run.set_opt(input.path                       , "--targets="        ),
				run.set_opt(out.path                         , "--xml="            )
			]
		)
		# --------------------------------
		return tool.identifier

	def scrapy_scraper(self, tool: session.Tool):
		session.session.update(tool.identifier)
		# ---------------------------------
		dir   = directory.directory.init_tools_subdirectory("scrapy_scraper_download")
		out   = directory.directory.init_tools_file("scrapy_scraper")
		input = file.file.get(config.TXT.SUBDOMAIN_LIVE_LONG_2XX)
		run.single(
			cmd = [
				"scrapy-scraper -a random -l",
				run.set_opt(tool.base.args["rate_limit"], "-cr" ),
				run.set_opt(tool.base.args["threads"   ], "-crd"),
				run.set_opt(tool.base.args["timeout"   ], "-t"  ),
				run.set_opt(tool.base.args["retries"   ], "-rt" ),
				run.set_opt(input.path                  , "-u"  ),
				run.set_opt(dir                         , "-dir"),
				run.set_opt(out.path                    , "-o"  )
			]
		)
		file.copy_append(out, file.file.get(config.TXT.LINK))
		# --------------------------------
		return tool.identifier

	def uncover(self, tool: session.Tool):
		session.session.update(tool.identifier)
		# --------------------------------
		out   = directory.directory.init_tools_file("uncover", "json")
		query = f'ssl.cert.subject.CN:"{run.PLACEHOLDER}"'
		res   = run.multiple(
			threads = tool.base.args["threads"],
			out     = out,
			key     = config.TXT.CERT_SUBJECT_COMMON_NAME,
			cmd     = [
				f"uncover -silent -nc -j",
				run.set_opt(tool.base.args["total"  ], "-l"      ),
				run.set_opt(tool.base.args["timeout"], "-timeout"),
				run.set_opt(tool.base.args["retries"], "-retry"  ),
				run.set_opt(query                    , "-shodan" )
			]
		)
		res = jquery.results(res, "subject_common_name", "ip", '{ip: "\(.ip):\(.port)"} + (if .host != "" then {subdomain: .host} else {} end)')
		file.insert(jquery.jdump(res), file.file.get(config.JSON.CERT_SUBJECT_COMMON_NAME_TO_IP))
		# --------------------------------
		return tool.identifier

	def snallygaster(self, tool: session.Tool):
		session.session.update(tool.identifier)
		# --------------------------------
		self.__snallygaster(
			tool = tool,
			key  = config.TXT.SUBDOMAIN_LIVE_SHORT_HTTPS,
			cmd  = [
				"--nohttp"
			]
		)
		self.__snallygaster(
			tool = tool,
			key  = config.TXT.SUBDOMAIN_LIVE_SHORT_HTTP,
			cmd  = [
				"--nohttps"
			]
		)
		# --------------------------------
		return tool.identifier

	def __snallygaster(self, tool: session.Tool, key: config.TXT, cmd: list[str]):
		out        = directory.directory.init_tools_file("snallygaster", "json")
		user_agent = general.get_random_user_agent()
		run.multiple(
			threads = tool.base.args["threads"],
			out     = out,
			key     = key,
			cmd     = [
				"snallygaster -j",
				run.set_opt(user_agent, "--useragent"),
				*cmd,
				run.set_opt(run.PLACEHOLDER)
			]
		)
		res = jquery.jload_array(out)
		jquery.find_append_file(res, file.file.get(config.TXT.DIRECTORY_SENSITIVE), '.[].[].url')

	def trufflehog(self, tool: session.Tool):
		session.session.update(tool.identifier)
		# ---------------------------------
		dir1 = directory.directory.init_tools_subdirectory("scrapy_scraper_download")
		dir2 = directory.directory.init_tools_subdirectory("chad_download")
		out  = directory.directory.init_tools_file("trufflehog")
		run.single(
			out = out,
			cmd = [
				f"trufflehog filesystem --no-color --log-level=-1 --only-verified",
				run.set_opt(tool.base.args["threads"], "--concurrency="),
				run.set_opt(dir1),
				run.set_opt(dir2)
			]
		)
		file.copy_append(out, file.file.get(config.TXT.SECRET))
		# --------------------------------
		return tool.identifier

	def leaky_paths(self, tool: session.Tool):
		session.session.update(tool.identifier)
		# --------------------------------
		out        = directory.directory.init_tools_file("feroxbuster_leaky_paths", "json")
		input      = file.file.get(config.TXT.SUBDOMAIN_LIVE_LONG_2XX_4XX)
		paths      = wordlist.wordlist.get(config.Wordlist.LEAKY_PATHS)
		user_agent = general.get_random_user_agent()
		run.single(
			cmd = [
				f"cat {run.set_opt(input.path)} | feroxbuster --stdin --no-state --silent -k -n --auto-bail -m GET -s 200,301,302,401,403",
				run.set_opt(tool.base.args["threads"   ], "-t"       ),
				run.set_opt(tool.base.args["subthreads"], "-L"       ),
				run.set_opt(tool.base.args["timeout"   ], "-T"       ),
				run.set_opt(user_agent                  , "-a"       ),
				run.set_opt(paths                       , "-w"       ),
				run.set_opt(out.path                    , "--json -o")
			]
		)
		result = jquery.jload_array(out)
		jquery.find_append_file(result, file.file.get(config.TXT.LEAKY_PATHS        ), '.[] | select(."status" | tostring | test("^2|^3|^401$|^403$")).url')
		jquery.find_append_file(result, file.file.get(config.TXT.LEAKY_PATHS_2XX    ), '.[] | select(."status" | tostring | test("^2"               )).url')
		jquery.find_append_file(result, file.file.get(config.TXT.LEAKY_PATHS_2XX_4XX), '.[] | select(."status" | tostring | test("^2|^401$|^403$"   )).url')
		jquery.find_append_file(result, file.file.get(config.TXT.LEAKY_PATHS_3XX    ), '.[] | select(."status" | tostring | test("^3"               )).url')
		jquery.find_append_file(result, file.file.get(config.TXT.LEAKY_PATHS_401    ), '.[] | select(."status" | tostring | test("^401$"            )).url')
		jquery.find_append_file(result, file.file.get(config.TXT.LEAKY_PATHS_403    ), '.[] | select(."status" | tostring | test("^403$"            )).url')
		# --------------------------------
		return tool.identifier

	def urlhunter(self, tool: session.Tool):
		session.session.update(tool.identifier)
		# --------------------------------
		dir   = directory.directory.init_tools_subdirectory("urlhunter")
		out   = directory.directory.init_tools_file("urlhunter")
		input = file.file.get(config.TXT.SUBDOMAIN_LIVE)
		run.single(
			cmd = [
				"urlhunter -date latest",
				run.set_opt(input.path, "-keywords"),
				run.set_opt(out.path  , "-o"       ),
				run.set_opt(dir       , "-a"       ),
			]
		)
		# --------------------------------
		return tool.identifier

	def feroxbuster(self, tool: session.Tool):
		session.session.update(tool.identifier)
		# --------------------------------
		if self.__args.wordlist:
			out        = directory.directory.init_tools_file("feroxbuster", "json")
			input      = file.file.get(config.TXT.SUBDOMAIN_LIVE_LONG_4XX)
			user_agent = general.get_random_user_agent()
			run.single(
				cmd = [
					f"cat {run.set_opt(input.path)} | feroxbuster --stdin --no-state --silent -k -n --auto-bail -m GET -s 200,301,302,401,403",
					run.set_opt(tool.base.args["threads"   ], "-t"       ),
					run.set_opt(tool.base.args["subthreads"], "-L"       ),
					run.set_opt(tool.base.args["timeout"   ], "-T"       ),
					run.set_opt(user_agent                  , "-a"       ),
					run.set_opt(self.__args.wordlist        , "-w"       ),
					run.set_opt(out.path                    , "--json -o")
				]
			)
			res = jquery.jload_array(out)
			jquery.find_append_file(res, file.file.get(config.TXT.DIRECTORY        ), '.[] | select(."status" | tostring | test("^2|^3|^401$|^403$")).url')
			jquery.find_append_file(res, file.file.get(config.TXT.DIRECTORY_2XX    ), '.[] | select(."status" | tostring | test("^2"               )).url')
			jquery.find_append_file(res, file.file.get(config.TXT.DIRECTORY_2XX_4XX), '.[] | select(."status" | tostring | test("^2|^401$|^403$"   )).url')
			jquery.find_append_file(res, file.file.get(config.TXT.DIRECTORY_3XX    ), '.[] | select(."status" | tostring | test("^3"               )).url')
			jquery.find_append_file(res, file.file.get(config.TXT.DIRECTORY_401    ), '.[] | select(."status" | tostring | test("^401$"            )).url')
			jquery.find_append_file(res, file.file.get(config.TXT.DIRECTORY_403    ), '.[] | select(."status" | tostring | test("^403$"            )).url')
		# --------------------------------
		return tool.identifier

	def nmap(self, tool: session.Tool):
		session.session.update(tool.identifier)
		# --------------------------------
		out   = directory.directory.init_tools_file("nmap_icmp")
		input = file.file.get(config.TXT.IP_SUBDOMAIN)
		run.single(
			cmd = [
				"nmap -sn",
				run.set_opt(input.path, "-iL"),
				run.set_opt(out.path  , "-oG")
			]
		)
		res = file.read(out, array = False)
		grep.find_append_file(res, file.file.get(config.TXT.IP_SUBDOMAIN_LIVE), r"(?<=Host\:\ ).[^\s]+")
		# --------------------------------
		out   = directory.directory.init_tools_file("nmap_tcp")
		input = file.file.get(config.TXT.IP_SUBDOMAIN_LIVE)
		run.single(
			cmd = [
				"nmap -n -sS --version-light -sC -Pn --top-ports 1000",
				run.set_opt(input.path, "-iL"),
				run.set_opt(out.path  , "-oN")
			]
		)
		# --------------------------------
		out   = directory.directory.init_tools_file("nmap_udp")
		input = file.file.get(config.TXT.IP_SUBDOMAIN_LIVE)
		run.single(
			cmd = [
				"nmap -n -sU --version-light -sC -Pn -p 53,67,68,69,88,123,135,137,138,139,161,162,389,445,500,514,631,1900,4500",
				run.set_opt(input.path, "-iL"),
				run.set_opt(out.path  , "-oN")
			]
		)
		# --------------------------------
		return tool.identifier

	def forbidden(self, tool: session.Tool):
		session.session.update(tool.identifier)
		# --------------------------------
		if self.__args.collaborator:
			self.__forbidden(
				tool = tool,
				key  = config.TXT.SUBDOMAIN_LIVE_LONG_2XX,
				cmd  = [
					"-t redirects,parsers -f GET -l initial",
					run.set_opt(self.__args.collaborator, "-e")
				]
			)
		self.__forbidden(
			tool = tool,
			key  = config.TXT.SUBDOMAIN_LIVE_LONG_403,
			cmd  = [
				"-t protocols,methods,uploads,overrides,headers,paths-ram,encodings -f GET -l initial,path"
			]
		)
		self.__forbidden(
			tool = tool,
			key  = config.TXT.SUBDOMAIN_LIVE_LONG_401,
			cmd  = [
				"-t auths -f GET -l initial"
			]
		)
		# --------------------------------
		return tool.identifier

	def __forbidden(self, tool: session.Tool, key: config.TXT, cmd: list[str]):
		with concurrent.futures.ThreadPoolExecutor(max_workers = tool.base.args["threads"]) as executor:
			dir = directory.directory.init_tools_subdirectory("forbidden")
			for url in file.read(file.file.get(key)):
				out = directory.directory.init_tools_file(url.replace("//", "_").replace(".", "_").replace(":", "_"), "json", dir)
				executor.submit(
					run.single,
					cmd = [
						"forbidden -st -a random",
						run.set_opt(tool.base.args["subthreads"], "-th"),
						run.set_opt(tool.base.args["timeout"   ], "-rt"),
						*cmd,
						run.set_opt(out.path, "-o"),
						run.set_opt(url     , "-u"),
					],
				)

	def nuclei(self, tool: session.Tool):
		session.session.update(tool.identifier)
		# ---------------------------------
		out   = directory.directory.init_tools_file("nuclei")
		input = file.file.get(config.TXT.SUBDOMAIN_LIVE_LONG_2XX_4XX)
		run.single(
			cmd = [
				"nuclei -silent -nc",
				run.set_opt(tool.base.args["threads"   ], "-c"      ),
				run.set_opt(tool.base.args["subthreads"], "-bs"     ),
				run.set_opt(tool.base.args["timeout"   ], "-timeout"),
				run.set_opt(tool.base.args["retries"   ], "-retries"),
				run.set_opt(input.path                  , "-l"      ),
				run.set_opt(out.path                    , "-o"      )
			]
		)
		# --------------------------------
		return tool.identifier

	def cleanup(self, tool: session.Tool):
		session.session.update(tool.identifier)
		# --------------------------------
		filter.files()
		directory.directory.cleanup()
		# --------------------------------
		return tool.identifier
