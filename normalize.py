#!/usr/bin/env python3

import sys


if __name__ == "__main__":
  print('\n'.join(map(lambda x: x.strip().encode("idna").decode(),
                      sys.stdin.readlines())))
