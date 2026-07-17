# GWSI 2.0 - 全球风电产业重构与全球经营体系战略模型

## 项目概述

GWSI 2.0（Global Wind Strategic Index 2.0）是一个全球市场筛选和战略决策支持系统，基于 Goldwind 2026-2035 全球风电产业战略规划。

该模型通过**九维度评分体系**、**修正系数调整**和**全球市场矩阵分析**，帮助企业：
- 🎯 科学评估国际市场机会
- 📊 量化市场进入风险与收益
- 🌍 制定全球战略优先级
- 💡 指导资源配置决策

---

## 核心特性

✅ **完整的九维度评分系统**
- 量化的评分规则
- 灵活的权重调整
- 科学的数据驱动

✅ **三层修正系数体系**
- 基础修正系数（0.40-1.20）
- 增分组项（+0.00-0.60）
- 综合回报率计算

✅ **动态多源数据集成**
- IEA Wind、GWEC、BNEF、World Bank、IMF 官方数据
- 智能缓存机制（减少API调用）
- 实时数据验证和聚合

✅ **全球市场对标**
- 150+ 国家/地区评估
- 历史趋势分析
- 实时排名更新

✅ **战略决策支持**
- 四象限市场矩阵
- 优先级排序
- 风险-收益评估

---

## 快速开始

### 1. 环境配置

```bash
git clone https://github.com/lichao320320-afk/model.git
cd model
pip install -r requirements.txt
```

### 2. 评估单个市场

```python
from engine.gwsi_calculator import GWSICalculator, DimensionScore
from datetime import datetime

# 创建计算器
calculator = GWSICalculator()

# 中国市场评估 - 定义各维度评分
dimension_scores = [
    DimensionScore(1, '市场规划力', 90, 0.25, ['IEA', 'GWEC'], 0.95, datetime.now().isoformat()),
    DimensionScore(2, '进入壁垒', 50, 0.15, ['WTO'], 0.85, datetime.now().isoformat()),
    # ... 其他维度
]

# 市场特定数据
market_data = {
    'avg_wind_speed': 7.8,
    'annual_generation_hours': 2600,
    'grid_penetration_rate': 96,
    'data_quality': 'authentic'
}

# 计算GWSI
result = calculator.calculate_gwsi('China', dimension_scores, market_data)
print(f"中国 GWSI: {result.final_gwsi}")
print(f"建议: {calculator.get_market_recommendation(result.final_gwsi)}")
```

### 3. 批量市场分析

```python
from engine.market_analyzer import MarketAnalyzer

analyzer = MarketAnalyzer()

# 添加多个市场评估
for market, scores, data in market_list:
    analyzer.add_market_evaluation(market, scores, data)

# 获取市场排名
ranking = analyzer.get_market_ranking(top_n=20)
print(ranking)

# 四象限分析
quadrants = analyzer.get_market_matrix_quadrant()
print(f"优先进入: {quadrants['high_gwsi_high_attract']}")
```

### 4. 运行示例

```bash
python examples/sample-evaluation.py
```

---

## 项目结构

```
model/
├── README.md                              # 项目说明
├── requirements.txt                       # Python 依赖
├── gwsi-2.0/
│   ├── framework.md                       # 框架详解
│   ├── config/
│   │   ├── dimensions.json                # 九维度配置
│   │   ├── correction-factors.json        # 修正系数配置
│   │   └── thresholds.json                # 评分阈值
│   └── docs/
│       ├── methodology.md                 # 方法论说明
│       ├── scoring-rules.md               # 评分规则
│       └── case-studies.md                # 案例分析
├── engine/
│   ├── gwsi_calculator.py                 # 核心计算引擎（多源数据）
│   ├── market_analyzer.py                 # 市场分析工具
│   └── visualization.py                   # 可视化工具
├── data/
│   ├── raw/                               # 原始数据
│   │   ├── global-markets.csv
│   │   └── historical-scores.csv
│   └── processed/                         # 处理后的数据
├── examples/
│   ├── sample-evaluation.py               # 单市场评估示例
│   ├── batch-analysis.py                  # 批量分析示例
│   └── results/
│       ├── market-ranking.json
│       └── strategy-recommendation.json
└── tests/
    ├── test_calculator.py
    └── test_analyzer.py
```

---

## 九维度评分体系

| 维度 | 权重 | 评分范围 | 关键指标 |
|------|------|--------|----------|
| **01 市场规划力** | 25% | 0-100 | 未来装机容量、产业投资规模 |
| **02 进入壁垒** | 15% | 0-100 | 进入成本、贸易壁垒、竞争格局 |
| **03 基础设施** | 10% | 0-100 | 风资源、电网、物流 |
| **04 资本安全** | 10% | 0-100 | 政治风险、汇率风险、政策稳定性 |
| **05 本地化要求** | 10% | 0-100 | 本地制造、技术转让要求 |
| **06 供应链部署** | 10% | 0-100 | 零部件供应、产业链成熟度 |
| **07 正业准入性** | 5% | 0-100 | 行业准入标准、许可证要求 |
| **08 区域配对协调** | 10% | 0-100 | 区域协作、生态协调 |
| **09 投资便利性** | 5% | 0-100 | 投资政策、融资便利 |

---

## 修正系数体系

### 基础修正系数（数据可靠性）
- **真实指标** (IPyNAME, ALMM, KTVA等): 1.10-1.20
- **行业标准指标**: 1.00-1.10
- **分析估算**: 0.70-0.85

### 增分项（市场优势）
- **风资源优势**: +0.00-0.20
- **电网友好性**: +0.00-0.20
- **产业成熟度**: +0.00-0.20

### 综合修正系数
**修正系数 = 基础系数 × (1+增分项1) × (1+增分项2) × (1+增分项3)**

范围: 0.40 - 1.20

---

## 数据源集成

本模型支持实时调用以下国际官方数据源：

| 数据源 | 数据类型 | API | 更新频率 |
|------|--------|-----|--------|
| **IEA Wind** | 装机容量、投资、CAGR | https://www.iea.org/api/wind | 季度 |
| **GWEC** | 市场份额、增长、竞争 | https://gwec.net/api | 月度 |
| **BNEF** | 成本、融资、投资 | https://bnef-api.bloomberg.com | 实时 |
| **World Bank** | GDP、FDI、政治稳定性 | https://api.worldbank.org/v2 | 年度 |
| **IMF** | 信用评级、财政数据 | https://www.imf.org/api | 月度 |

**智能缓存机制**
- IEA/GWEC/BNEF: 7天缓存
- World Bank: 30天缓存
- IMF: 30天缓存
- 本地数据: 1天缓存

---

## GWSI 评分解释

```
GWSI Score 解释:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
80-100  ⭐⭐⭐  优先进入级
        特点: 市场机会大，风险可控
        建议: 加大投资，建立据点

60-79   ⭐⭐    战略储备级
        特点: 市场潜力中等，需观察
        建议: 建立合作伙伴关系

40-59   ⭐     风险评估级
        特点: 机会与风险并存
        建议: 试点项目，小额投资

20-39   ⏳    观察等待级
        特点: 市场尚未成熟
        建议: 持续跟踪，等待突破

0-19    ❌    不建议进入
        特点: 风险远高于收益
        建议: 继续观察，短期无进入计划
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## 使用场景

### 场景1: 年度战略规划
评估全球风电市场的前50个目标市场，制定年度投资优先级。

### 场景2: 市场进入决策
新市场开拓前，进行全面的GWSI评估，确保进入决策的科学性。

### 场景3: 竞争对标
与竞争对手对标，识别战略优势和劣势市场。

### 场景4: 政策影响分析
当市场政策变化时，实时调整GWSI评分，评估影响。

---

## API 使用示例

### 获取市场排名

```python
from engine.market_analyzer import MarketAnalyzer

analyzer = MarketAnalyzer()
ranking_df = analyzer.get_market_ranking(top_n=20)
print(ranking_df.to_string())
```

### 四象限矩阵分析

```python
quadrants = analyzer.get_market_matrix_quadrant(
    gwsi_threshold=60,
    attractiveness_threshold=70
)

print(f"优先进入 (I象限): {len(quadrants['high_gwsi_high_attract'])} 个")
print(f"战略储备 (IV象限): {len(quadrants['high_gwsi_low_attract'])} 个")
print(f"风险评估 (II象限): {len(quadrants['low_gwsi_high_attract'])} 个")
print(f"观察等待 (III象限): {len(quadrants['low_gwsi_low_attract'])} 个")
```

### 生成战略建议

```python
recommendation = analyzer.get_strategic_recommendations('China')

print(f"市场: {recommendation['market']}")
print(f"GWSI: {recommendation['final_gwsi']}")
print(f"建议: {recommendation['overall_recommendation']}")
print(f"\n优势维度:")
for strength in recommendation['top_3_strengths']:
    print(f"  - {strength['dimension']}: {strength['score']}")
print(f"\n行动计划:")
for action in recommendation['action_plan']['actions']:
    print(f"  - {action}")
```

### 导出分析报告

```python
report = analyzer.export_analysis_report(
    filename='gwsi_analysis_report_2026.json'
)
```

---

## 数据更新管理

### 自动更新

```python
# 启用自动数据更新
from engine.gwsi_calculator import DynamicDataAggregator

aggregator = DynamicDataAggregator()

# 获取最新数据（自动检查缓存）
data = aggregator.get_dimension_data(
    dimension_id=1,
    market='China',
    indicator_name='cagr'
)
```

### 手动刷新

```python
# 清除缓存强制刷新
aggregator.data_cache.clear()

# 重新获取数据
fresh_data = aggregator.get_dimension_data(
    dimension_id=1,
    market='China',
    indicator_name='cagr'
)
```

---

## 贡献指南

欢迎提交：
- 新市场数据更新
- 评分模型改进建议
- Bug 报告和功能需求
- 新的数据源集成

---

## 许可证

© 2026 Goldwind. All rights reserved.

---

## 联系方式

- 📧 Email: strategy@goldwind.com
- 🌐 Website: www.goldwind.com
- 📱 Support: +86-xxx-xxxx-xxxx
