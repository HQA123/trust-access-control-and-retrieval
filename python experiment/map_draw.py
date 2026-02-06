import matplotlib.pyplot as plt
from matplotlib.patches import Circle
from PIL import Image
import pandas as pd
import numpy as np

# 加载地图图片
img = Image.open(r'C:\Users\user\Desktop\新建文件夹\python experiment\map.png')

# 读取 IoT 点坐标
df = pd.read_csv(r'C:\Users\user\Desktop\新建文件夹\SIoT-IoT-Dataset-main\map_points_pub_mob_sta.csv', sep=',')
x_points = df['x'].tolist()
y_points = df['y'].tolist()
iot_points = list(zip(x_points, y_points))

# 服务覆盖半径 (归一化后的值)
coverage_radius = 0.1

# 生成候选 Edge Server 点（规则网格）
grid_density = 50  # 候选点网格的密度
x_range = np.linspace(0, 1, grid_density)
y_range = np.linspace(0, 1, grid_density)
candidate_servers = [(x, y) for x in x_range for y in y_range]

# 贪心算法选择 Edge Servers
uncovered_points = set(iot_points)
edge_servers = []

# 设置最大服务器数量
max_servers = 12

while uncovered_points and len(edge_servers) < max_servers:
    # 选择覆盖最多点的候选服务器
    best_server = None
    max_covered = 0
    for server in candidate_servers:
        covered = {point for point in uncovered_points if
                   np.linalg.norm(np.array(server) - np.array(point)) <= coverage_radius}
        if len(covered) > max_covered:
            max_covered = len(covered)
            best_server = server

    # 添加最佳服务器并更新已覆盖点
    edge_servers.append(best_server)
    uncovered_points -= {point for point in uncovered_points if
                         np.linalg.norm(np.array(best_server) - np.array(point)) <= coverage_radius}

del edge_servers[-2]
# 提取 Edge Server 的坐标
edge_x, edge_y = zip(*edge_servers)

# 创建图像和坐标轴
fig, ax = plt.subplots()
ax.imshow(img, extent=[0, 1, 0, 1])  # 将图片的坐标设置为0到1

# 绘制 IoT 设备点 (蓝色)
ax.scatter(x_points, y_points, color="blue", marker="o", s=10, label="Public IoT")

# 绘制 Edge Server 点 (橘色) 并标记序号
for idx, (x, y) in enumerate(edge_servers, start=1):
    ax.scatter(x, y, color="orange", marker="o", s=30, label="Edge Servers" if idx == 1 else "")
    # 标记序号
    ax.text(x, y, str(idx), color="white", fontsize=7.5, ha="center", va="center", weight="bold")

# 绘制服务覆盖范围（虚线圆圈）
for x, y in edge_servers:
    circle = Circle((x, y), coverage_radius, color="orange", fill=False, linestyle="--", linewidth=1.5)
    ax.add_patch(circle)

# 设置坐标轴范围
ax.set_xlim(0, 1)
ax.set_ylim(0, 1)

# 添加标题、图例和坐标轴标签
plt.legend()
plt.savefig('edge_server.png',dpi=300, bbox_inches='tight')
plt.show()


# 输出 Edge Server 数量
print(f"Number of Edge Servers: {len(edge_servers)}")
print(edge_servers)
