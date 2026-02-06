import os
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# 存储所有服务器的数据
average_trust_values = {}

# 遍历所有服务器
for idx in range(1, 12):
    os.chdir(f'C:\\Users\\user\\Desktop\\新建文件夹\\SIoT-IoT-Dataset-main\\edge server sample{idx}\\device_logs')

    df = pd.read_csv("device_records.csv")
    weights = pd.read_csv("output_weights.csv")

    # 过滤 timestamp = 1
    df_filtered = df[df["timestamp"] == 1].copy()

    # 计算 trust value
    df_filtered["trust_value"] = (
            weights.iloc[0].values * df_filtered["dtm"] +
            weights.iloc[1].values * df_filtered["rtm"] +
            weights.iloc[2].values * df_filtered["rsm"]
    )

    # 按 sr_type 分组，计算平均值
    avg_trust = df_filtered.groupby("sr_type")["trust_value"].mean()

    # 存储结果
    average_trust_values[f"Server {idx}"] = avg_trust

# 将结果转换为 DataFrame
result_df = pd.DataFrame(average_trust_values).fillna(0)  # 若某些 sr_type 在某服务器中无记录，则填充为0

# 转换 DataFrame 为字符串并替换 0 为指定字符
annot_data = result_df.applymap(lambda x: f"{x:.2f}" if x != 0 else "NA")

# 修改 y 轴标签，使每个单词的首字母大写
result_df.index = result_df.index.str.title()

# 绘制热力图
plt.figure(figsize=(12, 8))
sns.heatmap(
    result_df,
    annot=annot_data,  # 使用自定义的标注数据
    fmt="",            # 禁用默认数字格式
    cmap="YlGnBu",
    cbar=True,
    annot_kws={"size": 12}  # 热图内标注字体大小
)

plt.xlabel("Edge Servers", fontsize=16)  # 设置横轴标签字体大小
plt.ylabel("Type of Requester", fontsize=16)  # 设置纵轴标签字体大小
plt.tick_params(axis='both', which='major', labelsize=10.5)  # 调整主刻度字体大小
plt.tight_layout()

# 保存或展示热力图
plt.savefig("heatmap_with_na.png")
plt.show()