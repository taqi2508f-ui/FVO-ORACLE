import socket
import ssl
import re
import requests
from typing import Dict, List, Optional


VULN_SIGNATURES = {
    "SSH": [
        {"pattern": r"OpenSSH[_ ]([0-9.]+)", "check": lambda v: _version_lt(v, "8.0"),
         "cve": "CVE-2018-15473", "severity": "HIGH",
         "desc": "OpenSSH < 8.0 user enumeration vulnerability"},
        {"pattern": r"OpenSSH[_ ]([0-9.]+)", "check": lambda v: _version_lt(v, "7.4"),
         "cve": "CVE-2016-10012", "severity": "HIGH",
         "desc": "OpenSSH < 7.4 privilege separation vulnerability"},
    ],
    "FTP": [
        {"pattern": r"vsftpd ([0-9.]+)", "check": lambda v: v == "2.3.4",
         "cve": "CVE-2011-2523", "severity": "CRITICAL",
         "desc": "vsftpd 2.3.4 backdoor vulnerability - RCE possible"},
        {"pattern": r"ProFTPD ([0-9.]+)", "check": lambda v: _version_lt(v, "1.3.6"),
         "cve": "CVE-2019-12815", "severity": "CRITICAL",
         "desc": "ProFTPD < 1.3.6 arbitrary file copy via mod_copy"},
    ],
    "HTTP": [
        {"pattern": r"Apache/([0-9.]+)", "check": lambda v: _version_lt(v, "2.4.51"),
         "cve": "CVE-2021-41773", "severity": "CRITICAL",
         "desc": "Apache HTTP Server path traversal & RCE"},
        {"pattern": r"nginx/([0-9.]+)", "check": lambda v: _version_lt(v, "1.20.0"),
         "cve": "CVE-2021-23017", "severity": "HIGH",
         "desc": "nginx < 1.20.0 DNS resolver off-by-one heap overflow"},
        {"pattern": r"IIS/([0-9.]+)", "check": lambda v: _version_lt(v, "10.0"),
         "cve": "CVE-2017-7269", "severity": "CRITICAL",
         "desc": "IIS WebDAV ScStoragePathFromUrl buffer overflow"},
        {"pattern": r"Microsoft-IIS/([0-9.]+)", "check": lambda v: _version_lt(v, "10.0"),
         "cve": "CVE-2017-7269", "severity": "CRITICAL",
         "desc": "IIS WebDAV ScStoragePathFromUrl buffer overflow"},
    ],
    "MySQL": [
        {"pattern": r"([0-9]+\.[0-9]+\.[0-9]+)-", "check": lambda v: _version_lt(v, "8.0.28"),
         "cve": "CVE-2022-21245", "severity": "HIGH",
         "desc": "MySQL < 8.0.28 privilege escalation vulnerability"},
    ],
    "RDP": [
        {"pattern": r".*", "check": lambda v: True,
         "cve": "CVE-2019-0708", "severity": "CRITICAL",
         "desc": "BlueKeep RDP vulnerability - check patch status manually"},
    ],
    "SMB": [
        {"pattern": r".*", "check": lambda v: True,
         "cve": "CVE-2017-0144", "severity": "CRITICAL",
         "desc": "EternalBlue SMB vulnerability - verify patching"},
    ],
    "Telnet": [
        {"pattern": r".*", "check": lambda v: True,
         "cve": "MISC-001", "severity": "CRITICAL",
         "desc": "Telnet transmits credentials in plaintext"},
    ],
}

DANGEROUS_PORTS = {
    23: ("Telnet", "CRITICAL", "Unencrypted remote access — credentials sent in plaintext"),
    21: ("FTP", "HIGH", "FTP may transmit credentials in plaintext"),
    111: ("RPC", "HIGH", "RPC portmapper can expose internal services"),
    135: ("MSRPC", "HIGH", "MSRPC often targeted for privilege escalation"),
    139: ("NetBIOS", "HIGH", "NetBIOS exposes Windows file sharing info"),
    445: ("SMB", "CRITICAL", "SMB — multiple critical CVEs including EternalBlue"),
    1433: ("MSSQL", "HIGH", "MSSQL database exposed to network"),
    3389: ("RDP", "CRITICAL", "RDP — BlueKeep CVE-2019-0708 if unpatched"),
    4444: ("Metasploit", "CRITICAL", "Default Metasploit listener port — likely compromised"),
    5900: ("VNC", "HIGH", "VNC remote desktop often weakly authenticated"),
    6379: ("Redis", "CRITICAL", "Redis often runs without authentication"),
    27017: ("MongoDB", "CRITICAL", "MongoDB often runs without authentication"),
    9200: ("Elasticsearch", "CRITICAL", "Elasticsearch often exposes data without auth"),
    11211: ("Memcached", "HIGH", "Memcached can be exploited for DDoS amplification"),
    2375: ("Docker", "CRITICAL", "Docker API exposed without TLS — full host compromise"),
}


def _version_lt(v1: str, v2: str) -> bool:
    try:
        parts1 = [int(x) for x in v1.split(".")[:3]]
        parts2 = [int(x) for x in v2.split(".")[:3]]
        while len(parts1) < 3:
            parts1.append(0)
        while len(parts2) < 3:
            parts2.append(0)
        return parts1 < parts2
    except Exception:
        return False


class VulnScanner:
    def __init__(self):
        self._stop = False

    def stop(self):
        self._stop = True

    def analyze_port(self, port: int, service: str, banner: str) -> List[Dict]:
        findings = []

        if port in DANGEROUS_PORTS:
            svc, severity, desc = DANGEROUS_PORTS[port]
            findings.append({
                "type": "dangerous_port",
                "port": port,
                "service": svc,
                "severity": severity,
                "cve": "MISC",
                "description": desc,
                "banner": banner
            })

        if service in VULN_SIGNATURES:
            for sig in VULN_SIGNATURES[service]:
                match = re.search(sig["pattern"], banner, re.IGNORECASE)
                if match:
                    version = match.group(1) if match.lastindex else "unknown"
                    if sig["check"](version):
                        findings.append({
                            "type": "version_vuln",
                            "port": port,
                            "service": service,
                            "severity": sig["severity"],
                            "cve": sig["cve"],
                            "description": sig["desc"],
                            "version": version,
                            "banner": banner
                        })

        if "HTTP" in service and banner:
            findings.extend(self._check_http_headers(port, banner))

        return findings

    def _check_http_headers(self, port: int, banner: str) -> List[Dict]:
        findings = []
        banner_lower = banner.lower()

        if "x-powered-by" in banner_lower:
            match = re.search(r"x-powered-by:\s*(.+)", banner, re.IGNORECASE)
            if match:
                findings.append({
                    "type": "info_disclosure",
                    "port": port,
                    "service": "HTTP",
                    "severity": "LOW",
                    "cve": "INFO-001",
                    "description": f"Server discloses technology via X-Powered-By: {match.group(1).strip()}",
                    "banner": banner
                })

        if "server:" in banner_lower and ("apache" in banner_lower or "nginx" in banner_lower
                                           or "iis" in banner_lower):
            findings.append({
                "type": "info_disclosure",
                "port": port,
                "service": "HTTP",
                "severity": "LOW",
                "cve": "INFO-002",
                "description": "Server header discloses software version",
                "banner": banner
            })

        return findings

    def check_ssl(self, host: str, port: int = 443) -> List[Dict]:
        findings = []
        try:
            context = ssl.create_default_context()
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE
            with socket.create_connection((host, port), timeout=5) as sock:
                with context.wrap_socket(sock, server_hostname=host) as ssock:
                    cert = ssock.getpeercert()
                    proto = ssock.version()

                    if proto in ("TLSv1", "TLSv1.1", "SSLv2", "SSLv3"):
                        findings.append({
                            "type": "weak_tls",
                            "port": port,
                            "service": "SSL/TLS",
                            "severity": "HIGH",
                            "cve": "CVE-2014-3566",
                            "description": f"Weak TLS version in use: {proto} (POODLE/BEAST risk)",
                            "banner": proto
                        })
        except Exception:
            pass
        return findings

    def analyze_scan_results(self, host: str, scan_results: Dict) -> List[Dict]:
        all_findings = []
        for port, info in scan_results.items():
            service = info.get("service", "Unknown")
            banner = info.get("banner", "")
            port_findings = self.analyze_port(port, service, banner)
            all_findings.extend(port_findings)

        ssl_ports = [p for p in scan_results if p in (443, 8443, 465, 993, 995)]
        for port in ssl_ports:
            ssl_findings = self.check_ssl(host, port)
            all_findings.extend(ssl_findings)

        return all_findings
