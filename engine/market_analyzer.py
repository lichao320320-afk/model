"""
市场分析和排序模块
提供全球市场对标、排序、比较等功能
"""

import pandas as pd
from typing import List, Dict, Optional
import json
from datetime import datetime
from .gwsi_calculator import GWSICalculator, DimensionScore


class MarketAnalyzer:
    """市场分析器"""
    
    def __init__(self):
        self.calculator = GWSICalculator()
        self.market_scores = {}
        self.market_metadata = {}
    
    def add_market_evaluation(self, market_name: str, dimension_scores: List[DimensionScore],
                            market_data: Dict) -> Dict:
        """
        添加市场评估结果
        """
        result = self.calculator.calculate_gwsi(market_name, dimension_scores, market_data)
        
        self.market_scores[market_name] = {
            'base_gwsi': result.base_gwsi,
            'final_gwsi': result.final_gwsi,
            'correction_factor': result.correction_factors.comprehensive_factor,
            'confidence': result.confidence_score,
            'data_quality': result.data_quality,
            'timestamp': result.timestamp,
        }
        
        self.market_metadata[market_name] = {
            'dimension_scores': [{
                'id': d.dimension_id,
                'name': d.dimension_name,
                'score': d.score,
                'weight': d.weight,
                'sources': d.data_sources,
            } for d in dimension_scores],
            'market_data': market_data,
        }
        
        return self.market_scores[market_name]
    
    def get_market_ranking(self, top_n: Optional[int] = None, sort_by: str = 'final_gwsi') -> pd.DataFrame:
        """
        获取市场排名
        """
        if not self.market_scores:
            return pd.DataFrame()
        
        data = []
        for market, scores in self.market_scores.items():
            data.append({
                'Market': market,
                'Final GWSI': scores['final_gwsi'],
                'Base GWSI': scores['base_gwsi'],
                'Correction Factor': scores['correction_factor'],
                'Confidence': scores['confidence'],
                'Data Quality': scores['data_quality'],
                'Timestamp': scores['timestamp'],
            })
        
        df = pd.DataFrame(data)
        df = df.sort_values(by=sort_by, ascending=False)
        
        if top_n:
            df = df.head(top_n)
        
        df['Rank'] = range(1, len(df) + 1)
        return df[['Rank', 'Market', 'Final GWSI', 'Base GWSI', 'Correction Factor', 'Confidence', 'Data Quality']]
    
    def compare_markets(self, market_list: List[str]) -> pd.DataFrame:
        """
        对比多个市场的维度得分
        """
        comparison_data = []
        
        for market in market_list:
            if market in self.market_metadata:
                row = {'Market': market}
                for dim in self.market_metadata[market]['dimension_scores']:
                    row[dim['name']] = dim['score']
                comparison_data.append(row)
        
        if comparison_data:
            return pd.DataFrame(comparison_data)
        else:
            return pd.DataFrame()
    
    def get_market_matrix_quadrant(self, gwsi_threshold: float = 50,
                                   attractiveness_threshold: float = 50) -> Dict:
        """
        将市场分配到四象限矩阵
        """
        quadrants = {
            'high_gwsi_high_attract': [],  # I象限 - 优先进入
            'low_gwsi_high_attract': [],   # II象限 - 风险评估
            'low_gwsi_low_attract': [],    # III象限 - 观察等待
            'high_gwsi_low_attract': [],   # IV象限 - 战略储备
        }
        
        for market, scores in self.market_scores.items():
            gwsi = scores['final_gwsi']
            attractiveness = scores['confidence'] * 100
            
            if gwsi >= gwsi_threshold and attractiveness >= attractiveness_threshold:
                quadrants['high_gwsi_high_attract'].append(market)
            elif gwsi < gwsi_threshold and attractiveness >= attractiveness_threshold:
                quadrants['low_gwsi_high_attract'].append(market)
            elif gwsi < gwsi_threshold and attractiveness < attractiveness_threshold:
                quadrants['low_gwsi_low_attract'].append(market)
            else:
                quadrants['high_gwsi_low_attract'].append(market)
        
        return quadrants
    
    def get_strategic_recommendations(self, market: str) -> Dict:
        """
        获取市场的战略建议
        """
        if market not in self.market_scores:
            return {}
        
        scores = self.market_scores[market]
        metadata = self.market_metadata[market]
        
        gwsi = scores['final_gwsi']
        dimensions = metadata['dimension_scores']
        
        sorted_dims = sorted(dimensions, key=lambda x: x['score'], reverse=True)
        
        recommendation = {
            'market': market,
            'final_gwsi': gwsi,
            'overall_recommendation': self.calculator.get_market_recommendation(gwsi),
            'top_3_strengths': [
                {'dimension': d['name'], 'score': d['score']} 
                for d in sorted_dims[:3]
            ],
            'top_3_weaknesses': [
                {'dimension': d['name'], 'score': d['score']} 
                for d in sorted_dims[-3:]
            ],
            'action_plan': self._generate_action_plan(gwsi, sorted_dims),
        }
        
        return recommendation
    
    def _generate_action_plan(self, gwsi: float, dimensions: List[Dict]) -> Dict:
        """
        根据GWSI和维度生成行动计划
        """
        if gwsi >= 80:
            return {
                'timeline': '立即启动',
                'investment_level': '大额投资',
                'actions': [
                    '建立地区总部',
                    '投资本地生产基地',
                    '建立长期战略合作',
                    '加大市场开拓投入',
                ]
            }
        elif gwsi >= 60:
            return {
                'timeline': '6-12个月',
                'investment_level': '中等投资',
                'actions': [
                    '建立战略合作伙伴',
                    '开展可行性研究',
                    '建立小规模示范项目',
                    '培养本地团队',
                ]
            }
        elif gwsi >= 40:
            return {
                'timeline': '12-24个月',
                'investment_level': '小额试点',
                'actions': [
                    '进行深度市场调研',
                    '识别关键合作伙伴',
                    '试点项目（1-2个）',
                    '建立监测机制',
                ]
            }
        elif gwsi >= 20:
            return {
                'timeline': '持续跟踪',
                'investment_level': '零投资',
                'actions': [
                    '月度市场监测',
                    '关注政策变化',
                    '维持沟通渠道',
                    '准备应急计划',
                ]
            }
        else:
            return {
                'timeline': '暂无',
                'investment_level': '无',
                'actions': [
                    '列入观察名单',
                    '年度定期评估',
                    '等待重大政策突破',
                ]
            }
    
    def export_analysis_report(self, filename: str = 'gwsi_analysis_report.json'):
        """
        导出完整分析报告
        """
        report = {
            'timestamp': datetime.now().isoformat(),
            'total_markets': len(self.market_scores),
            'market_rankings': self.get_market_ranking().to_dict(orient='records'),
            'quadrant_analysis': self.get_market_matrix_quadrant(),
            'detailed_scores': self.market_scores,
            'recommendations': {
                market: self.get_strategic_recommendations(market)
                for market in self.market_scores.keys()
            }
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        return report
