#!/usr/bin/env python3

""" Remove dead domains from list. """

import argparse
import concurrent.futures
import subprocess
import threading


DNS_SERVERS = ("8.8.8.8",  # Google DNS
               "208.67.222.222",  # OpenDNS
               "84.200.69.80",  # DNS.WATCH
               "209.244.0.3",  # Level3 DNS
               "8.26.56.26")  # Comodo Secure DNS

checks_done_count = 0
domains_count = 0
domains_count_lock = threading.Lock()


def is_domain_dead(domain, dns_server):
  """ Return True if domain has a DNA A record on this DNS server, False instead. """
  cmd = ("dig", "+short", "+time=10", "+tries=6", "@%s" % (dns_server), domain)
  output = subprocess.check_output(cmd)
  # update progress
  global checks_done_count, domains_count, domains_count_lock
  with domains_count_lock:
    checks_done_count += 1
    print("%u/%u domains checked" % (checks_done_count // len(DNS_SERVERS), domains_count), end="\r")
  return not bool(output)


if __name__ == "__main__":
  # parse args
  arg_parser = argparse.ArgumentParser(description=__doc__,
                                       formatter_class=argparse.ArgumentDefaultsHelpFormatter)
  arg_parser.add_argument("list_file",
                          help="Domain list file path")
  args = arg_parser.parse_args()

  # analyze domains with thread pool
  futures = []
  domains = []
  with concurrent.futures.ThreadPoolExecutor(max_workers=64) as executor:
    with open(args.list_file, "rt") as list_file:
      for domain in list_file:
        domain = domain.rstrip()
        domains.append(domain)
        with domains_count_lock:
          domains_count += 1
        domain_futures = []
        for dns_server in DNS_SERVERS:
          future = executor.submit(is_domain_dead, domain, dns_server)
          domain_futures.append(future)
        futures.append(domain_futures)

  # write new file
  domains_removed_count = 0
  with open(args.list_file, "wt") as list_file:
    for domain_futures, domain in zip(futures, domains):
      domain_futures_results = tuple(f.result() for f in domain_futures)
      # consider domain is dead only if all DNS servers have no entry
      if all(domain_futures_results):
        domains_removed_count += 1
      else:
        list_file.write("%s\n" % (domain))
  print("\n%u dead domains removed" % (domains_removed_count))
