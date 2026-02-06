import os
import random
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy import interpolate
from typing import Dict, List, Tuple, Optional



class TrustValueAnalyzer:
    def __init__(self, log_path: str, obj_desc_path: str, sample_path: str, weights: List[float] = None):
        self.weights = weights
        self.device_types = [
            'smartphone', 'car', 'smart fitness', 'point of interest',
            'environment monitor', 'transportation', 'indicator',
            'garbage truck', 'street light', 'parking', 'alarms'
        ]
        # 读取数据
        self.log_df = pd.read_csv(log_path, sep=',')
        self.obj_desc = pd.read_csv(obj_desc_path, sep=',')
        self.sample = pd.read_csv(sample_path, sep=',')
        # 初始化存储结构
        self.device_to_srid = {}
        self.sample_srids = []
        self.filtered_log = None
        self.sr_type_log = {type_: {} for type_ in self.device_types}
        self.aligned_results = {}

    def create_device_mapping(self):
        """创建设备ID到sr_id的映射"""
        for idx, row in self.obj_desc.iterrows():
            self.device_to_srid[row['id_device']] = idx

    def find_sample_srids(self):
        """找出样本中设备对应的sr_id"""
        for device_id in self.sample['id_device']:
            if device_id in self.device_to_srid:
                self.sample_srids.append(self.device_to_srid[device_id])
        print("Sample设备对应的sr_ids:", sorted(self.sample_srids))

    def filter_logs(self):
        """过滤出相关设备的日志"""
        self.filtered_log = self.log_df[self.log_df['sr_id'].isin(self.sample_srids)].copy()
        print("\n数据统计:")
        print(f"原始log记录数: {len(self.log_df)}")
        print(f"筛选后记录数: {len(self.filtered_log)}")
        print(f"涉及的sr_id数量: {self.filtered_log['sr_id'].nunique()}")

    def calculate_trust_values(self):
        """计算每个设备的trust values"""
        for id in self.sample_srids:
            temp_df = self.filtered_log[self.filtered_log['sr_id'] == id]
            if len(temp_df) > 0:
                # 找到并保留最后一个timestamp=1及之后的数据
                last_timestamp_1_idx = temp_df[temp_df['timestamp'] == 1].index[-1] \
                    if len(temp_df) > 0 else 0
                temp_df = temp_df[temp_df.index >= last_timestamp_1_idx]

                # 计算trust values
                trust_values = (temp_df['dtm'] * self.weights[0] +
                                temp_df['rtm'] * self.weights[1] +
                                temp_df['rsm'] * self.weights[2]).round(4).values

                self.sr_type_log[temp_df['sr_type'].values[0]][id] = trust_values

        return self.sr_type_log

    def align_and_average(self, type_records: Dict, target_length: int) -> Tuple[
        Optional[np.ndarray], Optional[np.ndarray], int]:
        """对同类型设备的trust value序列进行插值对齐和平均"""
        if not type_records:
            return None, None, 0

        aligned_values = []
        for device_values in type_records.values():
            if len(device_values) > 1:
                x_original = np.arange(len(device_values))
                x_new = np.linspace(0, len(device_values) - 1, target_length)
                f = interpolate.interp1d(x_original, device_values, kind='linear')
                aligned_values.append(f(x_new))
            elif len(device_values) == 1:
                aligned_values.append(np.full(target_length, device_values[0]))

        if aligned_values:
            aligned_array = np.array(aligned_values)
            return np.mean(aligned_array, axis=0), np.std(aligned_array, axis=0), len(aligned_values)
        return None, None, 0

    def process_data(self, sr_type_log):
        """处理所有数据"""
        # 找出最长序列长度
        max_length = max(len(values) for devices in sr_type_log.values()
                         for values in devices.values() if devices)
        print(f"最长序列长度: {max_length}")

        # 对齐和平均
        for sr_type, devices in sr_type_log.items():
            if devices:
                mean_values, std_values, num_devices = self.align_and_average(devices, max_length)
                if mean_values is not None:
                    self.aligned_results[sr_type] = {
                        'mean': mean_values,
                        'std': std_values,
                        'num_devices': num_devices
                    }

    def plot_results(self, save_path='trust_values_aligned2.png'):
        """绘制结果图表"""
        plt.figure(figsize=(12, 6))
        x = np.arange(len(next(iter(self.aligned_results.values()))['mean']))

        for sr_type, data in self.aligned_results.items():
            plt.plot(x, data['mean'], label=f'{sr_type}')

        plt.title('Average Trust Values by Device Type (Aligned Time Series)')
        plt.xlabel('Time Sequence')
        plt.ylabel('Trust Value')

        # Change x-axis labels to [0, 1, 2, 3] and position legend inside
        # plt.xticks([0, 1, 2, 3])
        plt.legend(bbox_to_anchor=(1.05, 1), loc='upper right')  # Inside, top-right
        plt.grid(True)

        # Adjust to remove space below y-axis
        plt.tight_layout()
        plt.subplots_adjust(bottom=0.1)  # Remove extra space below y-axis
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.show()

    def save_means_to_csv(self, output_path='aligned_results2.csv'):
        """
        将所有 mean 值保存到一个 CSV 文件中
        """
        combined_data = {}

        for sr_type, data in self.aligned_results.items():
            column_name = f'{sr_type}'
            combined_data[column_name] = data['mean']

        # 转换为 DataFrame 并保存
        df = pd.DataFrame(combined_data)
        df.to_csv(output_path, index=False)
        print(f"已保存所有 mean 值到文件: {output_path}")

    def save_results(self):
        """保存处理结果"""
        print("\n各类型设备统计信息:")
        for sr_type, data in self.aligned_results.items():
            print(f"\n{sr_type}:")
            print(f"设备数量: {data['num_devices']}")
            print(f"平均trust value: {np.mean(data['mean']):.4f}")
            print(f"标准差: {np.mean(data['std']):.4f}")

            # 保存到CSV
            pd.DataFrame({
                'time_point': np.arange(len(data['mean'])),
                'mean_trust': data['mean'],
                'std_trust': data['std']
            }).to_csv(f'{sr_type}_aligned_trust_values.csv', index=False)

    def run(self):
        """运行完整的分析流程"""
        self.create_device_mapping()
        self.find_sample_srids()
        self.filter_logs()
        # sr_type_log = self.calculate_trust_values()
        # self.process_data()
        # self.plot_results()
        # self.save_results()

if __name__ == "__main__":
    device_types = [
        'smartphone', 'car', 'smart fitness', 'point of interest',
        'environment monitor', 'transportation', 'indicator',
        'garbage truck', 'street light', 'parking', 'alarms'
    ]
    sr_type_log_agg = {type_: {} for type_ in device_types}
    for idx in range(1, 12):
        os.chdir(f'C:\\Users\\user\\Desktop\\新建文件夹\\SIoT-IoT-Dataset-main\\edge server sample{idx}')
        weight_list = pd.read_csv('device_logs\\output_weights.csv', sep=',')['Weight'].tolist()
        analyzer = TrustValueAnalyzer(
            log_path='device_logs\\device_records.csv',
            obj_desc_path='output_objects_description.csv',
            sample_path='sample_10_percent_2.csv',
            weights=weight_list
        )
        analyzer.run()

        # 添加整合的trust values
        sr_type_log = analyzer.calculate_trust_values()
        for k, v in sr_type_log.items():
            for v2 in v.values():
                sr_type_log_agg[k][random.randint(0, 10000)] = v2

    analyzer.process_data(sr_type_log_agg)
    analyzer.plot_results()
    analyzer.save_means_to_csv()