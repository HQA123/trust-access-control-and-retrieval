import pandas as pd
import os
'''
    抽取10%的样本
'''

for idx in range(1,12):
    os.chdir(f'C:\\Users\\user\\Desktop\\新建文件夹\\SIoT-IoT-Dataset-main\\edge server sample{idx}')

    # 加载数据
    df = pd.read_csv('output_objects_description.csv', sep=',')

    # 计算10%的样本大小
    sample_size = int(len(df) * 0.10)

    # 第一次抽取10%的样本
    sample_df1 = df.sample(n=sample_size, replace=False, random_state=1)

    # 第二次抽取10%的样本
    sample_df2 = df.sample(n=sample_size, replace=False, random_state=2)

    # 保存第一个样本到新的CSV文件
    sample_df1.to_csv('sample_10_percent_1.csv', index=False)

    # 保存第二个样本到新的CSV文件
    sample_df2.to_csv('sample_10_percent_2.csv', index=False)