import pandas as pd
import numpy as np
import os

'''
    将关系举证SOR1和SOR2合并成SOR矩阵
'''

for idx in range(1,12):
    os.chdir(f'C:\\Users\\user\\Desktop\\新建文件夹\\SIoT-IoT-Dataset-main\\edge server sample{idx}')

    # 读取CSV文件，指定分隔符为分号
    df1 = pd.read_csv('output_SOR.csv', sep=',', header=None)
    df2 = pd.read_csv('output_SOR2.csv', sep=',', header=None)

    # 相加两个DataFrame
    sum_df = df1 + df2

    # 对于每个元素，取它与1的较小值
    result = np.minimum(sum_df, 1)

    # 将DataFrame保存到CSV文件，不包括索引
    sum_df.to_csv('output_sum_SOR.csv', index=False, header=False)

print("successfully cleaned data!")

