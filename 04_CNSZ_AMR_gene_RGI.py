import os
import glob
import subprocess
os.chdir('')
# 基础路径配置
base_dir = "./assembly_results"
output_base = "./RGI_batch_results"

# 创建输出目录
if not os.path.exists(output_base):
    os.makedirs(output_base)

# 自动获取所有样本的 scaffolds.fasta 路径
# 假设目录结构为：assembly_results/样本名_output/scaffolds.fasta
fasta_files = glob.glob(os.path.join(base_dir, "*_output", "scaffolds.fasta"))

print(f"共发现 {len(fasta_files)} 个样本待处理...")

for fasta_path in fasta_files:
    # 从路径中提取样本名，例如从 'AB-6_output' 提取 'AB-6'
    sample_name = os.path.basename(os.path.dirname(fasta_path)).replace("_output", "")
    output_path = os.path.join(output_base, f"{sample_name}_RGI")

    # 检查是否已经处理过，避免重复运行
    if os.path.exists(f"{output_path}.txt"):
        print(f"跳过已存在的样本: {sample_name}")
        continue

    # 构建 RGI 命令
    # --num_threads: 根据您的服务器配置调整核心数
    cmd = [
        "rgi", "main",
        "--input_sequence", fasta_path,
        "--output_file", output_path,
        "--input_type", "contig",
        "--local",
        "--num_threads", "8",
        "--clean"
    ]

    try:
        print(f"正在分析样本: {sample_name}")
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"样本 {sample_name} 分析失败: {e}")

print("所有样本处理完毕。")
