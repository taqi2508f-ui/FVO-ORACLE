import socket
import struct
import threading
import subprocess
import platform
import ipaddress
import queue
from typing import Callable, List, Dict, Optional


class HostDiscovery:
    def __init__(self, timeout: float = 1.5, threads: int = 100):
        self.timeout = timeout
        self.threads = threads
        self._stop_event = threading.Event()

    def stop(self):
        self._stop_event.set()

    def reset(self):
        self._stop_event.clear()

    def _ping_host(self, ip: str) -> bool:
        system = platform.system().lower()
        if system == "windows":
            cmd = ["ping", "-n", "1", "-w", "1000", ip]
        else:
            cmd = ["ping", "-c", "1", "-W", "1", ip]
        try:
            result = subprocess.run(
                cmd, stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL, timeout=3,
                **self._no_window_kwargs()
            )
            return result.returncode == 0
        except Exception:
            return False

    @staticmethod
    def _no_window_kwargs() -> dict:
        """Prevent a console window from flashing for each subprocess call on Windows."""
        if platform.system().lower() == "windows":
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            return {
                "creationflags": subprocess.CREATE_NO_WINDOW,
                "startupinfo": startupinfo,
            }
        return {}

    def _tcp_probe(self, ip: str, port: int = 80) -> bool:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(self.timeout)
            result = sock.connect_ex((ip, port))
            sock.close()
            return result == 0
        except Exception:
            return False

    def _resolve_hostname(self, ip: str) -> str:
        try:
            return socket.gethostbyaddr(ip)[0]
        except Exception:
            return ""

    def _get_mac(self, ip: str) -> str:
        try:
            system = platform.system().lower()
            if system == "windows":
                result = subprocess.run(
                    ["arp", "-a", ip], capture_output=True, text=True, timeout=3,
                    **self._no_window_kwargs()
                )
                for line in result.stdout.splitlines():
                    if ip in line:
                        parts = line.split()
                        for part in parts:
                            if "-" in part and len(part) == 17:
                                return part.upper()
            return ""
        except Exception:
            return ""

    def _probe_host(self, ip: str, result_queue: queue.Queue,
                    callback: Optional[Callable], progress_ref: list,
                    progress_lock: threading.Lock, total: int,
                    progress_callback: Optional[Callable]):
        if self._stop_event.is_set():
            return

        alive = self._ping_host(ip)
        if not alive:
            alive = self._tcp_probe(ip, 80) or self._tcp_probe(ip, 443) or self._tcp_probe(ip, 22)

        if alive:
            hostname = self._resolve_hostname(ip)
            mac = self._get_mac(ip)
            info = {"ip": ip, "hostname": hostname, "mac": mac, "alive": True}
            result_queue.put(info)
            if callback:
                callback(info)

        with progress_lock:
            progress_ref[0] += 1
            if progress_callback:
                progress_callback(progress_ref[0], total)

    def scan_range(
        self,
        cidr: str,
        callback: Optional[Callable] = None,
        progress_callback: Optional[Callable] = None
    ) -> List[Dict]:
        self.reset()
        try:
            network = ipaddress.ip_network(cidr, strict=False)
            hosts = list(network.hosts())
        except ValueError:
            try:
                parts = cidr.split("-")
                if len(parts) == 2:
                    start = ipaddress.ip_address(parts[0].strip())
                    end = ipaddress.ip_address(parts[1].strip())
                    hosts = []
                    current = start
                    while current <= end:
                        hosts.append(current)
                        current += 1
                else:
                    hosts = [ipaddress.ip_address(cidr)]
            except Exception:
                return []

        total = len(hosts)
        result_queue = queue.Queue()
        host_queue = queue.Queue()
        progress_ref = [0]
        progress_lock = threading.Lock()

        for h in hosts:
            host_queue.put(str(h))

        def worker():
            while not self._stop_event.is_set():
                try:
                    ip = host_queue.get_nowait()
                except queue.Empty:
                    break
                self._probe_host(
                    ip, result_queue, callback,
                    progress_ref, progress_lock, total, progress_callback
                )
                host_queue.task_done()

        thread_list = []
        count = min(self.threads, total)
        for _ in range(count):
            t = threading.Thread(target=worker, daemon=True)
            t.start()
            thread_list.append(t)

        for t in thread_list:
            t.join()

        results = []
        while not result_queue.empty():
            results.append(result_queue.get())

        return sorted(results, key=lambda x: socket.inet_aton(x["ip"]))

    def get_local_network(self) -> str:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
            s.close()
            parts = local_ip.split(".")
            return f"{parts[0]}.{parts[1]}.{parts[2]}.0/24"
        except Exception:
            return "192.168.1.0/24"

    def get_local_ip(self) -> str:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except Exception:
            return "127.0.0.1"
