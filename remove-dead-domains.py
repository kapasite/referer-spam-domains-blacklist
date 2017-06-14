#!/usr/bin/env python3

""" Remove dead domains from list. """

import argparse
import concurrent.futures
import functools
import ipaddress
import os
import socket
import subprocess

import tqdm


DNS_SERVERS = ("8.8.8.8",  # Google DNS
               "208.67.222.222",  # OpenDNS
               "84.200.69.80",  # DNS.WATCH
               "209.244.0.3",  # Level3 DNS
               "8.26.56.26")  # Comodo Secure DNS
WEB_PORTS = (80, 443)


def dns_resolve(domain, dns_server):
  """ Return IP string if domain has a DNA A record on this DNS server, False otherwise. """
  cmd = ("dig", "+short", "+time=5", "+tries=999", "@%s" % (dns_server), domain)
  output = subprocess.check_output(cmd, universal_newlines=True)
  if output:
    ip = output.splitlines()[-1]
    try:
      # validate IP
      return str(ipaddress.IPv4Address(ip))
    except ipaddress.AddressValueError:
      pass
  return False


@functools.lru_cache(maxsize=2048)
def has_tcp_port_open(ip, port):
  """ Return True if domain is listening on a TCP port, False instead. """
  r = True
  with socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM) as sckt:
    sckt.settimeout(10)
    try:
      sckt.connect((ip, port))
    except (ConnectionRefusedError, socket.timeout):
      r = False
  return r


if __name__ == "__main__":
  # parse args
  arg_parser = argparse.ArgumentParser(description=__doc__,
                                       formatter_class=argparse.ArgumentDefaultsHelpFormatter)
  arg_parser.add_argument("list_file",
                          help="Domain list file path")
  args = arg_parser.parse_args()

  # read list
  with open(args.list_file, "rt") as list_file:
    domains = tuple(map(str.rstrip, list_file.readlines()))
  dead_domains = set()

  # resolve domains with thread pool
  dns_check_futures = []
  with concurrent.futures.ThreadPoolExecutor(max_workers=os.cpu_count() * 12) as executor:
    # add work
    for domain in tqdm.tqdm(domains,
                            desc="Adding DNS domain check work to thread pool",
                            unit=" domains",
                            leave=True):
      dns_check_domain_futures = []
      for dns_server in DNS_SERVERS:
        future = executor.submit(dns_resolve, domain, dns_server)
        dns_check_domain_futures.append(future)
      dns_check_futures.append(dns_check_domain_futures)

    # show progress
    for dns_check_domain_futures in tqdm.tqdm(dns_check_futures,
                                              desc="DNS domain checks",
                                              unit=" domains",
                                              leave=True):
      for _ in tqdm.tqdm(concurrent.futures.as_completed(dns_check_domain_futures),
                         total=len(dns_check_domain_futures),
                         desc="Per domain DNS checks",
                         unit=" DNS servers",
                         leave=True):
        pass

  # for domains with at least one failed DNS resolution, check open ports
  tcp_check_futures = {}
  with concurrent.futures.ThreadPoolExecutor(max_workers=os.cpu_count() * 2) as executor:
    for dns_check_domain_futures, domain in zip(dns_check_futures, domains):
      dns_check_domain_results = tuple(f.result() for f in dns_check_domain_futures)
      if not any(dns_check_domain_results):
        # all DNS checks failed
        dead_domains.add(domain)
      elif not all(dns_check_domain_results):
        # at least one DNS check failed, but at least one succeeded
        ip = next(filter(None, dns_check_domain_results))  # take result of first successful resolution
        tcp_check_domain_futures = []
        for port in WEB_PORTS:
          future = executor.submit(has_tcp_port_open, ip, port)
          tcp_check_domain_futures.append(future)
        tcp_check_futures[domain] = tcp_check_domain_futures

    # show progress
    for domain in tqdm.tqdm(tcp_check_futures,
                            desc="TCP domain check",
                            unit=" domains",
                            leave=True):
      for _ in tqdm.tqdm(concurrent.futures.as_completed(tcp_check_futures[domain]),
                         total=len(tcp_check_futures[domain]),
                         desc="Per domain TCP port server check",
                         unit=" port checks",
                         leave=True):
        pass

  # results
  for domain, tcp_check_domain_futures in tcp_check_futures.items():
    tcp_check_domain_results = tuple(f.result() for f in tcp_check_domain_futures)
    if not any(dns_check_domain_results):
      # no web port open for this domain
      dead_domains.add(domain)

  # write new file
  with open(args.list_file, "wt") as list_file:
   for domain in domains:
      if domain not in dead_domains:
        list_file.write("%s\n" % (domain))
  print("\n%u dead domain(s) removed" % (len(dead_domains)))
