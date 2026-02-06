% 数据定义
data = [
    0.528813559, 0.639774859, 0.685152057, 0.696840307, 0.733990148, 0.735152488;  % KND21
    0.183074266, 0.715506716, 0.815315315, 0.868817204, 0.93306288, 0.9500998;    % HLX23
    0.471502591, 0.782214156, 0.920754717, 0.966165414, 0.97731569, 0.982889734   % Ours
];

% 定义标签
categories = {'0.5', '1', '1.5', '2', '2.5', '3'};
models = {'KND21', 'HLX23', 'Ours'};

% 绘制条形图
figure;
b = bar(data', 'grouped');  % 绘制分组条形图
b(1).FaceColor = [0 1 0];
b(2).FaceColor = [1 0 0];
b(3).FaceColor = [0 0 1];

% 添加轴标签和标题
set(gca,'FontSize',14);
xlabel('Time Period (T)', 'FontSize', 16);
ylabel('Trust Value', 'FontSize', 16);
set(gca, 'XTickLabel', categories, 'FontSize', 14);

% 显示图例
legend(models, 'Location', 'best', 'FontSize', 13);

% 显示网格线
grid on;
