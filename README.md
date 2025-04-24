# LogTraceFinder

日志追踪查询自助工具

## 启动

创建.env文件

```env
CLICKHOUSE_HOST=127.0.0.1
CLICKHOUSE_PORT=8123
CLICKHOUSE_USER=default
CLICKHOUSE_PASSWORD=
CLICKHOUSE_DATABASE=otel
```

初始化环境

```bash
bash init.sh
```

启动

```bash
bash start_app.sh
```
