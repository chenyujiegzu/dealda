import numpy as np
import matplotlib.pyplot as plt

# 加载 .npy 文件
avspec = np.load('combined_spectrum.npy')

# 打印数组的形状和部分数据，检查它的内容
print(f"Shape of the spectrum: {avspec.shape}")
print(f"Spectrum data (first 10 values): {avspec[:10]}")

# 绘制频谱
plt.plot(avspec)
plt.yscale('log')  # 如果数据差异很大，可以使用对数坐标
plt.xlabel('Frequency Channel')
plt.ylabel('Amplitude')
plt.title('Combined Spectrum')
plt.show()

