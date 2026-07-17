"""
示例：单市场GWSI 2.0评估
"""

from datetime import datetime
from engine.gwsi_calculator import GWSICalculator, DimensionScore


def evaluate_china_market():
    """
    中国市场评估示例
    """
    # 初始化计算器
    calculator = GWSICalculator()
    
    market = 'China'
    
    # 定义各维度的评分
    dimension_scores = [
        # 维度1: 市场规划力 (weight: 25%)
        DimensionScore(
            dimension_id=1,
            dimension_name='市场规划力',
            score=90,
            weight=0.25,
            data_sources=['IEA Wind', 'GWEC', 'BNEF'],
            confidence_level=0.95,
            last_updated=datetime.now().isoformat()
        ),
        # 维度2: 进入壁垒 (weight: 15%)
        DimensionScore(
            dimension_id=2,
            dimension_name='进入壁垒',
            score=50,
            weight=0.15,
            data_sources=['WTO', '商务部'],
            confidence_level=0.85,
            last_updated=datetime.now().isoformat()
        ),
        # 维度3: 基础设施 (weight: 10%)
        DimensionScore(
            dimension_id=3,
            dimension_name='基础设施',
            score=85,
            weight=0.10,
            data_sources=['IEA', '国家气象局'],
            confidence_level=0.92,
            last_updated=datetime.now().isoformat()
        ),
        # 维度4: 资本安全 (weight: 10%)
        DimensionScore(
            dimension_id=4,
            dimension_name='资本安全',
            score=70,
            weight=0.10,
            data_sources=['IMF', 'World Bank'],
            confidence_level=0.88,
            last_updated=datetime.now().isoformat()
        ),
        # 维度5: 本地化要求 (weight: 10%)
        DimensionScore(
            dimension_id=5,
            dimension_name='本地化要求',
            score=40,
            weight=0.10,
            data_sources=['GWEC', '产业政策'],
            confidence_level=0.80,
            last_updated=datetime.now().isoformat()
        ),
        # 维度6: 供应链部署 (weight: 10%)
        DimensionScore(
            dimension_id=6,
            dimension_name='供应链部署',
            score=85,
            weight=0.10,
            data_sources=['BNEF', 'GWEC'],
            confidence_level=0.90,
            last_updated=datetime.now().isoformat()
        ),
        # 维度7: 正业准入性 (weight: 5%)
        DimensionScore(
            dimension_id=7,
            dimension_name='正业准入性',
            score=75,
            weight=0.05,
            data_sources=['IEC', 'CNS'],
            confidence_level=0.87,
            last_updated=datetime.now().isoformat()
        ),
        # 维度8: 区域配对协调 (weight: 10%)
        DimensionScore(
            dimension_id=8,
            dimension_name='区域配对协调',
            score=80,
            weight=0.10,
            data_sources=['GWEC', 'ASEAN'],
            confidence_level=0.86,
            last_updated=datetime.now().isoformat()
        ),
        # 维度9: 投资便利性 (weight: 5%)
        DimensionScore(
            dimension_id=9,
            dimension_name='投资便利性',
            score=65,
            weight=0.05,
            data_sources=['World Bank', 'MOFCOM'],
            confidence_level=0.84,
            last_updated=datetime.now().isoformat()
        ),
    ]
    
    # 市场特定数据
    market_data = {
        'avg_wind_speed': 7.8,
        'annual_generation_hours': 2600,
        'grid_penetration_rate': 96,
        'grid_stability_index': 0.96,
        'supply_chain_completeness': 85,
        'local_talent_count': 5000,
        'data_quality': 'authentic',  # 中国官方数据质量好
    }
    
    # 执行计算
    result = calculator.calculate_gwsi(market, dimension_scores, market_data)
    
    # 输出结果
    print(f"\n{'='*60}")
    print(f"GWSI 2.0 评估结果 - {market} 市场")
    print(f"{'='*60}")
    print(f"\n基础 GWSI 评分:        {result.base_gwsi}")
    print(f"修正系数:")
    print(f"  - 基础系数:         {result.correction_factors.base_coefficient:.3f}")
    print(f"  - 风资源加分:       {result.correction_factors.bonus_wind_resource:+.3f}")
    print(f"  - 电网友好加分:     {result.correction_factors.bonus_grid_friendly:+.3f}")
    print(f"  - 产业成熟加分:     {result.correction_factors.bonus_industry_maturity:+.3f}")
    print(f"  - 综合系数:         {result.correction_factors.comprehensive_factor:.3f}")
    print(f"\n最终 GWSI 评分:        {result.final_gwsi}")
    print(f"置信度:               {result.confidence_score:.3f}")
    print(f"数据质量:             {result.data_quality}")
    print(f"\n战略建议:")
    print(f"  {calculator.get_market_recommendation(result.final_gwsi)}")
    print(f"\n评估时间:             {result.timestamp}")
    print(f"{'='*60}")
    
    return result


def evaluate_multiple_markets():
    """
    多市场对比评估
    """
    calculator = GWSICalculator()
    
    markets_data = {
        'China': {
            'scores': [90, 50, 85, 70, 40, 85, 75, 80, 65],
            'market_data': {
                'avg_wind_speed': 7.8,
                'annual_generation_hours': 2600,
                'grid_penetration_rate': 96,
                'data_quality': 'authentic'
            }
        },
        'Germany': {
            'scores': [55, 75, 90, 95, 80, 90, 85, 90, 85],
            'market_data': {
                'avg_wind_speed': 6.5,
                'annual_generation_hours': 2000,
                'grid_penetration_rate': 98,
                'data_quality': 'high'
            }
        },
        'India': {
            'scores': [92, 60, 75, 65, 50, 70, 70, 65, 60],
            'market_data': {
                'avg_wind_speed': 8.5,
                'annual_generation_hours': 2800,
                'grid_penetration_rate': 85,
                'data_quality': 'medium'
            }
        },
    }
    
    results = {}
    for market, data in markets_data.items():
        dimension_scores = [
            DimensionScore(
                dimension_id=i+1,
                dimension_name=f'维度{i+1}',
                score=data['scores'][i],
                weight=0.11,
                data_sources=['多源'],
                confidence_level=0.85,
                last_updated=datetime.now().isoformat()
            )
            for i in range(9)
        ]
        
        result = calculator.calculate_gwsi(market, dimension_scores, data['market_data'])
        results[market] = result
    
    # 排序并输出
    print(f"\n{'='*70}")
    print(f"全球市场 GWSI 2.0 对标分析")
    print(f"{'='*70}")
    print(f"\n{'市场':<15} {'最终GWSI':>12} {'置信度':>10} {'建议':>25}")
    print(f"{'-'*70}")
    
    for market in sorted(results.keys(), key=lambda m: results[m].final_gwsi, reverse=True):
        result = results[market]
        recommendation = calculator.get_market_recommendation(result.final_gwsi)[:10]
        print(f"{market:<15} {result.final_gwsi:>12.2f} {result.confidence_score:>10.3f} {recommendation:>25}")
    
    print(f"{'='*70}")
    
    return results


if __name__ == '__main__':
    # 单市场评估
    print("\n" + "#"*60)
    print("# 中国市场单独评估")
    print("#"*60)
    evaluate_china_market()
    
    # 多市场对比
    print("\n" + "#"*60)
    print("# 全球市场对标分析")
    print("#"*60)
    evaluate_multiple_markets()
