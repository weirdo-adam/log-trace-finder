# LogTraceFinder

一个基于Flask的日志追踪查询自助工具，支持连接ClickHouse数据库进行高效的日志查询和链路追踪。

## 功能特性

- 🔍 **多维度查询**: 支持按关键词、TraceID、接口地址、时间范围等多维度查询
- 🏃 **高性能**: 基于ClickHouse数据库，支持大规模日志数据的快速查询
- 🎨 **友好界面**: 响应式Web界面，支持移动端访问
- 📊 **链路追踪**: 支持分布式链路追踪，快速定位问题
- ⏰ **时间范围**: 支持自定义时间范围查询，默认查询最近1小时数据
- 📱 **移动适配**: 完全响应式设计，支持各种设备访问

## 技术栈

- **后端**: Flask 3.1.0
- **数据库**: ClickHouse (通过clickhouse-connect)
- **部署**: Gunicorn WSGI服务器
- **前端**: HTML5 + CSS3 + JavaScript (原生)
- **Python版本**: >= 3.13

## 项目结构

```
log-trace-finder/
├── app.py                 # 主应用文件
├── templates/
│   └── index.html        # Web界面模板
├── requirements.txt      # Python依赖列表
├── pyproject.toml       # 项目配置文件
├── init.sh              # 环境初始化脚本
├── start_app.sh         # 应用启动脚本
├── test_clickhouse.py   # ClickHouse连接测试
└── README.md            # 项目说明文档
```

## 快速开始

### 环境要求

- Python 3.13+
- ClickHouse数据库
- Linux/macOS系统（推荐）

### 1. 克隆项目

```bash
git clone <repository-url>
cd log-trace-finder
```

### 2. 配置环境变量

创建`.env`文件并配置ClickHouse连接信息：

```bash
cp .env-example .env
```

编辑`.env`文件：

```env
CLICKHOUSE_HOST=localhost
CLICKHOUSE_PORT=8123
CLICKHOUSE_USER=default
CLICKHOUSE_PASSWORD=your_password
CLICKHOUSE_DATABASE=otel
```

### 3. 初始化环境

```bash
bash init.sh
```

该脚本会自动：
- 检查Python版本
- 创建虚拟环境
- 安装项目依赖

### 4. 启动应用

```bash
bash start_app.sh
```

应用将在 `http://0.0.0.0:8000` 启动。

## 使用说明

### 查询功能

系统支持以下查询条件：

1. **关键词**: 在日志内容(Body)中进行模糊匹配
2. **日志链路ID**: 精确匹配TraceID
3. **接口地址**: 按LogAttributes中的uri字段查询
4. **时间范围**: 支持自定义开始和结束时间

### 数据库表结构

系统查询`otel_logs`表，包含以下字段：

- `ServiceName`: 服务名称
- `Timestamp`: 时间戳
- `Body`: 日志内容
- `SeverityText`: 日志级别
- `LogAttributes`: 日志属性（JSON格式）
- `TraceId`: 链路追踪ID

### 查询限制

- 默认限制返回1000条记录
- 如未指定时间范围，默认查询最近1小时数据

## 开发指南

### 本地开发

1. 激活虚拟环境：
```bash
source .venv/bin/activate
```

2. 安装开发依赖：
```bash
pip install -r requirements.txt
```

3. 直接运行Flask应用：
```bash
python app.py
```

### 自定义配置

在`app.py`中可以修改以下配置：

- 查询字段映射
- 时间范围默认值
- 查询限制条件
- 服务名称过滤

## 部署说明

### 生产环境部署

1. 使用Gunicorn部署（推荐）：
```bash
gunicorn -w 4 -b 0.0.0.0:8000 app:app
```

2. 使用systemd管理服务：

创建`/etc/systemd/system/log-trace-finder.service`：

```ini
[Unit]
Description=Log Trace Finder
After=network.target

[Service]
Type=notify
User=www-data
WorkingDirectory=/path/to/log-trace-finder
Environment=PATH=/path/to/log-trace-finder/.venv/bin
ExecStart=/path/to/log-trace-finder/.venv/bin/gunicorn -w 4 -b 0.0.0.0:8000 app:app
ExecReload=/bin/kill -s HUP $MAINPID
Restart=always

[Install]
WantedBy=multi-user.target
```

### Nginx反向代理

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## 贡献指南

1. Fork 项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启Pull Request

## 许可证

本项目采用 MIT 许可证。

## 更新日志

### v0.1.0
- 初始版本发布
- 支持基础日志查询功能
- 实现Web界面
- 支持ClickHouse数据库连接

## 常见问题

### Q: 如何增加查询结果数量限制？
A: 在`app.py`第139行修改`LIMIT 1000`值。

### Q: 如何支持更多的查询字段？
A: 在`query_conditions`中添加新的查询条件，并在HTML表单中添加对应的输入字段。

## 支持

如遇到问题，请提交Issue或联系项目维护者。
