import numpy as np
import mmap
import matplotlib.pyplot as plt
from scipy.ndimage import gaussian_filter1d
import argparse

# 合成天线信号并计算每对天线的相对延迟
def combine_signals(filenames, sample_rate, nchan):
    n_antennas = len(filenames)
    avspec = np.zeros(nchan // 2)

    # 初始化信号容器
    signals = np.zeros((n_antennas, nchan), dtype=np.float32)

    # 处理每个天线的信号
    for i, filename in enumerate(filenames):
        with open(filename, 'r+b') as f:
            fmap = mmap.mmap(f.fileno(), 0)
            tseries = np.frombuffer(fmap[:2 * nchan], dtype=np.int8).astype(np.float32)
            tseries -= np.mean(tseries)

            # 傅里叶变换计算频谱
            tempspec = np.fft.fft(tseries)
            # 确保频谱形状匹配，取正频率部分并填充至 nchan
            if tempspec.size >= nchan:
                signals[i, :] = np.abs(tempspec[:nchan]) ** 2  # 确保频谱大小与 nchan 匹配
            else:
                signals[i, :] = np.pad(np.abs(tempspec) ** 2, (0, nchan - tempspec.size), 'constant')  # 填充信号

            fmap.close()

    # 计算各天线之间的相对延迟（fringe search）
    phase_differences = np.zeros((n_antennas, n_antennas))  # 用于存储相位差矩阵
    for i in range(n_antennas):
        for j in range(i + 1, n_antennas):
            # 对每对天线计算交叉频谱
            cross_spectrum = np.fft.fft(signals[i]) * np.conj(np.fft.fft(signals[j]))
            phase_diff = np.angle(cross_spectrum)  # 计算相位差
            delay_samples = np.argmax(np.abs(np.fft.ifft(phase_diff)))  # 找到最大相位差对应的延迟位置
            delay_seconds = delay_samples / sample_rate
            phase_differences[i, j] = delay_seconds
            phase_differences[j, i] = -delay_seconds  # 对称关系

            # 打印时间延迟和相位差
            print(f"天线 {i} 和 天线 {j} 的相位差: {np.mean(phase_diff):.4f} rad")
            print(f"天线 {i} 和 天线 {j} 的延迟: {delay_seconds * 1e3:.4f} ms")

    # 应用时延修正到信号中
    corrected_signals = np.zeros_like(signals)
    for i in range(n_antennas):
        for j in range(n_antennas):
            if i != j:
                delay_samples = int(phase_differences[i, j] * sample_rate)
                corrected_signals[j, :] = np.roll(signals[j, :], delay_samples)

    # 合成信号
    combined_signal = np.sum(corrected_signals, axis=0)
    # 应用汉宁窗口
    combined_signal *= np.hanning(len(combined_signal))

    # 计算频谱
    tempspec = np.fft.fft(combined_signal)
    avspec += (np.abs(tempspec[:nchan // 2]) ** 2) / len(filenames)

    return avspec, phase_differences

def remove_dc(avspec, freq, dc_freq=1000.0, bandwidth=0.3):
    """去除频谱中 DC（1 GHz）附近的分量"""
    # 创建一个遮罩，去掉 1 GHz 附近的频率
    mask = np.logical_or(freq < (dc_freq - bandwidth), freq > (dc_freq + bandwidth))
    avspec[~mask] = 0  # 将 DC 附近的频谱分量置为 0
    return avspec

def main():
    # 设置命令行参数
    parser = argparse.ArgumentParser(description="Process .dat files and compute phase offset for array synthesis.")
    parser.add_argument('--file', nargs='+', required=True, help="Paths to the .dat files from antennas.")
    args = parser.parse_args()

    # 固定的采样率和通道数
    sample_rate = 1000000000  # 1000MSps (1 GHz)
    nchan = 4096  # 通道数

    # 从命令行获取文件列表
    filenames = args.file

    # 合成天线信号并计算相对延迟
    avspec, phase_differences = combine_signals(filenames, sample_rate, nchan)

    # 计算频率向量
    freq_start = 1.0e3  # 1 GHz
    freq_end = 1.5e3    # 1.5 GHz
    freq = np.linspace(freq_start, freq_end, nchan // 2)  # 创建频率范围

    # 去除 DC（1 GHz）附近的频率分量
    avspec = remove_dc(avspec, freq)

    # 对频谱数据进行平滑处理（使用高斯滤波）
    smooth_spec = gaussian_filter1d(avspec, sigma=5)  # 你可以调整sigma值来控制平滑度

    # 绘制平滑后的频谱图
    plt.figure(figsize=(10, 6))
    plt.plot(freq, smooth_spec, label='Smoothed Combined Spectrum', color='blue')
    plt.axvline(x=1420, color='red', linestyle='--', label='21cm Line (1420 MHz)')
    plt.yscale('log')  # 对数坐标
    plt.xlabel('Frequency (MHz)')
    plt.ylabel('Amplitude (Normalized Power Spectrum)')
    plt.title('Smoothed Combined Amplitude Spectrum')
    plt.legend()
    plt.grid()

    # 保存平滑后的频谱图为 PNG 格式
    plt.savefig("smoothed_combined_spectrum.png", dpi=300)  # 保存为 PNG 图像
    plt.show()

    # 保存频谱结果为 NumPy 数组
    np.save("combined_spectrum.npy", avspec)
    np.save("phase_differences.npy", phase_differences)  # 保存相对延迟结果
    print("Saved combined spectrum to combined_spectrum.npy, smoothed_combined_spectrum.png, and phase_differences.npy.")

if __name__ == "__main__":
    main()

