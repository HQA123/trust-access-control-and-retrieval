import os
import numpy as np
import pandas as pd

def calculate_final_trust(sample_matrix: np.ndarray) -> np.ndarray:
    """使用熵权法计算最终trust value"""
    # 归一化
    normalized = sample_matrix / sample_matrix.sum(axis=0)

    # 处理可能出现的0值(log0未定义)
    normalized = np.where(normalized == 0, 1e-10, normalized)

    # 计算熵值
    entropy = -1 / np.log(len(sample_matrix)) * np.sum(normalized * np.log(normalized), axis=0)

    # 计算权重
    weights = (1 - entropy) / (3 - np.sum(entropy))

    # 计算最终trust value
    return weights

if __name__ == "__main__":
    for idx in range(1, 12):
        os.chdir(f'C:\\Users\\user\\Desktop\\新建文件夹\\SIoT-IoT-Dataset-main\\edge server sample{idx}\\device_logs')

        df = pd.read_csv('device_records.csv', sep=',')
        sample_matrix = df[['dtm', 'rtm', 'rsm']].to_numpy()
        result = calculate_final_trust(sample_matrix)

        # 将结果转换为 DataFrame
        result_df = pd.DataFrame(result, columns=["Weight"])

        # 保存为 CSV 文件
        result_df.to_csv('output_weights.csv', index=False, header=True)