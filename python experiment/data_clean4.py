import pandas as pd

# df = pd.read_csv(r'C:\Users\user\Desktop\新建文件夹\SIoT-IoT-Dataset-main\private_devices\private_mobile_devices.csv', sep=',')
df_obj = pd.read_csv(r'F:\新建文件夹\dataset\SIoT-IoT-Dataset-main\SIoT-IoT-Dataset-main\objects_description\objects_description.csv', sep=',')

# 删除矩阵特定的行和列
drop_by_index = []
# 删除的device_type列表
device_type_del = [3,5,6,7,8]

# 遍历DataFrame的每一行
for index, row in df_obj.iterrows():
    # 检查device_type是否为特定值
    if row['device_type'] in device_type_del:
        # 如果是，则将对应的device_name添加到列表中
        drop_by_index.append(index)
        print("row is", index)

df_obj = df_obj.drop(drop_by_index) # 删除行
print("drop row successfully!")

# 将DataFrame保存到CSV文件，不包括索引
df_obj.to_csv(r'F:\新建文件夹\dataset\SIoT-IoT-Dataset-main\SIoT-IoT-Dataset-main\objects_description\output_objects_description.csv', index=False, header=True)

