#!/bin/bash

python3 setup.py sdist

sleep 2

rm -r /home/dadaia/workspace/data_engineering/dm_batch/dist/
cp -r /home/dadaia/workspace/data_engineering/rand_engine/dist /home/dadaia/workspace/data_engineering/dm_batch/


rm -r /home/dadaia/workspace/data_engineering/dm_streaming/dist/
cp -r /home/dadaia/workspace/data_engineering/rand_engine/dist /home/dadaia/workspace/data_engineering/dm_streaming/