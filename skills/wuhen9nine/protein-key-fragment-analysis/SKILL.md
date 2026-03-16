---
name: serine-protease-fragment-analysis
description: 蛋白质关键序列片段预测分析。对任意蛋白质家族的多物种FASTA序列执行完整分析流程，提取共识序列并识别关键功能片段、统计氨基酸组成、预测片段主要功能。适用于：（1）用户提到"提取蛋白关键序列/片段"、"分析蛋白保守区"、"预测蛋白功能片段"时，（2）对新物种/类群运行完整分析流程，（3）从已有FASTA序列提取共识序列并识别关键片段，（4）跨物种横向对比关键片段差异，（5）生成结构化分析报告。适用于任何蛋白质家族。
---

# 蛋白质关键序列片段预测分析

> 本流程适用于**任何蛋白质家族**，对多物种 FASTA 序列执行 MSA → 共识序列 → 关键片段识别 → 氨基酸组成统计 → 功能预测的完整分析链路。

## 核心文件

- **主分析脚本**：`scripts/serine_protease_analysis.py`（完整分析流程）
- **批量运行入口**：`scripts/run_full_analysis.py`（多物种批量 + 大样本采样）
- **方法细节**：`references/method.md`
- **功能域参考**：`references/functional_domains.md`（分析新蛋白家族时，在此补充对应 Pfam 保守域）

---

## 快速运行

```bash
# 单物种分析
python3 serine_protease_analysis.py <物种名> <fasta路径>

# 多物种批量分析（推荐）
# 1. 将各物种 .fasta 文件放入 input_clean/ 目录
# 2. 运行批量脚本
python3 run_full_analysis.py
```

---

## 分析流程

### Step 1：序列读取
- 解析标准 FASTA 格式，统计序列数量和长度分布
- **大样本处理**：序列数超过阈值时随机采样（seed=42，保证可复现）

### Step 2：多序列比对（MSA）
- 工具：**ClustalOmega**（`apt install clustalo` 或 `conda install clustalo`）
- 单序列物种跳过 MSA，直接使用原始序列

### Step 3：共识序列提取
- 各位点最高频氨基酸占比 ≥ 阈值（默认 0.5）则写入，否则标 X
- 去除 gap（`-`）后得到连续共识序列

### Step 4：关键片段识别（三维度并行）
1. **已知功能块匹配**：在共识序列中搜索目标蛋白家族的 Pfam 保守域特征序列（需在 `functional_domains.md` 中预先配置）
2. **高保守连续区检测**：保守率 ≥ 90%、长度 ≥ 6aa 的连续区段
3. **保守 Cys 检测**：统计共识序列中 Cys 数量（潜在二硫键网络）

> 分析新蛋白家族时，在 `KNOWN_MOTIFS` 和 `CONSERVED_BLOCKS` 中补充对应的 Pfam 特征序列（来源：Pfam / InterPro / UniProt）。

### Step 4.5：片段氨基酸组成与理化性质分析

对每个关键片段统计各功能类别氨基酸的出现频率：

| 类别 | 氨基酸 |
|------|--------|
| Hydrophobic（疏水性） | V, L, I, M |
| Nucleophilic（亲核性） | S, T, C |
| Aromatic（芳香性） | F, Y, W |
| Amide（酰胺类） | N, Q |
| Acidic（酸性） | D, E |
| Cationic（阳离子性） | H, K, R |
| **排除不统计** | X, A, G, P |

> ⚠️ 此分类体系与 `aa-pair-analysis` 完全一致，A/G/P 排除不统计。

- **主导类别判定**：某类别占比 ≥ 35% 则为该类主导，否则判定为 Mixed（混合型）
- 结果写入 `composition` 字段（含各类别计数、比例、主导类别、理化性质描述）

### Step 5：基于氨基酸组成的功能预测

根据各类别比例按优先级推断主要功能，结果写入 `function_prediction` 字段：

| 优先级 | 判断条件 | 功能预测 |
|--------|---------|---------|
| 1 | Pfam 已知功能块命中 | 🔴 已知功能位点——高度保守催化/结合区域 |
| 2 | Cys 在片段中占比 ≥ 12% | 🟡 二硫键网络/结构骨架 |
| 3 | Nucleophilic ≥ 40% | 🟢 催化活性位点/磷酸化调控区（Ser/Thr/Cys核心） |
| 4 | Hydrophobic ≥ 45% | ⬛ 疏水折叠核心/跨膜区 |
| 5 | Aromatic ≥ 20% | 🟣 底物识别/π-π堆叠区 |
| 6 | Cationic ≥ 35% | ⚡ 正电荷底物结合区 |
| 7 | Acidic ≥ 35% | 🔵 金属离子螯合/催化酸基区 |
| 8 | Nucleophilic ≥ 25% + Cationic ≥ 15% | 🔵 亲核-阳离子协作底物识别区 |
| 9 | Hydrophobic ≥ 25% + Nucleophilic ≥ 25% | ⬛ 两亲性蛋白-蛋白相互作用界面 |
| 10 | Acidic ≥ 20% + Cationic ≥ 20% | ⚡ 电荷互补区（盐桥网络/静电引导） |
| 11 | Amide ≥ 20% | 🔵 酰胺富集区（氢键网络/糖基化位点） |
| 12 | 以上均不满足 | 🔵 混合型功能区（Linker/多功能结合界面） |

### Step 6：生成报告
- 每物种：`_分析报告.md` + `_key_fragments.json`（含 `composition` 和 `function_prediction` 字段）
- 全物种：`汇总分析报告_含功能预测.md`

---

## 输出文件结构

```
<工作目录>/
├── 汇总分析报告_含功能预测.md
└── results/
    └── <物种名>/
        ├── <物种名>_input.fasta
        ├── <物种名>_aligned.fasta
        ├── <物种名>_consensus.fasta
        ├── <物种名>_key_fragments.json
        └── <物种名>_分析报告.md
```

---

## 关键参数

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `THRESHOLD` | 0.5 | 共识序列保守性阈值 |
| `MAX_SEQ` | 50 | 超过此数量时触发随机采样 |
| `SAMPLE_SIZE` | 50 | 采样序列数 |
| `MIN_LEN` | 6 | 高保守区最小长度（aa） |
| `HIGH_CONSERVATION` | 0.90 | 高保守区保守率阈值 |

---

## 依赖环境

- Python 3.8+
- ClustalOmega（`clustalo --version` 验证）
- 无需额外 Python 包（仅使用标准库）

---

## 注意事项

- 分析新蛋白家族前，在 `references/functional_domains.md` 中补充对应 Pfam 保守域特征序列
- 详细方法说明见 `references/method.md`
- 已完成物种自动跳过（检测到 `_分析报告.md` + `_key_fragments.json` 即跳过）
