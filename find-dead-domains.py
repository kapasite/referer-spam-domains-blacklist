#!/usr/bin/env python3

""" Find dead domains in list. """

import concurrent.futures
import subprocess


def is_domain_dead(domain):
  # check if domain has DNA A record
  cmd = ("dig", "+short", domain)
  try:
    output = subprocess.check_output(cmd)
  except subprocess.CalledProcessError:
    # probably timeout, consider dead
    return True
  return not bool(output)


if __name__ == "__main__":
  futures = {}
  with concurrent.futures.ThreadPoolExecutor(max_workers=32) as executor:
    with open("spammers.txt", "rt") as list_file:
      for domain in list_file:
        domain = domain.rstrip()
        futures[executor.submit(is_domain_dead, domain)] = domain
  for future, domain in futures.items():
    dead = future.result()
    if dead:
      print(domain)
