#!/usr/bin/env python3

""" Remove dead domains from list. """

import argparse
import concurrent.futures
import subprocess
import threading


domains_done_count = 0
domains_count = 0
domains_count_lock = threading.Lock()


def is_domain_dead(domain):
  """ Return True if domain has a DNA A record, False instead. """
  cmd = ("dig", "+short", "+time=10", "+tries=6", domain)
  output = subprocess.check_output(cmd)
  # update progress
  global domains_done_count, domains_count, domains_count_lock
  with domains_count_lock:
    domains_done_count += 1
    print("%u/%u domains checked" % (domains_done_count, domains_count), end="\r")
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
        future = executor.submit(is_domain_dead, domain)
        futures.append(future)

  # write new file
  domains_removed_count = 0
  with open(args.list_file, "wt") as list_file:
    for future, domain in zip(futures, domains):
      dead = future.result()
      if not dead:
        list_file.write("%s\n" % (domain))
      else:
        domains_removed_count += 1
  print("\n%u dead domains removed" % (domains_removed_count))
