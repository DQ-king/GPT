# 车辆拥堵监控服务

基于 FastAPI 的简单拥堵检测服务。输入一组车辆的 ID、坐标（必填）、可选的速度和角度，输出拥堵区域、拥堵车辆 ID 和拥堵等级。

## 功能概览
- 采用基于地理距离的聚类算法，将距离在阈值内的车辆归为同一组。
- 支持基于车辆数量和平均速度推断拥堵等级（low / medium / high）。
- 暴露 `/congestion` 接口用于检测拥堵区域，`/health` 用于健康检查。

## 快速开始
1. 安装依赖
   ```bash
   pip install -r requirements.txt
   ```
2. 运行服务
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```
3. 访问接口文档
   - 交互式文档（Swagger UI）：<http://localhost:8000/docs>
   - 备用文档（ReDoc）：<http://localhost:8000/redoc>

## 请求示例
```bash
curl -X POST http://localhost:8000/congestion \
  -H "Content-Type: application/json" \
  -d '{
    "observations": [
      {"vehicle_id": "A", "coordinate": {"latitude": 40.0, "longitude": -74.0}, "speed_kph": 8},
      {"vehicle_id": "B", "coordinate": {"latitude": 40.0003, "longitude": -74.0002}, "speed_kph": 9},
      {"vehicle_id": "C", "coordinate": {"latitude": 40.0004, "longitude": -74.0003}, "speed_kph": 7}
    ]
  }'
```

返回示例：
```json
{
  "congested_regions": [
    {
      "region_id": 1,
      "centroid": {"latitude": 40.00023333333333, "longitude": -74.00016666666667},
      "vehicle_ids": ["A", "B", "C"],
      "congestion_level": "medium"
    }
  ]
}
```

## 拥堵判断规则
- 距离阈值：默认 50 米内视为同一聚类（可在 `CongestionService` 初始化时配置）。
- 最小聚类规模：默认 3 辆车以上才认为是拥堵组。
- 拥堵等级：
  - `high`：车辆数量 ≥ 8，或平均速度 < 5 km/h。
  - `medium`：车辆数量 ≥ 5，或平均速度 < 15 km/h。
  - `low`：其他情况。

## 运行测试
```bash
pytest
```

## 项目结构
```
app/
  main.py         # FastAPI 入口
  service.py      # 拥堵检测算法
  schemas.py      # Pydantic 数据模型

tests/
  test_service.py # 聚类与等级判断单测
  test_api.py     # API 层单测
```

更多接口细节参见 [docs/API.md](docs/API.md)。
