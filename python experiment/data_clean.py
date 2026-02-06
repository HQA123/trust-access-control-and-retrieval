import pandas as pd

'''
    把移动的private devices转化成一个定点，用平均法表示它在该区域运动
'''

df = pd.read_csv(r'C:\Users\user\Desktop\新建文件夹\SIoT-IoT-Dataset-main\private_devices\private_mobile_devices.csv', sep=',')
# df_obj = pd.read_csv(r'C:\Users\user\Desktop\新建文件夹\SIoT-IoT-Dataset-main\objects_description\objects_description.csv', sep=',')

# 使用groupby()按id_user分组，并使用agg()计算x和y的平均值
averages = df.groupby('id_user').agg({'x': 'mean', 'y': 'mean'})

# 打印结果
print(averages)

print("drop row successfully!")

# 将DataFrame保存到CSV文件，不包括索引
averages.to_csv(r'C:\Users\user\Desktop\新建文件夹\SIoT-IoT-Dataset-main\private_devices\output_private_mobile_devices_mean.csv', index=True, header=True)

