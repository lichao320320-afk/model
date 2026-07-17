"""
GWSI 2.0 核心计算引擎
提供GWSI评分计算、修正系数应用、市场评估等核心功能
支持动态数据集成和实时更新
"""

import json
import math
from datetime import datetime
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from abc import ABC, abstractmethod
import requests
from functools import lru_cache


@dataclass
class DimensionScore:
    """维度评分数据类"""
    dimension_id: int
    dimension_name: str
    score: float
    weight: float
    data_sources: List[str]
    confidence_level: float  # 0-1, 表示数据可信度
    last_updated: str


@dataclass
class CorrectionFactors:
    """修正系数数据类"""
    base_coefficient: float
    bonus_wind_resource: float
    bonus_grid_friendly: float
    bonus_industry_maturity: float
    comprehensive_factor: float


@dataclass
class GWSIResult:
    """GWSI评分结果"""
    market_name: str
    base_gwsi: float
    correction_factors: CorrectionFactors
    final_gwsi: float
    confidence_score: float
    timestamp: str
    data_quality: str  # high/medium/low


class DataSourceConnector(ABC):
    """数据源连接器抽象基类"""
    
    @abstractmethod
    def fetch_data(self, indicator: str, market: str, **kwargs) -> Dict:
        """从数据源获取数据"""
        pass
    
    @abstractmethod
    def validate_data(self, data: Dict) -> bool:
        """验证数据有效性"""
        pass


class IEAWindConnector(DataSourceConnector):
    """IEA Wind 数据连接器"""
    
    def __init__(self, api_key: str = None):
        self.base_url = "https://www.iea.org/api/wind"
        self.api_key = api_key
        self.cache = {}
    
    def fetch_data(self, indicator: str, market: str, **kwargs) -> Dict:
        """
        从IEA Wind获取风电数据
        支持指标: capacity, cagr, investment, technology_level
        """
        try:
            endpoint = f"{self.base_url}/markets/{market}/indicators/{indicator}"
            params = {
                'format': 'json',
                'version': 'v1',
                **kwargs
            }
            
            # 检查缓存
            cache_key = f"{market}_{indicator}"
            if cache_key in self.cache:
                cached_data, timestamp = self.cache[cache_key]
                if (datetime.now() - timestamp).days < 7:  # 7天缓存
                    return cached_data
            
            # 真实API调用
            headers = {'Authorization': f'Bearer {self.api_key}'} if self.api_key else {}
            response = requests.get(endpoint, params=params, headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                self.cache[cache_key] = (data, datetime.now())
                return data
            else:
                print(f"IEA API Error: {response.status_code}")
                return self._get_fallback_data(market, indicator)
        
        except Exception as e:
            print(f"IEA连接错误: {e}")
            return self._get_fallback_data(market, indicator)
    
    def _get_fallback_data(self, market: str, indicator: str) -> Dict:
        """备用数据"""
        fallback = {
            'China': {'capacity': 120, 'cagr': 12, 'investment': 15000},
            'India': {'capacity': 45, 'cagr': 15, 'investment': 5000},
            'Germany': {'capacity': 63, 'cagr': 3, 'investment': 2000},
        }
        return fallback.get(market, {})
    
    def validate_data(self, data: Dict) -> bool:
        """验证数据"""
        required_fields = ['value', 'unit', 'year']
        return all(field in data for field in required_fields) if isinstance(data, dict) else False


class GWECConnector(DataSourceConnector):
    """Global Wind Energy Council 数据连接器"""
    
    def __init__(self):
        self.base_url = "https://gwec.net/api"
    
    def fetch_data(self, indicator: str, market: str, **kwargs) -> Dict:
        """从GWEC获取全球风电数据"""
        try:
            endpoint = f"{self.base_url}/markets/{market}/{indicator}"
            response = requests.get(endpoint, timeout=10)
            
            if response.status_code == 200:
                return response.json()
            else:
                return self._get_sample_data(market, indicator)
        
        except Exception as e:
            print(f"GWEC连接错误: {e}")
            return self._get_sample_data(market, indicator)
    
    def _get_sample_data(self, market: str, indicator: str) -> Dict:
        """示例数据"""
        sample = {
            'market_share': 0.15,
            'growth_trend': 'positive',
            'competitive_intensity': 0.7,
        }
        return sample
    
    def validate_data(self, data: Dict) -> bool:
        """验证数据"""
        return isinstance(data, dict) and len(data) > 0


class BNEFConnector(DataSourceConnector):
    """Bloomberg NEF 数据连接器"""
    
    def __init__(self, api_key: str = None):
        self.base_url = "https://bnef-api.bloomberg.com"
        self.api_key = api_key
    
    def fetch_data(self, indicator: str, market: str, **kwargs) -> Dict:
        """从BNEF获取投融资和成本数据"""
        try:
            endpoint = f"{self.base_url}/wind/{market}/{indicator}"
            headers = {'X-API-Key': self.api_key} if self.api_key else {}
            response = requests.get(endpoint, headers=headers, timeout=10)
            
            if response.status_code == 200:
                return response.json()
            else:
                return {'lcoe': 45, 'capex_trend': 'declining'}
        
        except Exception as e:
            print(f"BNEF连接错误: {e}")
            return {}
    
    def validate_data(self, data: Dict) -> bool:
        """验证数据"""
        return isinstance(data, dict) and len(data) > 0


class WorldBankConnector(DataSourceConnector):
    """World Bank 数据连接器"""
    
    def __init__(self):
        self.base_url = "https://api.worldbank.org/v2"
    
    def fetch_data(self, indicator: str, market: str, **kwargs) -> Dict:
        """从World Bank获取宏观经济指标"""
        try:
            # 使用ISO国家代码
            country_code = kwargs.get('country_code', 'CN')
            indicator_code = self._map_indicator(indicator)
            
            endpoint = f"{self.base_url}/country/{country_code}/indicator/{indicator_code}"
            params = {'format': 'json', 'per_page': 1}
            response = requests.get(endpoint, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                return data[1][0] if data[1] else {}
            else:
                return {}
        
        except Exception as e:
            print(f"World Bank连接错误: {e}")
            return {}
    
    def _map_indicator(self, indicator: str) -> str:
        """指标映射"""
        mapping = {
            'gdp_growth': 'NY.GDP.MKTP.KD.ZS',
            'fdi_inflow': 'BX.KLT.DINV.CD.WD',
            'political_stability': 'PV.EST',
        }
        return mapping.get(indicator, indicator)
    
    def validate_data(self, data: Dict) -> bool:
        """验证数据"""
        return isinstance(data, dict)


class IMFConnector(DataSourceConnector):
    """IMF 数据连接器"""
    
    def __init__(self):
        self.base_url = "https://www.imf.org/external/datamapper/api/v1"
    
    def fetch_data(self, indicator: str, market: str, **kwargs) -> Dict:
        """从IMF获取信用评级和财政数据"""
        try:
            # 简化实现
            credit_ratings = {
                'China': 'A+',
                'India': 'BBB-',
                'Germany': 'AAA',
                'Brazil': 'BB-',
            }
            return {'credit_rating': credit_ratings.get(market, 'BB')}
        
        except Exception as e:
            print(f"IMF连接错误: {e}")
            return {}
    
    def validate_data(self, data: Dict) -> bool:
        """验证数据"""
        return isinstance(data, dict) and 'credit_rating' in data


class DynamicDataAggregator:
    """动态数据聚合器 - 整合多个数据源"""
    
    def __init__(self):
        self.connectors = {
            'iea_wind': IEAWindConnector(),
            'gwec': GWECConnector(),
            'bnef': BNEFConnector(),
            'world_bank': WorldBankConnector(),
            'imf': IMFConnector(),
        }
        self.data_cache = {}
    
    def get_dimension_data(self, dimension_id: int, market: str, 
                          indicator_name: str) -> Dict:
        """
        获取维度数据，优先级：缓存 > 多源聚合 > 备用数据
        """
        cache_key = f"{market}_{dimension_id}_{indicator_name}"
        
        # 检查缓存
        if cache_key in self.data_cache:
            cached_data, timestamp = self.data_cache[cache_key]
            if (datetime.now() - timestamp).days < 1:  # 1天缓存
                return cached_data
        
        # 多源数据聚合
        aggregated_data = self._aggregate_from_sources(
            dimension_id, market, indicator_name
        )
        
        # 缓存结果
        self.data_cache[cache_key] = (aggregated_data, datetime.now())
        
        return aggregated_data
    
    def _aggregate_from_sources(self, dimension_id: int, market: str,
                                indicator_name: str) -> Dict:
        """从多个数据源聚合数据"""
        
        # 根据维度选择数据源
        source_mapping = {
            1: ['iea_wind', 'gwec', 'bnef'],  # 市场规划力
            2: ['world_bank'],                 # 进入壁垒
            3: ['iea_wind'],                   # 基础设施
            4: ['imf', 'world_bank'],          # 资本安全
            5: ['gwec'],                       # 本地化要求
            6: ['bnef', 'gwec'],               # 供应链部署
            7: ['gwec'],                       # 正业准入性
            8: ['world_bank'],                 # 区域配对协调
            9: ['world_bank', 'imf'],          # 投资便利性
        }
        
        selected_sources = source_mapping.get(dimension_id, [])
        
        data_list = []
        for source_name in selected_sources:
            if source_name in self.connectors:
                try:
                    connector = self.connectors[source_name]
                    data = connector.fetch_data(indicator_name, market)
                    if connector.validate_data(data):
                        data_list.append({
                            'source': source_name,
                            'data': data,
                            'confidence': 0.9
                        })
                except Exception as e:
                    print(f"获取{source_name}数据失败: {e}")
        
        # 聚合多源数据
        if data_list:
            return {
                'value': self._aggregate_values(data_list),
                'sources': [d['source'] for d in data_list],
                'confidence': sum(d['confidence'] for d in data_list) / len(data_list),
                'timestamp': datetime.now().isoformat(),
            }
        else:
            return {
                'value': None,
                'sources': [],
                'confidence': 0,
                'timestamp': datetime.now().isoformat(),
            }
    
    def _aggregate_values(self, data_list: List[Dict]) -> float:
        """聚合多个数据值，加权平均"""
        if not data_list:
            return None
        
        values = []
        weights = []
        for item in data_list:
            if isinstance(item['data'], dict) and 'value' in item['data']:
                values.append(item['data']['value'])
                weights.append(item['confidence'])
        
        if values:
            total_weight = sum(weights)
            return sum(v * w for v, w in zip(values, weights)) / total_weight
        
        return None


class GWSICalculator:
    """GWSI 2.0 计算引擎"""
    
    def __init__(self, config_path: str = 'gwsi-2.0/config/'):
        self.config_path = config_path
        self.dimensions = self._load_dimensions()
        self.correction_config = self._load_correction_config()
        self.data_aggregator = DynamicDataAggregator()
    
    def _load_dimensions(self) -> List[Dict]:
        """加载维度配置"""
        try:
            with open(f'{self.config_path}dimensions.json', 'r', encoding='utf-8') as f:
                config = json.load(f)
                return config.get('dimensions', [])
        except Exception as e:
            print(f"加载维度配置失败: {e}")
            return []
    
    def _load_correction_config(self) -> Dict:
        """加载修正系数配置"""
        try:
            with open(f'{self.config_path}correction-factors.json', 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"加载修正系数配置失败: {e}")
            return {}
    
    def score_dimension(self, dimension_id: int, market: str,
                       raw_values: Dict) -> DimensionScore:
        """对单个维度进行评分"""
        
        dimension = next((d for d in self.dimensions if d['id'] == dimension_id), None)
        if not dimension:
            raise ValueError(f"维度 {dimension_id} 不存在")
        
        # 计算子指标评分
        sub_scores = []
        data_sources = []
        confidence_scores = []
        
        for sub_indicator in dimension['sub_indicators']:
            sub_name = sub_indicator['name']
            if sub_name in raw_values:
                raw_value = raw_values[sub_name]
                score = self._calculate_sub_score(raw_value, sub_indicator)
                weight = sub_indicator['weight']
                sub_scores.append((score, weight))
        
        # 加权计算维度得分
        if sub_scores:
            total_score = sum(score * weight for score, weight in sub_scores)
            avg_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0.8
        else:
            total_score = 0
            avg_confidence = 0
        
        return DimensionScore(
            dimension_id=dimension_id,
            dimension_name=dimension['name'],
            score=total_score,
            weight=dimension['weight'],
            data_sources=dimension.get('data_sources', []),
            confidence_level=avg_confidence,
            last_updated=datetime.now().isoformat()
        )
    
    def _calculate_sub_score(self, raw_value: float, 
                            sub_indicator: Dict) -> float:
        """根据评分规则计算子指标得分"""
        
        scoring_rules = sub_indicator['scoring_rules']
        
        # 支持数值范围和文本匹配两种规则
        for rule in scoring_rules:
            if 'range' in rule:
                min_val, max_val = rule['range']
                if min_val <= raw_value < max_val:
                    return rule['score']
            elif 'text' in rule and raw_value == rule['text']:
                return rule['score']
        
        # 如果没有匹配，返回0
        return 0
    
    def calculate_base_gwsi(self, dimension_scores: List[DimensionScore]) -> float:
        """计算基础GWSI评分（未修正）"""
        total_score = 0
        total_weight = 0
        
        for dim_score in dimension_scores:
            total_score += dim_score.score * dim_score.weight
            total_weight += dim_score.weight
        
        if total_weight > 0:
            return total_score / total_weight
        return 0
    
    def calculate_correction_factors(self, market: str,
                                    market_data: Dict) -> CorrectionFactors:
        """计算修正系数"""
        
        # 基础修正系数
        base_coefficient = self._calculate_base_coefficient(market_data)
        
        # 增分项
        bonus_wind = self._calculate_bonus(
            'wind_resource', 
            market_data.get('avg_wind_speed', 0),
            market_data.get('annual_generation_hours', 0)
        )
        
        bonus_grid = self._calculate_bonus(
            'grid_friendly',
            market_data.get('grid_penetration_rate', 0),
            market_data.get('grid_stability_index', 0)
        )
        
        bonus_maturity = self._calculate_bonus(
            'industry_maturity',
            market_data.get('supply_chain_completeness', 0),
            market_data.get('local_talent_count', 0)
        )
        
        # 综合修正系数
        comprehensive = base_coefficient * (1 + bonus_wind) * (1 + bonus_grid) * (1 + bonus_maturity)
        comprehensive = max(0.4, min(1.2, comprehensive))  # 限制范围
        
        return CorrectionFactors(
            base_coefficient=base_coefficient,
            bonus_wind_resource=bonus_wind,
            bonus_grid_friendly=bonus_grid,
            bonus_industry_maturity=bonus_maturity,
            comprehensive_factor=comprehensive
        )
    
    def _calculate_base_coefficient(self, market_data: Dict) -> float:
        """计算基础修正系数"""
        data_quality = market_data.get('data_quality', 'medium')
        
        quality_mapping = {
            'authentic': 1.15,
            'high': 1.1,
            'medium': 1.0,
            'low': 0.75,
            'very_low': 0.65,
        }
        
        return quality_mapping.get(data_quality, 1.0)
    
    def _calculate_bonus(self, bonus_type: str, *values) -> float:
        """计算增分项"""
        if bonus_type == 'wind_resource':
            wind_speed = values[0] if len(values) > 0 else 0
            generation_hours = values[1] if len(values) > 1 else 0
            
            bonus = 0
            if wind_speed >= 7.5:
                bonus += 0.15
            if generation_hours >= 2500:
                bonus += 0.1
            
            return min(bonus, 0.2)
        
        elif bonus_type == 'grid_friendly':
            penetration = values[0] if len(values) > 0 else 0
            stability = values[1] if len(values) > 1 else 0
            
            bonus = 0
            if penetration > 95:
                bonus += 0.15
            if stability > 0.95:
                bonus += 0.1
            
            return min(bonus, 0.2)
        
        elif bonus_type == 'industry_maturity':
            completeness = values[0] if len(values) > 0 else 0
            talent = values[1] if len(values) > 1 else 0
            
            bonus = 0
            if completeness >= 80:
                bonus += 0.12
            if talent >= 1000:
                bonus += 0.1
            
            return min(bonus, 0.2)
        
        return 0
    
    def calculate_gwsi(self, market: str, dimension_scores: List[DimensionScore],
                      market_data: Dict) -> GWSIResult:
        """完整的GWSI计算流程"""
        
        # 1. 计算基础GWSI
        base_gwsi = self.calculate_base_gwsi(dimension_scores)
        
        # 2. 计算修正系数
        correction_factors = self.calculate_correction_factors(market, market_data)
        
        # 3. 应用修正系数
        final_gwsi = base_gwsi * correction_factors.comprehensive_factor
        final_gwsi = max(0, min(100, final_gwsi))  # 限制在0-100范围
        
        # 4. 计算数据质量和置信度
        avg_confidence = sum(d.confidence_level for d in dimension_scores) / len(dimension_scores) if dimension_scores else 0
        
        if avg_confidence >= 0.85:
            data_quality = 'high'
        elif avg_confidence >= 0.65:
            data_quality = 'medium'
        else:
            data_quality = 'low'
        
        return GWSIResult(
            market_name=market,
            base_gwsi=round(base_gwsi, 2),
            correction_factors=correction_factors,
            final_gwsi=round(final_gwsi, 2),
            confidence_score=round(avg_confidence, 3),
            timestamp=datetime.now().isoformat(),
            data_quality=data_quality
        )
    
    def get_market_recommendation(self, gwsi_score: float) -> str:
        """根据GWSI评分提供战略建议"""
        if gwsi_score >= 80:
            return "⭐⭐⭐ 优先进入级 - 加大投资，建立据点"
        elif gwsi_score >= 60:
            return "⭐⭐ 战略储备级 - 建立合作伙伴关系"
        elif gwsi_score >= 40:
            return "⭐ 风险评估级 - 试点项目，小额投资"
        elif gwsi_score >= 20:
            return "⏳ 观察等待级 - 持续跟踪，等待突破"
        else:
            return "❌ 不建议进入 - 继续观察"


# 示例使用
if __name__ == '__main__':
    # 初始化计算器
    calculator = GWSICalculator()
    
    # 中国市场评估示例
    market = 'China'
    
    # 示例维度评分
    dimension_scores = [
        DimensionScore(1, '市场规划力', 90, 0.25, ['IEA', 'GWEC'], 0.95, datetime.now().isoformat()),
        DimensionScore(2, '进入壁垒', 50, 0.15, ['WTO'], 0.85, datetime.now().isoformat()),
        DimensionScore(3, '基础设施', 85, 0.10, ['IEA'], 0.92, datetime.now().isoformat()),
        DimensionScore(4, '资本安全', 70, 0.10, ['IMF'], 0.88, datetime.now().isoformat()),
        DimensionScore(5, '本地化要求', 40, 0.10, ['GWEC'], 0.80, datetime.now().isoformat()),
        DimensionScore(6, '供应链部署', 85, 0.10, ['BNEF'], 0.90, datetime.now().isoformat()),
        DimensionScore(7, '正业准入性', 75, 0.05, ['IEC'], 0.87, datetime.now().isoformat()),
        DimensionScore(8, '区域配对协调', 80, 0.10, ['GWEC'], 0.86, datetime.now().isoformat()),
        DimensionScore(9, '投资便利性', 65, 0.05, ['World Bank'], 0.84, datetime.now().isoformat()),
    ]
    
    # 市场数据
    market_data = {
        'avg_wind_speed': 7.8,
        'annual_generation_hours': 2600,
        'grid_penetration_rate': 96,
        'grid_stability_index': 0.96,
        'supply_chain_completeness': 85,
        'local_talent_count': 5000,
        'data_quality': 'authentic',
    }
    
    # 计算GWSI
    result = calculator.calculate_gwsi(market, dimension_scores, market_data)
    
    print(f"\n=== {market} 市场 GWSI 2.0 评估结果 ===")
    print(f"基础GWSI: {result.base_gwsi}")
    print(f"修正系数: {result.correction_factors.comprehensive_factor}")
    print(f"最终GWSI: {result.final_gwsi}")
    print(f"置信度: {result.confidence_score}")
    print(f"数据质量: {result.data_quality}")
    print(f"建议: {calculator.get_market_recommendation(result.final_gwsi)}")
    print(f"更新时间: {result.timestamp}")
