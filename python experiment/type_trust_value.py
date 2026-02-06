import pandas as pd
import numpy as np


def analyze_trust_by_type(log_file, timestamp=1, weights=[0.41820, 0.40630, 0.17550]):
    # 读取CSV文件
    df = pd.read_csv(log_file)

    # 筛选特定timestamp的数据
    df_time = df[df['timestamp'] == timestamp]

    # 按sr_type分组计算平均值
    grouped = df_time.groupby('sr_type').agg({
        'dtm': 'mean',
        'rtm': 'mean',
        'rsm': 'mean'
    }).round(4)

    # 计算加权trust value
    grouped['trust_value'] = (grouped['dtm'] * weights[0] +
                              grouped['rtm'] * weights[1] +
                              grouped['rsm'] * weights[2]).round(4)

    # 添加每种类型的设备数量
    grouped['device_count'] = df_time.groupby('sr_type').size()

    print("\n设备类型统计:")
    print("=" * 80)
    print(grouped)

    print("\n总体统计:")
    print("=" * 80)
    total_devices = grouped['device_count'].sum()
    weighted_avg = (grouped['trust_value'] * grouped['device_count']).sum() / total_devices
    print(f"总设备数: {total_devices}")
    print(f"加权平均trust value: {weighted_avg:.4f}")

    return grouped

# 使用示例
results = analyze_trust_by_type(r"F:\新建文件夹\dataset\SIoT-IoT-Dataset-main\SIoT-IoT-Dataset-main\edge server sample1\device_records_20241124_115542.csv")
print(results['trust_value'].values)