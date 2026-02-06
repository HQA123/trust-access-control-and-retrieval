import pandas as pd
import numpy as np

'''
    为每个Edge Server筛选服务范围内的点
'''

# 读取 IoT 数据点
# df = pd.read_csv(r'C:\Users\user\Desktop\新建文件夹\SIoT-IoT-Dataset-main\private_devices\output_private_mobile_devices_mean.csv', sep=',')
df = pd.read_csv(r'C:\Users\user\Desktop\新建文件夹\SIoT-IoT-Dataset-main\map_points_pub_mob_sta.csv', sep=',')

# 定义 Edge Server 的位置和服务半径
all_servers = [
    (0.7959183673469387, 0.5102040816326531),
    (0.6326530612244897, 0.44897959183673464),
    (0.36734693877551017, 0.3061224489795918),
    (0.5102040816326531, 0.3877551020408163),
    (0.8163265306122448, 0.7346938775510203),
    (0.5510204081632653, 0.3061224489795918),
    (0.6938775510204082, 0.6326530612244897),
    (0.22448979591836732, 0.5306122448979591),
    (0.24489795918367346, 0.26530612244897955),
    (0.3469387755102041, 0.42857142857142855),
    (0.44897959183673464, 0.5918367346938775)
]

coverage_radius = 0.1  # 服务覆盖半径

# 为每个 Edge Server 筛选服务范围内的点并保存到单独的文本文件
for idx, edge_server in enumerate(all_servers):
    # 计算 IoT 点与 Edge Server 的欧几里得距离
    df['distance_to_server'] = np.sqrt((df['x'] - edge_server[0])**2 + (df['y'] - edge_server[1])**2)

    # 筛选出在服务范围内的 IoT 点
    covered_points = df[df['distance_to_server'] <= coverage_radius]

    # 提取服务范围内的 IoT 点的 ID
    covered_ids = covered_points['id_device'].tolist()

    # 输出结果到文本文件
    output_text = str(covered_ids)
    with open(f'covered_public_points_output_server_{idx + 1}.txt', 'w', encoding='utf-8') as file:
        file.write(output_text)

    print(output_text)