#!/bin/bash

cd /home/dan/uems/runs/ens20
ems_prep --dset gefsp01 --length 24 &&
ems_run &&
ens_post &&
cd /home/dan/uems/scripts
sh post.sh