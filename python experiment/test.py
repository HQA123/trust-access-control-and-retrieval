import random
import sys
import numpy as np
from dataclasses import dataclass
from typing import Dict, List, Tuple
import zmq
from multiprocessing import Process
import pandas as pd
import csv
from datetime import datetime
import os

os.chdir(f'C:\\Users\\user\\Desktop\\新建文件夹\\SIoT-IoT-Dataset-main\\edge server sample1')
df_mal = pd.read_csv('sample_10_percent_1.csv', sep=',')

df_mal.drop(1, axis=0, inplace=True)
df_mal.drop(1, axis=0, inplace=True)
print(df_mal)