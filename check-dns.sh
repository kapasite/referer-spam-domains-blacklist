#!/bin/bash

for DOM in `cat spammers.txt`; do

  host "$DOM" &> /dev/null

  if [ "$?" == "0" ]; then
    echo "$DOM" >> up.txt
  else
    echo "$DOM" >> down.txt
  fi

done

exit 0
