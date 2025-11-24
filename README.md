# 数据预处理与可视化工具说明

本目录提供两个小工具，用于对宏观房价数据做去噪和平滑，并对比处理前后的曲线。

## 文件概览
- `clean_and_smooth.py`：按需对数值列进行 IQR 截尾（可关闭）和滚动均值平滑，输出清洗后的 CSV。
- `plot_compare.py`：绘制原始数据与清洗/平滑后数据的对比曲线。

## 环境依赖
- Python 3.x
- pandas
- matplotlib

## 使用方法

### 1) 去噪/平滑
默认会进行 IQR 截尾 + 滚动平滑；如不想截尾，增加 `--no-cap`。
```bash
python clean_and_smooth.py \
  --raw prepared_dataset.csv \
  --out prepared_dataset_clean.csv \
  --smooth CSUSHPISA Houses Cons_Material FEDFUNDS UNRATE EmpRate \
  --window 3 \
  --past-window \
  --no-cap
```
参数说明：
- `--raw`：原始 CSV 路径，要求包含 `DATE` 列。
- `--out`：输出 CSV 路径。
- `--smooth`：需要平滑的列名（将新增 `*_smoothed` 列）。
- `--window`：滚动窗口大小（整数）。`--past-window` 代表仅用过去窗口，避免未来信息泄漏；不加则为居中窗口（适合可视化）。
- `--no-cap`：关闭 IQR 截尾，只做平滑。

### 2) 曲线对比
在生成了清洗数据后，绘制原始 vs 清洗/平滑曲线：
```bash
python plot_compare.py \
  --raw prepared_dataset.csv \
  --clean prepared_dataset_clean.csv \
  --cols CSUSHPISA UNRATE FEDFUNDS Houses Cons_Material EmpRate
```
说明：若清洗文件中存在 `*_smoothed`，优先绘制平滑列；否则使用清洗后的原列。

## 常见场景
- 可视化/报告：使用默认或居中窗口，观察趋势，展示处理前后对比。
- 建模特征：建议加上 `--past-window` 避免使用未来信息；如不希望削弱极端事件，添加 `--no-cap` 或调大窗口/阈值。

## 提示
- IQR 截尾：按 Q1-1.5*IQR 和 Q3+1.5*IQR 对数值列进行 winsorize；可通过 `--no-cap` 关闭。
- 平滑：滚动均值是线性去噪，窗口过大可能过度平滑，通常 3-6 期较稳妥。
