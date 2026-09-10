import socket
import threading
import queue
import time
from typing import Callable, List, Dict, Optional


COMMON_PORTS = {
    21: "FTP", 22: "SSH", 23: "Telnet", 25: "SMTP", 53: "DNS",
    80: "HTTP", 110: "POP3", 111: "RPC", 135: "MSRPC", 139: "NetBIOS",
    143: "IMAP", 443: "HTTPS", 445: "SMB", 465: "SMTPS", 514: "Syslog",
    587: "SMTP-TLS", 631: "IPP", 993: "IMAPS", 995: "POP3S",
    1080: "SOCKS", 1433: "MSSQL", 1521: "Oracle", 2049: "NFS",
    2375: "Docker", 2376: "Docker-TLS", 3000: "NodeJS", 3306: "MySQL",
    3389: "RDP", 4444: "Metasploit", 4848: "GlassFish", 5000: "Flask",
    5432: "PostgreSQL", 5900: "VNC", 5985: "WinRM-HTTP", 5986: "WinRM-HTTPS",
    6379: "Redis", 6443: "Kubernetes", 7001: "WebLogic", 8000: "HTTP-Alt",
    8080: "HTTP-Proxy", 8443: "HTTPS-Alt", 8888: "Jupyter", 9000: "SonarQube",
    9090: "Prometheus", 9200: "Elasticsearch", 10250: "Kubelet",
    11211: "Memcached", 27017: "MongoDB", 50070: "Hadoop-HDFS"
}


class PortScanner:
    def __init__(self, timeout: float = 1.0, threads: int = 200):
        self.timeout = timeout
        self.threads = threads
        self._stop_event = threading.Event()
        self.results: Dict[int, Dict] = {}
        self._lock = threading.Lock()

    def stop(self):
        self._stop_event.set()

    def reset(self):
        self._stop_event.clear()
        self.results = {}

    def _check_port(self, host: str, port: int, result_queue: queue.Queue):
        if self._stop_event.is_set():
            return
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(self.timeout)
            start = time.time()
            code = sock.connect_ex((host, port))
            latency = round((time.time() - start) * 1000, 2)
            if code == 0:
                service = COMMON_PORTS.get(port, "Unknown")
                banner = self._grab_banner(sock, port)
                result_queue.put({
                    "port": port,
                    "state": "open",
                    "service": service,
                    "banner": banner,
                    "latency_ms": latency
                })
            sock.close()
        except (socket.timeout, ConnectionRefusedError, OSError):
            pass

    def _grab_banner(self, sock: socket.socket, port: int) -> str:
        try:
            sock.settimeout(2.0)
            probes = {
                80: b"HEAD / HTTP/1.0\r\nHost: target\r\n\r\n",
                443: b"HEAD / HTTP/1.0\r\nHost: target\r\n\r\n",
                8080: b"HEAD / HTTP/1.0\r\nHost: target\r\n\r\n",
                21: None,
                22: None,
                25: None,
                110: None,
                143: None,
            }
            if port in probes and probes[port]:
                sock.send(probes[port])
            banner = sock.recv(1024).decode("utf-8", errors="ignore").strip()
            return banner[:200] if banner else ""
        except Exception:
            return ""

    def scan(
        self,
        host: str,
        port_range: tuple = (1, 1024),
        port_list: Optional[List[int]] = None,
        callback: Optional[Callable] = None,
        progress_callback: Optional[Callable] = None
    ) -> Dict[int, Dict]:
        self.reset()

        if port_list:
            ports = port_list
        else:
            ports = list(range(port_range[0], port_range[1] + 1))

        total = len(ports)
        result_queue = queue.Queue()
        port_queue = queue.Queue()

        for p in ports:
            port_queue.put(p)

        scanned = [0]
        scan_lock = threading.Lock()

        def worker():
            while not self._stop_event.is_set():
                try:
                    port = port_queue.get_nowait()
                except queue.Empty:
                    break
                self._check_port(host, port, result_queue)
                with scan_lock:
                    scanned[0] += 1
                    if progress_callback:
                        progress_callback(scanned[0], total)
                port_queue.task_done()

        thread_list = []
        count = min(self.threads, total)
        for _ in range(count):
            t = threading.Thread(target=worker, daemon=True)
            t.start()
            thread_list.append(t)

        for t in thread_list:
            t.join()

        while not result_queue.empty():
            item = result_queue.get()
            self.results[item["port"]] = item
            if callback:
                callback(item)

        return dict(sorted(self.results.items()))

    def scan_common(
        self,
        host: str,
        callback: Optional[Callable] = None,
        progress_callback: Optional[Callable] = None
    ) -> Dict[int, Dict]:
        return self.scan(
            host,
            port_list=list(COMMON_PORTS.keys()),
            callback=callback,
            progress_callback=progress_callback
        )
