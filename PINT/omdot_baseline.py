# Yujie Chen, gs.yujiechen23@gzu.edu.cn, 2026/4/25
# Updated with GLSFitter and Red Noise support

import os
import copy
import argparse
import numpy as np
import astropy.units as u
import matplotlib.pyplot as plt
from pint.models import get_model
from pint.toa import get_TOAs
from pint.simulation import make_fake_toas_uniform
from pint.fitter import GLSFitter
from pint.models.noise_model import PLRedNoise
from pint.models.parameter import floatParameter
import pint.logging

def str2bool(v):
    if isinstance(v, bool):
        return v
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')

def main():
    parser = argparse.ArgumentParser(
        description="Predict the required observing baseline for pulsar OMDOT detection with Red Noise.",
        formatter_class=lambda prog: argparse.ArgumentDefaultsHelpFormatter(prog, max_help_position=50)
    )

    # 1. 基础文件与物理参数
    parser.add_argument('-par', '--parfile', type=str, required=True, help="Input pulsar parameter (.par) file.")
    parser.add_argument('-set_omdot', type=float, default=0.0043, help="Theoretical OMDOT value (deg/yr).")

    # 2. 模拟时间设置
    parser.add_argument('-start_MJD', type=float, default=52609, help="Starting MJD for simulation.")
    parser.add_argument('--fit_start', type=float, default=5.0, help="Start of baseline range (years).")
    parser.add_argument('--duration', type=float, default=20.0, help="End of baseline range (years).")
    parser.add_argument('-fit_lengths', type=float, default=0.5, help="Step size for baseline range (years).")
    parser.add_argument('-TOAs_error', type=float, default=0.75, help="TOA precision in microseconds.")
    parser.add_argument('--cadence', type=float, default=7.0, help="Observation cadence in days.")
    parser.add_argument('-obs', type=str, default="fast", help="Observatory name.")

    # 3. 红噪声设置
    parser.add_argument('--rn_amp', type=float, default=1e-13, help="Red noise amplitude (RNAMP).")
    parser.add_argument('--rn_idx', type=float, default=4.0, help="Red noise spectral index (RNIDX).")

    # 4. 参数冻结控制 (True = 不参与拟合, False = 参与拟合)
    parser.add_argument('--RAJ-frozen', type=str2bool, default=False, help="Freeze Right Ascension (RAJ).")
    parser.add_argument('--DECJ-frozen', type=str2bool, default=False, help="Freeze Declination (DECJ).")
    parser.add_argument('--F0-frozen', type=str2bool, default=False, help="Freeze pulse frequency (F0).")
    parser.add_argument('--F1-frozen', type=str2bool, default=False, help="Freeze frequency derivative (F1).")
    parser.add_argument('--PMRA-frozen', type=str2bool, default=True, help="Freeze proper motion in RA (PMRA).")
    parser.add_argument('--PMDEC-frozen', type=str2bool, default=True, help="Freeze proper motion in DEC (PMDEC).")
    parser.add_argument('--T0-frozen', type=str2bool, default=False, help="Freeze epoch of periastron (T0).")
    parser.add_argument('--PB-frozen', type=str2bool, default=False, help="Freeze binary period (PB).")
    parser.add_argument('--A1-frozen', type=str2bool, default=False, help="Freeze projected semi-major axis (A1).")
    parser.add_argument('--ECC-frozen', type=str2bool, default=False, help="Freeze eccentricity (ECC).")
    parser.add_argument('--OM-frozen', type=str2bool, default=False, help="Freeze longitude of periastron (OM).")
    parser.add_argument('--OMDOT-frozen', type=str2bool, default=False, help="Freeze rate of periastron advance (OMDOT).")

    # 5. 输出控制
    parser.add_argument('-O', '--output_tim', type=str, default="simulated_total.tim", help="Output simulated TOAs.")
    parser.add_argument('-save_image', type=str, default=None, help="Save plot path.")
    parser.add_argument('-sigma_threshold', type=str, default="7", help="Detection thresholds (e.g., '3,7').")
    parser.add_argument('--seed', type=int, default=None, help="Random seed.")

    args = parser.parse_args()

    # 绘图配置
    plt.rcParams['font.family'] = 'STIXGeneral'
    plt.rcParams['mathtext.fontset'] = 'stix'
    pint.logging.setup(level="WARNING")

    # 1. 加载模型并应用初始设置
    m = get_model(args.parfile)
    
    # 注入红噪声组件
    if "PLRedNoise" not in m.components:
        m.add_component(PLRedNoise())
    m.RNAMP.value = args.rn_amp
    m.RNIDX.value = args.rn_idx

    # 设置进动理论值
    m.OMDOT.value = args.set_omdot

    # 设置参数冻结状态
    m.RAJ.frozen = args.RAJ_frozen
    m.DECJ.frozen = args.DECJ_frozen
    m.F0.frozen = args.F0_frozen
    m.F1.frozen = args.F1_frozen
    m.PMRA.frozen = args.PMRA_frozen
    m.PMDEC.frozen = args.PMDEC_frozen
    m.T0.frozen = args.T0_frozen
    m.PB.frozen = args.PB_frozen
    m.A1.frozen = args.A1_frozen
    m.ECC.frozen = args.ECC_frozen
    m.OM.frozen = args.OM_frozen
    m.OMDOT.frozen = args.OMDOT_frozen

    # 2. 模拟循环
    start_mjd = args.start_MJD
    baselines_yr = np.arange(args.fit_start, args.duration + 1e-5, args.fit_lengths)
    toa_err = args.TOAs_error * u.us
    
    if args.seed is not None:
        np.random.seed(args.seed)

    omdot_errors = []
    print(f"{'Baseline(yr)':<15} {'OMDOT_Error(deg/yr)':<20}")

    for yr in baselines_yr:
        m_loop = copy.deepcopy(m)
        duration_days = yr * 365.25
        n_pts = int(duration_days / args.cadence)

        # 生成模拟数据
        ts = make_fake_toas_uniform(
            startMJD=start_mjd,
            endMJD=start_mjd + duration_days,
            ntoas=n_pts,
            model=m, # 使用包含理论OMDOT和红噪声的模型生成
            obs=args.obs,
            error=toa_err,
            add_noise=True,
            include_bipm=False
        )

        # 使用 GLSFitter 进行拟合
        f = GLSFitter(ts, m_loop)
        f.fit_toas()

        err = f.model.OMDOT.uncertainty_value
        val = f.model.OMDOT.value
        omdot_errors.append(err)

        print(f"{yr:<15.2f} 测量值: {val:.8f} ± {err:.8f}")

    # 保存最后一份模拟数据
    ts.write_TOA_file(args.output_tim, format="tempo2")
    print(f"\nFinal TOA file saved to: {args.output_tim}")

    # 4. 绘图
    plt.figure(figsize=(9, 7))
    sigmas = [float(s.strip()) for s in args.sigma_threshold.split(',')]
    colors = ['red', 'orange', 'green', 'purple', 'magenta']
    
    for i, sig in enumerate(sigmas):
        plt.axhline(y=args.set_omdot/sig, color=colors[i % len(colors)], 
                    linestyle='--', lw=2, label=rf'${sig:g}\sigma$ threshold')

    plt.plot(baselines_yr, omdot_errors, 'o', color='C0', markersize=8, label='Simulated data')
    plt.yscale('log')
    plt.xlabel('Timing baseline (yr)', fontsize=20)
    plt.ylabel(r'Uncertainty (deg/yr)', fontsize=20)
    plt.tick_params(axis='both', which='major', labelsize=18)
    plt.tick_params(axis='both', which='minor', labelsize=12)
    plt.legend(loc='upper right', fontsize=18, frameon=True)
    plt.tight_layout()

    if args.save_image:
        plt.savefig(args.save_image, dpi=300)
    plt.show()

if __name__ == "__main__":
    main()
