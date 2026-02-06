import random
from dataclasses import dataclass
from typing import Dict, List, Tuple
import pandas as pd
import csv
import os

@dataclass
class Device:
    device_id: str
    device_type: str  # 设备类型
    off_service: set[str]  # 不提供服务的设备
    req_service: set[str]  # 请求服务的设备
    punishment: int  # 惩罚值

class TrustServer:
    def __init__(self):
        # 设备信息存储
        self.devices: Dict[str, Device] = {}

        # 创建日志目录
        self.log_dir = 'device_logs'
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)

        # 创建日志文件
        self.log_file = f'{self.log_dir}/device_records_KND21.csv'

        # 初始化CSV文件头
        with open(self.log_file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                'timestamp',
                'sp_id',
                'sr_id',
                'sr_type',
                'Trust'
            ])

    def similarity_trust(self, sp_id, sr_id, sp_type, sr_type, violations):
        if sr_id not in self.devices:
            self.devices[sr_id] = Device(
    sp_id,
    sp_type,
    set(map(str.strip, str(df4.loc[int(sr_type) - 1, 'id_off_service']).split(','))),
    set(map(str.strip, str(df4.loc[int(sr_type) - 1, 'id_req_service']).split(','))),
    1
)
        if sp_id not in self.devices:
            self.devices[sp_id] = Device(
    sp_id,
    sp_type,
    set(map(str.strip, str(df4.loc[int(sp_type) - 1, 'id_off_service']).split(','))),
    set(map(str.strip, str(df4.loc[int(sp_type) - 1, 'id_req_service']).split(','))),
    1
)

        if self.devices[sr_id].req_service:
            if (violations > 5) and (len(self.devices[sr_id].req_service) >= 2):
                to_remove = set(random.sample(self.devices[sr_id].req_service, 2))
                self.devices[sr_id].req_service.difference_update(to_remove)
                self.devices[sr_id].punishment *= 0.6
            elif violations > 0:
                to_remove = set(random.sample(self.devices[sr_id].req_service, 1))
                self.devices[sr_id].req_service.difference_update(to_remove)
                self.devices[sr_id].punishment *= 0.8
            else:
                self.devices[sr_id].req_service = set(map(str.strip, str(df4.loc[int(sr_type) - 1, 'id_req_service']).split(',')))
                self.devices[sr_id].punishment =1

        temp_common = self.devices[sp_id].off_service & self.devices[sr_id].req_service
        temp_all = self.devices[sp_id].off_service | self.devices[sr_id].req_service
        simu = len(temp_common) / len(temp_all) if len(temp_all) else 0

        simd_second_term = 0
        if df1.iloc[int(sp_id), int(sr_id)] == 1:
            simd_second_term += 1
        if df2.iloc[int(sp_id), int(sr_id)] == 1:
            simd_second_term += 1
        if df3.iloc[int(sp_id), int(sr_id)] == 1:
            simd_second_term += 1
        simd_second_term /= 3

        trust_value = 0.5 * simu + 0.5 * simd_second_term * self.devices[sr_id].punishment

        return trust_value



    def log_device_state(self, timestamp, sp_id, sr_id, sr_type, Trust):
        with open(self.log_file, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                timestamp,
                sp_id,
                sr_id,
                sr_type,
                Trust
            ])

if __name__ == "__main__":
    for idx in range(1, 12):
        os.chdir(f'/home/hqa/files/TrustPIR work materials/SIoT-IoT-Dataset-main/edge server sample{idx}')
        server = TrustServer()
        global df1, df2, df3, df4
        df1 = pd.read_csv('output_OOR.csv', sep=',', header=None)
        df2 = pd.read_csv('output_CLOR.csv', sep=',', header=None)
        df3 = pd.read_csv('output_sum_SOR.csv', sep=',', header=None)
        df4 = pd.read_csv(f'/home/hqa/files/TrustPIR work materials/SIoT-IoT-Dataset-main/objects_profile/processed_objects_profile.csv', sep=',')
        df_obj = pd.read_csv('output_objects_description.csv', sep=',')
        df_mal = pd.read_csv('sample_10_percent_1.csv', sep=',')
        df_temp_acc = pd.read_csv('sample_10_percent_2.csv', sep=',')

        # 遍历所有设备对
        n_devices = len(df1)
        for current_timestamp in range(0, 3):
            for i in range(n_devices):
                for j in range(n_devices):
                    if i != j:  # 不考虑自己对自己的关系
                        # 检查是否存在任何一种关系
                        if df1.iloc[i, j] == 1 or df2.iloc[i, j] == 1 or df3.iloc[i, j] == 1:
                            sp_id = str(i)
                            sr_id = str(j)

                            # 生成随机的violation数量（这里可以根据需要修改）
                            if df_obj.loc[j, 'id_device'] in df_mal['id_device'].values:
                                violations = random.randint(5, 10)
                                trust = server.similarity_trust(sp_id, sr_id, df_obj.loc[j, 'device_type'], df_obj.loc[i, 'device_type'], violations)
                            elif df_obj.loc[j, 'id_device'] in df_temp_acc['id_device'].values:
                                violations = random.randint(0, 5)
                                trust = server.similarity_trust(sp_id, sr_id, df_obj.loc[j, 'device_type'], df_obj.loc[i, 'device_type'], violations)
                            else:
                                continue

                            print(f"Trust value between {sp_id} and {sr_id} is {trust}, at timestamp {current_timestamp}")
                            server.log_device_state(current_timestamp, sp_id, sr_id, df_obj.loc[j, 'device_type'],trust)

        print(f"Sample {idx} done!")
