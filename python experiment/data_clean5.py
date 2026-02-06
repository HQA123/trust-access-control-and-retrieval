import pandas as pd

'''
    把移动的public devices转化成一个定点，用平均法表示它在该区域运动
'''

df = pd.read_csv(r'C:\Users\51901\OneDrive\Desktop\新建文件夹\dataset\SIoT-IoT-Dataset-main\SIoT-IoT-Dataset-main\public_devices\public_mobile_devices.csv', sep=',')
# df_obj = pd.read_csv(r'C:\Users\user\Desktop\新建文件夹\SIoT-IoT-Dataset-main\objects_description\objects_description.csv', sep=',')

# 使用groupby()按id_user分组，并使用agg()计算x和y的平均值
averages = df.groupby('id_device').agg({'x': 'mean', 'y': 'mean'})

# 打印结果
print(averages)

print("drop row successfully!")

# 将DataFrame保存到CSV文件，不包括索引
averages.to_csv(r'C:\Users\51901\OneDrive\Desktop\新建文件夹\dataset\SIoT-IoT-Dataset-main\SIoT-IoT-Dataset-main\public_devices\output_public_mobile_devices_mean.csv', index=True, header=True)

