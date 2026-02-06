import pandas as pd
import os

'''
    筛选出抽样后的objects_description数据
'''

# 读取CSV文件，指定分隔符为分号
df_obj = pd.read_csv(r'C:\Users\user\Desktop\新建文件夹\SIoT-IoT-Dataset-main\objects_description\objects_description.csv', sep=',')

# 删除矩阵特定的行和列
drop_by_index = []
# 删除的device_type列表
device_type_del = [3,5,6,7,8]

# 定义函数以读取文本文件内容并解析为列表
def read_list_from_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
            # 使用 eval 将字符串列表转换为真正的列表
            data_list = eval(content)
            return data_list
    except FileNotFoundError:
        print(f"文件 {file_path} 不存在！")
        return []
    except Exception as e:
        print(f"读取文件 {file_path} 时出错: {e}")
        return []

for idx in range(1,12):
    os.chdir(f'C:\\Users\\user\\Desktop\\新建文件夹\\SIoT-IoT-Dataset-main\\edge server sample{idx}')

    private_file = f'covered_private_points_output_server_{idx}.txt'
    public_file = f'covered_public_points_output_server_{idx}.txt'
    # 选择private id_user
    private_id_user = read_list_from_file(private_file)
    # 选择public id_device
    public_id_device = read_list_from_file(public_file)

    df_obj_copy = df_obj.copy()
    # 条件：需要删除的样本
    drop_condition = (
        df_obj_copy['device_type'].isin(device_type_del) |  # device_type 在 device_type_del 中
        ~(
            df_obj_copy['id_device'].isin(public_id_device) |  # id_device 不在 public_id_device 中
            df_obj_copy['id_user'].isin(private_id_user)      # 且 id_user 不在 private_id_user 中
        )
    )

    # 获取被删除的样本索引
    drop_by_index = df_obj_copy[drop_condition].index.tolist()

    df_obj_copy = df_obj_copy.drop(drop_by_index) # 删除行
    print("drop row successfully!")

    # 将DataFrame保存到CSV文件，不包括索引
    df_obj_copy.to_csv('output_objects_description.csv', index=False)

print("successfully cleaned data!")


