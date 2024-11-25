import numpy as np
import mmap
import matplotlib.pyplot as plt
from scipy.ndimage import gaussian_filter1d
import argparse

# 计算单根天线的频谱
def compute_single_antennas_spectrum(filename, sample_rate, nchan):
    with open(filename, 'r+b') as f:
        fmap = mmap.mmap(f.fileno(), 0)
        tseries = np.frombuffer(fmap[:2 * nchan], dtype=np.int8).astype(np.float32)
        tseries -= np.mean(tseries)  # 去除直流分量

        # 傅里叶变换计算频谱
        tempspec = np.fft.fft(tseries)
        fmap.close()

    # 获取正频率部分（频谱的前半部分）
    spectrum = np.abs(tempspec[:nchan // 2]) ** 2
    return spectrum

def main():
    # 设置命令行参数
    parser = argparse.ArgumentParser(description="Compute and plot spectrum for a single antenna.")
    parser.add_argument('--file', required=True, help="Path to the .dat file from the antenna.")
    args = parser.parse_args()

    # 固定的采样率和通道数
    sample_rate = 1000000000  # 1000MSps (1 GHz)
    nchan = 4096  # 通道数

    # 从命令行获取文件路径
    filename = args.file

    # 计算单根天线的频谱
    spectrum = compute_single_antennas_spectrum(filename, sample_rate, nchan)

    # 计算频率向量
    freq_start = 1000  # 1 GHz
    freq_end = 1500    # 1.5 GHz
    freq = np.linspace(freq_start, freq_end, nchan // 2)  # 创建频率范围

    # 对频谱数据进行平滑处理（使用高斯滤波）
    smooth_spec = gaussian_filter1d(spectrum, sigma=5)  # 你可以调整sigma值来控制平滑度

    # 绘制平滑后的频谱图
    plt.figure(figsize=(10, 6))
    plt.plot(freq, smooth_spec, label='Smoothed Spectrum', color='blue')
    plt.axvline(x=1420, color='red', linestyle='--', label='21cm Line (1420 MHz)')
    plt.yscale('log')  # 对数坐标
    plt.xlabel('Frequency (MHz)')
    plt.ylabel('Amplitude (Normalized Power Spectrum)')
    plt.title('Smoothed Spectrum of Single Antenna')
    plt.legend()
    plt.grid()

    # 保存平滑后的频谱图为 PNG 格式
    plt.savefig("smoothed_single_antenna_spectrum.png", dpi=300)  # 保存为 PNG 图像
    plt.show()

    # 保存频谱结果为 NumPy 数组
    np.save("single_antenna_spectrum.npy", spectrum)
    print("Saved single antenna spectrum to single_antenna_spectrum.npy and smoothed_single_antenna_spectrum.png.")

if __name__ == "__main__":
    main()

