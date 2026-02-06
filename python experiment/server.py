import signal
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
    device_type: str  # 设备类型，用于确定role score
    neighbors_dtm: {}  # 邻居对其的DTM值,{'sp_id': [dtm,timestamp]}
    violation_history: {}  # violation record历史记录,{'sp_id': [[value,timestamp]]}

class TrustServer:
    def __init__(self, port="5555"):
        # 初始化ZMQ
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.PULL)
        self.socket.bind(f"tcp://*:{port}")
        self.socket.setsockopt(zmq.RCVHWM, 100000)  # 设置接收缓冲区
        self.running = True

        # 设备信息存储
        self.devices: Dict[str, Device] = {}

        # Trust相关参数
        self.lambda_decay = 0.4  # 时间衰减因子
        
        # 读取数据
        self.df1 = pd.read_csv('output_OOR.csv', sep=',', header=None)
        self.df2 = pd.read_csv('output_CLOR.csv', sep=',', header=None)
        self.df3 = pd.read_csv('output_sum_SOR.csv', sep=',', header=None)

        # Role scores配置
        self.role_scores = {
            # 私有设备 (较低的基础信任值，因为是个人设备)
            'smartphone': 0.3,  # 普及率高但个人设备
            'car': 0.5,  # 私人车辆，中等信任度
            'smart fitness': 0.2,  # 个人健康设备，可信度较低
            # 公共设备 (较高的基础信任值，因为由机构维护)
            'point of interest': 0.7,  # 公共信息设施
            'environment monitor': 0.9,  # 环境监测设备，高度可信
            'transportation': 0.8,  # 公共交通工具
            'indicator': 0.7,  # 公共显示设备
            'garbage truck': 0.6,  # 市政服务车辆
            'street light': 0.7,  # 市政基础设施
            'parking': 0.6,  # 停车场设施
            'alarms': 0.9  # 安全监控设备，最高可信度
        }

        # 创建日志目录
        self.log_dir = 'device_logs'
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)

        # 创建日志文件
        file_time = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.log_file = f'{self.log_dir}/device_records_{file_time}.csv'

        # 初始化CSV文件头
        with open(self.log_file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                'timestamp',
                'sp_id',
                'sr_id',
                'sr_type',
                'dtm',
                'rtm',
                'rsm',
                'violations',
                'neighbors_count',  # 当前邻居数量
                'violation_history_count'  # 历史违规记录数量
            ])

    def calculate_dtm(self, sp_id: str, sr_id: str, sr_type: str, timestamp: int, violations: int) -> float:
        """计算Direct Trust Metric"""
        device = self.devices[sr_id]
        role_score = self.role_scores.get(sr_type)

        # 计算violation impact
        violation_impact = 0
        if sp_id in device.violation_history:
            for i in reversed(device.violation_history[sp_id]):
                violation_impact += min(i[0] / 10, 1) * (self.lambda_decay ** (timestamp - i[1]))
                if timestamp - i[1] >= 3: # 超过3个时间单位，停止迭代
                    break
        else:
            device.violation_history[sp_id] = []
        violation_impact += min(violations / 10, 1)

        dtm = max(role_score - violation_impact, 0)
        device.violation_history[sp_id].append([violations,timestamp])

        return dtm

    def calculate_rtm(self, neighbors_dtm) -> float:
        """计算Recommender Trust Metric"""
        rtm = 0
        for neighbor in neighbors_dtm.values():
            rtm += neighbor[0]
        return rtm / len(neighbors_dtm) if len(neighbors_dtm) else 0

    def jaccard_similarity(self, sp_id: str, sr_id: str, type: str) -> float:
        """计算Jaccard相似度"""
        switcher = {
            'OOR': self.df1,
            'CLOR': self.df2,
            'SOR': self.df3
        }
        df = switcher.get(type)
        sp_neighbors = set(); sr_neighbors = set()
        for i in range(len(df)):
            if df.iloc[int(sp_id), i] == 1:
                sp_neighbors.add(i)
            if df.iloc[int(sr_id), i] == 1:
                sr_neighbors.add(i)

        # 邻居交集的大小除以邻居并集的大小
        common_neighbors = sp_neighbors & sr_neighbors
        all_neighbors = sp_neighbors | sr_neighbors

        return len(common_neighbors) / len(all_neighbors) if all_neighbors else 0

    def calculate_rsm(self, sp_id: str, sr_id: str, violations: str) -> float:
        """计算Relationship Similarity Metric"""
        oor = self.jaccard_similarity(sp_id, sr_id, 'OOR') if self.df1.iloc[int(sp_id), int(sr_id)] == 0 else 1
        clor = self.jaccard_similarity(sp_id, sr_id, 'CLOR') if self.df2.iloc[int(sp_id), int(sr_id)] == 0 else 1
        sor = self.jaccard_similarity(sp_id, sr_id, 'SOR') if self.df3.iloc[int(sp_id), int(sr_id)] == 0 else 1

        # 模拟网络拓扑因为violation而断开的情况
        punish_factor = 1
        if violations >= 5:
            temp_list = self.devices[sr_id].violation_history[sp_id]
            for i in reversed(temp_list):
                if i[0] >=5:
                    punish_factor *= 0.6
                else:
                    break

        return (0.4 * oor + 0.3 * clor + 0.3 * sor) * punish_factor

    def calculate_final_trust(self, sample_matrix: List, dtm: float, rtm: float, rsm: float) -> float:
        """使用熵权法计算最终trust value"""
        # 归一化
        normalized = sample_matrix / sample_matrix.sum(axis=0)

        # 计算熵值
        entropy = -1 / np.log(len(sample_matrix)) * np.sum(normalized * np.log(normalized), axis=0)

        # 计算权重
        weights = (1 - entropy) / (3 - np.sum(entropy))

        # 计算最终trust value
        return weights[0] * dtm + weights[1] * rtm + weights[2] * rsm

    def signal_handler(self, signum, frame):
        """处理进程信号"""
        print("\nShutting down server...")
        self.running = False
        sys.exit(0)

    def log_device_state(self, sp_id, sr_id, sr_type, dtm, rtm, rsm, violations, timestamp):
        """记录设备状态"""
        device = self.devices[sr_id]

        with open(self.log_file, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                timestamp,
                sp_id,
                sr_id,
                sr_type,
                f"{dtm:.4f}",
                f"{rtm:.4f}",
                f"{rsm:.4f}",
                violations,
                len(device.neighbors_dtm),
                sum(len(v) for v in device.violation_history.values())
            ])

    def run(self):
        # 设置信号处理，接受到信号正常退出程序
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)

        print("Trust Server is running...")
        while self.running:
            try:
                message = self.socket.recv_json()
                sp_id = message['sp_id'] # id是从0开始，但是在description文件中是从1开始
                sr_id = message['sr_id']
                sr_type = message['sr_type']
                timestamp = message['timestamp']
                violations = message['violations']
                if sr_id not in self.devices:
                    self.devices[sr_id] = Device(sr_id, sr_type, {}, {})

                dtm = self.calculate_dtm(sp_id, sr_id, sr_type, timestamp, violations)
                self.devices[sr_id].neighbors_dtm[sp_id] = [dtm, timestamp]
                # experiment2
                if violations >= 5:
                    for sp_id_mal in range(20000, 20030):
                        dtm_experiment2 = self.calculate_dtm(sp_id_mal, sr_id, sr_type, timestamp, 0)
                        self.devices[sr_id].neighbors_dtm[sp_id_mal] = [dtm_experiment2, timestamp]

                neighbors_dtm_temp = {k: v for k, v in self.devices[sr_id].neighbors_dtm.items() if k != sp_id} # 删除自己
                rtm = self.calculate_rtm(neighbors_dtm_temp) #只计算neighbors的RTM,不包括自己
                rsm = self.calculate_rsm(sp_id, sr_id, violations)

                # 记录设备状态
                self.log_device_state(sp_id, sr_id, sr_type, dtm, rtm, rsm, violations, timestamp)

                print(f"Received record: {sp_id} -> {sr_id} ({sr_type})，DTM: {dtm:.4f}, RTM: {rtm:.4f}, RSM: {rsm:.4f}, timestamp: {timestamp}")
            except zmq.error.ContextTerminated:
                break
            except Exception as e:
                print(f"Error processing message: {e}")
                continue

        # 清理资源
        self.socket.close()
        self.context.term()

def run_server(port="5555"):
    server = TrustServer(port)
    server.run()

if __name__ == "__main__":
    print("Starting Trust Server...")
    os.chdir(f'/home/hqa/files/TrustPIR work materials/SIoT-IoT-Dataset-main/edge server sample1')
    # 启动服务器进程
    server_process = Process(target=run_server, args=("5551",))
    server_process.start()

    # # 确保有两个参数
    # if len(sys.argv) != 3:
    #     print("Usage: python server.py <port> <idx>")
    #     sys.exit(1)
    #
    # # 获取命令行参数
    # port = sys.argv[1]
    # idx = sys.argv[2]
    #
    # print("Starting Trust Server...")
    # os.chdir(f'C:\\Users\\user\\Desktop\\新建文件夹\\SIoT-IoT-Dataset-main\\edge server sample{idx}')
    #
    # # 启动服务器进程
    # server_process = Process(target=run_server, args=(port,))
    # server_process.start()

    try:
        server_process.join()
    except KeyboardInterrupt:
        print("\nReceived keyboard interrupt, shutting down...")
        server_process.terminate()
        server_process.join()


