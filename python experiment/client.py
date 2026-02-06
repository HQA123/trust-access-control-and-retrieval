import os

import zmq
import pandas as pd
import random

class TrustClient:
    def __init__(self, server_address="tcp://localhost:5555"):
        # 初始化ZMQ
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.PUSH)
        self.socket.setsockopt(zmq.SNDHWM, 100000)  # 设置高水位标记
        self.socket.connect(server_address)

    def send_violation_record(self, sp_id: str, sr_id: str, sr_type: str, timestamp: int, violations: int):
        """发送violation记录到服务器"""
        message = {
            "sp_id": sp_id,
            "sr_id": sr_id,
            "sr_type": sr_type,
            "timestamp": timestamp,
            "violations": violations
        }
        self.socket.send_json(message)
        return

# 使用示例
if __name__ == "__main__":

    os.chdir(f'/home/hqa/files/TrustPIR work materials/SIoT-IoT-Dataset-main/edge server sample1')
    global df1, df2, df3
    df1 = pd.read_csv('output_OOR.csv', sep=',', header=None)
    df2 = pd.read_csv('output_CLOR.csv', sep=',', header=None)
    df3 = pd.read_csv('output_sum_SOR.csv', sep=',', header=None)
    df_obj = pd.read_csv('output_objects_description.csv', sep=',')
    df_mal = pd.read_csv('sample_10_percent_1.csv', sep=',')
    df_temp_acc = pd.read_csv('sample_10_percent_2.csv', sep=',')
    # 创建客户端
    client = TrustClient("tcp://localhost:5551")
    for current_timestamp in range(0,5):
        #current_timestamp = 1
        print(current_timestamp)

        # 设备类型转换器
        switcher = {
            '1': 'smartphone',
            '2': 'car',
            '4': 'smart fitness',
            '9': 'point of interest',
            '10': 'environment monitor',
            '11': 'transportation',
            '12': 'indicator',
            '13': 'garbage truck',
            '14': 'street light',
            '15': 'parking',
            '16': 'alarms'
        }

        # 遍历所有设备对
        n_devices = len(df1)

        for i in range(n_devices):
            for j in range(n_devices):
                if i != j:  # 不考虑自己对自己的关系
                    # 检查是否存在任何一种关系
                    if df1.iloc[i, j] == 1 or df2.iloc[i, j] == 1 or df3.iloc[i, j] == 1:
                        sp_id = str(i)
                        sr_id = str(j)

                        # 生成随机的violation数量（这里可以根据需要修改）
                        violations = 0
                        if (df_obj.loc[j, 'id_device'] in df_mal['id_device'].values) and (current_timestamp > 1):
                            violations = random.randint(5, 10)
                        if (df_obj.loc[j, 'id_device'] in df_temp_acc['id_device'].values) and (current_timestamp == 2):
                            violations = random.randint(0, 5)

                        # 获取sr的设备类型
                        sr_device_type = switcher.get(str(df_obj.loc[j, 'device_type']))

                        try:
                            client.send_violation_record(
                                sp_id=sp_id,
                                sr_id=sr_id,
                                sr_type=sr_device_type,
                                timestamp=current_timestamp,
                                violations=violations
                            )
                            print(f"Sent record: {sp_id} -> {sr_id} ({sr_device_type})")
                        except Exception as e:
                            print(f"Error sending record: {e}")

        print("All violation records sent")