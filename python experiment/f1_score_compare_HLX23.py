import random
from dataclasses import dataclass
from typing import Dict, List, Tuple
import pandas as pd
import csv
import os



def f1_score_factor(sample_dict, df_mal, df_temp_acc):
    mal_list = df_mal['id_device'].values
    acc_list = df_temp_acc['id_device'].values
    TP = 0; FP = 0; FN = 0; TN = 0
    for key in sample_dict.keys():
        if key in mal_list:
            if sample_dict[key] == 1:
                TP += 1
            else:
                FN += 1
        elif key in acc_list:
            if sample_dict[key] == 1:
                FP += 1
            else:
                TN += 1
    return TP, FP, FN, TN

def f1_score(TP, FP, FN):
    precision = TP / (TP + FP) if TP + FP != 0 else 0
    recall = TP / (TP + FN) if TP + FN != 0 else 0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall != 0 else 0
    return f1

if __name__ == "__main__":
    f1_factor = {
        'TP': [0, 0, 0, 0, 0, 0, 0, 0],
        'FP': [0, 0, 0, 0, 0, 0, 0, 0],
        'FN': [0, 0, 0, 0, 0, 0, 0, 0],
        'TN': [0, 0, 0, 0, 0, 0, 0, 0]
    }
    for idx in range(1, 12):
        os.chdir(f'/home/hqa/files/TrustPIR work materials/SIoT-IoT-Dataset-main/edge server sample{idx}')
        df_log = pd.read_csv('device_logs/device_records_HLX23_experiment2.csv', sep=',')
        df_obj = pd.read_csv('output_objects_description.csv', sep=',')
        df_mal = pd.read_csv('sample_10_percent_1.csv', sep=',')
        df_temp_acc = pd.read_csv('sample_10_percent_2.csv', sep=',')

        # 创建sample的识别字典
        sample_dict = {}
        for i in range(len(df_temp_acc)):
            sample_dict[df_temp_acc.loc[i, 'id_device']] = 0
        for i in range(len(df_mal)):
            sample_dict[df_mal.loc[i, 'id_device']] = 0

        f1_list2 = []
        f1_factor2 = {
        'TP': [0, 0, 0, 0, 0, 0, 0, 0],
        'FP': [0, 0, 0, 0, 0, 0, 0, 0],
        'FN': [0, 0, 0, 0, 0, 0, 0, 0],
        'TN': [0, 0, 0, 0, 0, 0, 0, 0]
    }
        count = 0
        for i in range(len(df_log)):
            print('processing:', i, '.idx:', idx)
            sr = df_log.loc[i, 'sr_id']
            if df_obj.loc[sr, 'id_device'] in sample_dict.keys():
                if df_log.loc[i, 'Trust'] <= 0.3:
                    sample_dict[df_obj.loc[sr, 'id_device']] = 1
                else:
                    sample_dict[df_obj.loc[sr, 'id_device']] = 0

            # 每隔len(df_log)/10条数据统计一次f1_score
            if (i+1) % (len(df_log) // 8) == 0:
                f1_factor2['TP'][count], f1_factor2['FP'][count], f1_factor2['FN'][count], f1_factor2['TN'][count] = f1_score_factor(sample_dict, df_mal, df_temp_acc)
                count += 1

        # 将f1_factor2加到f1_factor中
        for key in f1_factor.keys():
            for i in range(len(f1_factor[key])):
                f1_factor[key][i] += f1_factor2[key][i]
        print(f1_factor2)

    f1 = []
    for i in range(len(f1_factor[key])):
        f1.append(f1_score(f1_factor['TP'][i], f1_factor['FP'][i], f1_factor['FN'][i]))
    # 将结果转换为 DataFrame
    result_df = pd.DataFrame(f1, columns=["F1"])
    # 保存为 CSV 文件
    result_df.to_csv('output_F1_HLX23_experiment2.csv', index=False, header=True)
    print(f1)
