#!/bin/bash

for p in "What text is in this image?" "Please describe this image:" "Please transcribe this image:";
do for run in {1..3};
do time ./bench.py --prompt "$p" --model sysbak2 --images $1;
done; done
