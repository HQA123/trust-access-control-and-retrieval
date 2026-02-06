% 第一张图
figure;
hold on;
plot(1:10, rand(1, 10), 'r', 'DisplayName', 'Red Line');
plot(1:10, rand(1, 10), 'b', 'DisplayName', 'Blue Line');
h1 = legend('show');
title('Plot 1');

% 第二张图
figure;
hold on;
plot(1:10, rand(1, 10), 'g', 'DisplayName', 'Green Line');
plot(1:10, rand(1, 10), 'k', 'DisplayName', 'Black Line');
h2 = legend('show');
title('Plot 2');

% 完全复制图例
copyobj(h1, gca);  % 将 h1 (第一张图的图例) 复制到第二张图的当前坐标轴
