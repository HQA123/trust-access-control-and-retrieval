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

@dataclass
class Device:
    device_id: str
    message_violation: []  # [总数，违规数]
    neighbour: {}  # neighbour的评价,{'sp_id': 1 or 0}

class TrustServer:
    def __init__(self):
        # 设备信息存储
        self.devices: Dict[str, Device] = {}

        # 创建日志目录
        self.log_dir = 'device_logs'
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)

        # 创建日志文件
        self.log_file = f'{self.log_dir}/device_records_HLX23_experiment2.csv'

        # 初始化CSV文件头
        with open(self.log_file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                'timestamp',
                'sp_id',
                'sr_id',
                'sr_type',
                'T_D',
                'T_I',
                'Trust'
            ])

    def data_trust_calculation(self, sp_id, sr_id, violation, message_num):
        if sr_id not in self.devices:
            self.devices[sr_id] = Device(sr_id, [0,0], {})

        self.devices[sr_id].message_violation[0] += violation
        self.devices[sr_id].message_violation[1] += message_num

        beta = self.devices[sr_id].message_violation[0]/ self.devices[sr_id].message_violation[1]

        if beta > 0.5:
            T_D = 0
        elif beta > 0.3:
            T_D = 0.5*(1-beta)
        else:
            T_D = 1-beta

        # if violation > 0:
        #     self.devices[sr_id].neighbour[sp_id] = 0
        # else:
        #     self.devices[sr_id].neighbour[sp_id] = 1
        self.devices[sr_id].neighbour[sp_id] = 1 - violation / 10

        return T_D

    def interact_trust_calculation(self, sr_id):
        total = len(self.devices[sr_id].neighbour)
        positive_sum = sum(list(self.devices[sr_id].neighbour.values()))
        T_I = positive_sum/(total + 1) + 0.5/(total + 1)

        return T_I

    def log_device_state(self, timestamp, sp_id, sr_id, sr_type, T_D, T_I, Trust):
        with open(self.log_file, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                timestamp,
                sp_id,
                sr_id,
                sr_type,
                T_D,
                T_I,
                Trust
            ])

if __name__ == "__main__":
    for idx in range(1, 12):
        os.chdir(f'/home/hqa/files/TrustPIR work materials/SIoT-IoT-Dataset-main/edge server sample{idx}')
        server = TrustServer()
        global df1, df2, df3
        df1 = pd.read_csv('output_OOR.csv', sep=',', header=None)
        df2 = pd.read_csv('output_CLOR.csv', sep=',', header=None)
        df3 = pd.read_csv('output_sum_SOR.csv', sep=',', header=None)
        df_obj = pd.read_csv('output_objects_description.csv', sep=',')
        df_mal = pd.read_csv('sample_10_percent_1.csv', sep=',')
        df_temp_acc = pd.read_csv('sample_10_percent_2.csv', sep=',')

        # 遍历所有设备对
        n_devices = len(df1)
        for current_timestamp in range(0, 4):
            for i in range(n_devices):
                for j in range(n_devices):
                    if i != j:  # 不考虑自己对自己的关系
                        # 检查是否存在任何一种关系
                        if df1.iloc[i, j] == 1 or df2.iloc[i, j] == 1 or df3.iloc[i, j] == 1:
                            sp_id = str(i)
                            sr_id = str(j)

                            # 生成随机的violation数量（这里可以根据需要修改）
                            if df_obj.loc[j, 'id_device'] in df_mal['id_device'].values:
                                if current_timestamp == 0:
                                    violations = 0
                                else:
                                    violations = random.randint(5, 10)
                            elif df_obj.loc[j, 'id_device'] in df_temp_acc['id_device'].values:
                                if current_timestamp == 1:
                                    violations = random.randint(0, 5)
                                else:
                                    violations = 0
                            else:
                                continue

                            T_D = server.data_trust_calculation(sp_id, sr_id, violations, 10)
                            if violations >= 5:
                                for sp_id_mal in range(20000, 20030):
                                    server.devices[sr_id].neighbour[sp_id_mal] = 1
                            T_I = server.interact_trust_calculation(sr_id)

                            Trust = 0.5 * T_D + 0.5 * T_I
                            print(f"Trust value between {sp_id} and {sr_id} is {Trust}, at timestamp {current_timestamp}")
                            server.log_device_state(current_timestamp, sp_id, sr_id, df_obj.loc[j, 'device_type'], T_D, T_I, Trust)

        print(f"Server {idx} done!")
