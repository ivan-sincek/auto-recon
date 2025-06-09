#!/usr/bin/env python3

from . import array, debug, file, grep

import cryptography.x509, OpenSSL.crypto

IGNORED_CA = ["Amazon", "DigiCert", "E6", "GTS", "GeoTrust", "GlobalSign", "Go Daddy", "GoDaddy", "Google", "ISRG", "Internet Security Research Group", "Let's Encrypt", "Microsoft", "R11", "Starfield"]
"""
List of case-insensitive keywords.
"""

ENCODING = "ISO-8859-1"

# ----------------------------------------

def decode_pem(text: str, out: file.SafeFile | str = None) -> list[cryptography.x509.Certificate]:
	"""
	Extract all PEM certificates from a text and deserialize them into objects, then, dump the stringified objects into a file.
	"""
	tmp = []
	stringified = []
	for pem in grep.find(text, r"-----BEGIN CERTIFICATE-----[\s\S]+?-----END CERTIFICATE-----", sort = False):
		try:
			tmp.append(cryptography.x509.load_pem_x509_certificate(pem.encode(ENCODING)))
			if out:
				stringified.append(OpenSSL.crypto.dump_certificate(OpenSSL.crypto.FILETYPE_TEXT, OpenSSL.crypto.load_certificate(OpenSSL.crypto.FILETYPE_PEM, pem)).decode(ENCODING))
		except Exception as ex:
			debug.debug.log_error(f"utils.cert.decode_pem() > {out}" if out else "utils.cert.decode_pem()", ex)
	if stringified:
		file.insert(("\n").join(stringified), out)
	return tmp

def __get_attribute(cert: cryptography.x509.Certificate, attribute: cryptography.x509.ObjectIdentifier, subject: bool) -> list[str]:
	"""
	Get an attribute from a certificate.\n
	Set 'subject' to 'True' to get an attribute from the certificate's subject, or to 'False' to get it from the certificate's issuer.
	"""
	tmp = []
	section = cert.subject if subject else cert.issuer
	if section:
		for entry in section.get_attributes_for_oid(attribute):
			if entry.value:
				tmp.append(str(entry.value))
	return tmp

# ----------------------------------------

def __get_common_name(cert: cryptography.x509.Certificate, subject: bool):
	"""
	Get the common name from a certificate.\n
	Set 'subject' to 'True' to get an attribute from the certificate's subject, or to 'False' to get it from the certificate's issuer.\n
	Returns a unique sorted list.
	"""
	return array.filter_blacklist(__get_attribute(cert, cryptography.x509.NameOID.COMMON_NAME, subject), IGNORED_CA, case_sensitive = False, sort = True)

def get_subject_common_name(cert: cryptography.x509.Certificate):
	"""
	Get the common name from the certificate's subject.\n
	Returns a unique sorted list.
	"""
	return __get_common_name(cert, subject = True)

def get_issuer_common_name(cert: cryptography.x509.Certificate):
	"""
	Get the common name from the certificate's issuer.\n
	Returns a unique sorted list.
	"""
	return __get_common_name(cert, subject = False)

# ----------------------------------------

def __get_org_name(cert: cryptography.x509.Certificate, subject: bool):
	"""
	Get the organization name from a certificate.\n
	Set 'subject' to 'True' to get an attribute from the certificate's subject, or to 'False' to get it from the certificate's issuer.\n
	Returns a unique sorted list.
	"""
	return array.filter_blacklist(__get_attribute(cert, cryptography.x509.NameOID.ORGANIZATION_NAME, subject), IGNORED_CA, case_sensitive = False, sort = True)

def get_subject_org_name(cert: cryptography.x509.Certificate):
	"""
	Get the organization name from the certificate's subject.\n
	Returns a unique sorted list.
	"""
	return __get_org_name(cert, subject = True)

def get_issuer_org_name(cert: cryptography.x509.Certificate):
	"""
	Get the organization name from the certificate's issuer.\n
	Returns a unique sorted list.
	"""
	return __get_org_name(cert, subject = False)

# ----------------------------------------

def __get_org_unit_name(cert: cryptography.x509.Certificate, subject: bool):
	"""
	Get the organization unit name from a certificate.\n
	Set 'subject' to 'True' to get an attribute from the certificate's subject, or to 'False' to get it from the certificate's issuer.\n
	Returns a unique sorted list.
	"""
	return array.filter_blacklist(__get_attribute(cert, cryptography.x509.NameOID.ORGANIZATIONAL_UNIT_NAME, subject), IGNORED_CA, case_sensitive = False, sort = True)

def get_subject_org_unit_name(cert: cryptography.x509.Certificate):
	"""
	Get the organization unit name from the certificate's subject.\n
	Returns a unique sorted list.
	"""
	return __get_org_unit_name(cert, subject = True)

def get_issuer_org_unit_name(cert: cryptography.x509.Certificate):
	"""
	Get the organization unit name from the certificate's issuer.\n
	Returns a unique sorted list.
	"""
	return __get_org_unit_name(cert, subject = False)

# ----------------------------------------

class Certificate:

	def __init__(self, subdomain: str, text: str, out: file.SafeFile | str = None):
		"""
		Class for storing certificate details.
		"""
		self.subdomain            : str       = subdomain
		self.subject_common_name  : list[str] = []
		self.subject_org_name     : list[str] = []
		self.subject_org_unit_name: list[str] = []
		self.issuer_common_name   : list[str] = []
		self.issuer_org_name      : list[str] = []
		self.issuer_org_unit_name : list[str] = []
		for cert in decode_pem(text, out):
			self.subject_common_name.extend(get_subject_common_name(cert))
			self.subject_org_name.extend(get_subject_org_name(cert))
			self.subject_org_unit_name.extend(get_subject_org_unit_name(cert))
			self.issuer_common_name.extend(get_issuer_common_name(cert))
			self.issuer_org_name.extend(get_issuer_org_name(cert))
			self.issuer_org_unit_name.extend(get_issuer_org_unit_name(cert))
		for attr, value in list(self.__dict__.items()):
			if isinstance(value, list):
				setattr(self, attr, array.unique(value)) if value else delattr(self, attr)

	def to_dict(self):
		"""
		Return the class as a dictionary.
		"""
		return self.__dict__
