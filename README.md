# MCompass-Sys-Monitor

基于 [chaosgoo/mcompass](https://github.com/chaosgoo/mcompass) 的 Minecraft 指南针硬件开发的系统性能监控表。

![Preview](./images/preview.png)

## 运行参数

| 参数             | 类型         | 默认值 | 说明                         |
| ---------------- | ------------ | ------ | ---------------------------- |
| `--compass-ip`   | `str`        | 必填   | 指南针配网后的 IP 地址       |
| `--monitor-type` | `str`        | `cpu`  | 监控类型，可选 `cpu`、`mem`  |
| `--interval`     | `float`      | `1.0`  | 监控间隔，单位秒             |
| `--half`         | `store_true` | 否     | 仅使用指南针上半圈显示       |
| `--silent`       | `store_true` | 否     | 静默模式，不输出任何日志     |
| `--logarithm`    | `store_true` | 否     | 对数模式，低数值时指针更灵敏 |