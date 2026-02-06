% 加载CSV文件
data = readtable('aligned_results2.csv');

% 绘制所有设备类型的 trust values
figure;
hold on;

% 获取列名（即设备类型）
column_names = {'Smartphone','Car','Smart Fitness','Point of Interest', ...
                'Environment Monitor','Transportation','Garbage Truck', ...
                'Street Light','Parking','Alarms'};

% 使用高对比度颜色
colors = lines(length(column_names));  % 获取颜色序列

% 为每个设备类型绘制曲线
for i = 1:length(column_names)
    % 按索引获取设备类型的 mean 值
    device_mean = data{:, i};  % 使用索引提取数据列
    
    % 动态生成时间点
    time_points = linspace(0, 3, length(device_mean));
    
    % 绘制主要的线条并包含图例
    if i<= 3
        plot(time_points, device_mean, 'Color', colors(i, :), ...
             'LineWidth', 1.5, 'DisplayName', column_names{i});
        % 稀疏显示标记点（每隔30个点显示一个），不添加到图例中
        sparse_indices = 1:30:length(device_mean);
        plot(time_points(sparse_indices), device_mean(sparse_indices), ...
             'o', 'Color', colors(i, :), 'MarkerFaceColor', colors(i, :), ...
             'MarkerSize', 5, 'HandleVisibility', 'off');  
    elseif i<=7
        plot(time_points, device_mean, 'Color', colors(i, :), ...
             'LineWidth', 1.5, 'DisplayName', column_names{i});
        % 稀疏显示标记点（每隔30个点显示一个），不添加到图例中
        sparse_indices = 1:30:length(device_mean);
        plot(time_points(sparse_indices), device_mean(sparse_indices), ...
             '^', 'Color', colors(i, :), 'MarkerFaceColor', colors(i, :), ...
             'MarkerSize', 5, 'HandleVisibility', 'off');  
    elseif i<=11
        plot(time_points, device_mean, 'Color', colors(i, :), ...
             'LineWidth', 1.5, 'DisplayName', column_names{i});
        % 稀疏显示标记点（每隔30个点显示一个），不添加到图例中
        sparse_indices = 1:30:length(device_mean);
        plot(time_points(sparse_indices), device_mean(sparse_indices), ...
             '*', 'Color', colors(i, :), 'MarkerFaceColor', colors(i, :), ...
             'MarkerSize', 5, 'HandleVisibility', 'off');  
    end
end

% 添加标题和标签
set(gca,'FontSize',14);
xlabel('Time Period (T)', 'FontSize', 16);
ylabel('Trust Value', 'FontSize', 16);

% 设置横坐标刻度为 0 到 3
xticks(0:1:3);

% 显示图例
legend('show', 'Location', 'best', 'FontSize', 13);

% 调整布局
hold off;
