# 接口文档

## POST /congestion
根据车辆观测数据检测拥堵区域。

- Content-Type: `application/json`
- Request body: `CongestionRequest`

### 请求体示例
```json
{
  "observations": [
    {
      "vehicle_id": "car-001",
      "coordinate": {"latitude": 40.0, "longitude": -74.0},
      "speed_kph": 12,
      "heading_degrees": 90
    },
    {
      "vehicle_id": "car-002",
      "coordinate": {"latitude": 40.0003, "longitude": -74.0002},
      "speed_kph": 10
    },
    {
      "vehicle_id": "car-003",
      "coordinate": {"latitude": 40.0004, "longitude": -74.0004},
      "speed_kph": 9
    }
  ]
}
```

### 响应示例
```json
{
  "congested_regions": [
    {
      "region_id": 1,
      "centroid": {
        "latitude": 40.00023333333333,
        "longitude": -74.0002
      },
      "boundary": [
        {"latitude": 40.0, "longitude": -74.0},
        {"latitude": 40.0004, "longitude": -74.0003},
        {"latitude": 40.0003, "longitude": -74.0002}
      ],
      "vehicle_ids": ["car-001", "car-002", "car-003"],
      "congestion_level": "medium"
    }
  ]
}
```

### 字段说明
- `observations`: 车辆观测列表，不能为空。
  - `vehicle_id` (string, required): 车辆唯一标识。
  - `coordinate` (object, required):
    - `latitude` (float): 纬度，范围 -90 ~ 90。
    - `longitude` (float): 经度，范围 -180 ~ 180。
  - `speed_kph` (float, optional): 车速，km/h，非负。
  - `heading_degrees` (float, optional): 航向角度，0~360°。

- `congested_regions`: 拥堵区域数组，按检测到的顺序返回。
  - `region_id` (integer): 区域编号，从 1 开始。
  - `centroid` (object): 拥堵区域重心坐标。
  - `boundary` (array): 该区域的凸包坐标列表，按顺时针/逆时针顺序返回。
  - `vehicle_ids` (array): 属于该拥堵区域的车辆 ID 列表。
  - `congestion_level` (string): 拥堵等级，`low` / `medium` / `high`。

## GET /health
健康检查，返回 `{ "status": "ok" }`。
