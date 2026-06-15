# 礼簿 Libu

一本现代「礼簿」：中国家庭只记三笔最该被记住的账 —— **人情往来、子女、父母**。
自托管、注重隐私、移动优先（PC/手机自适应）。Nginx + 前端(Vue3) + 后端(FastAPI) 打进**单个 Docker 镜像**，数据存 SQLite。

> 设计文档见 [`docs/产品方案.md`](docs/产品方案.md) 与 [`docs/技术设计.md`](docs/技术设计.md)。

## 核心模型
三类账**逻辑对称**：都以事件为容器、都记送/收、每笔都挂往来对象。

- **事件(event)** 是记账容器：先建一场事（人情往来 / 子女 / 父母 任一，选 **送 / 收** 方向），再**批量加流水**。
- **往来对象(counterparty)** 三类通用，每笔记录**必填**：
  - 人情往来：张三、张三&李四（家庭）
  - 子女：老大、老二（多个孩子）
  - 父母：男方父母、女方父母（双方两个家庭）
  - 可个人或家庭，带关系/标签/备注；可编辑（个人↔家庭，对应结婚/离婚）、合并，历史自动同步。
- **台账**：按往来对象聚合送出/收到/净额（三类都有），还礼 / 赡养分摊对账有据。
- **统计**：三类年度收/送/净、近 12 个月趋势、成员记账占比。
- 金额以「分」存整数；颜色语义化（朱砂=人情、竹青=子女、黛蓝=父母；琥珀金=收、黛青=支）；删除引用保护（有引用拒删，改用隐藏/归档）。
- **访问控制 = nginx Basic Auth**（一个家庭用户名密码），后端无登录系统。

## 一键部署（单容器）
```bash
docker build -t libu .
docker run -d -p 8080:8080 \
  -e APP_USERNAME=family -e APP_PASSWORD=设一个家庭密码 \
  -v libu-data:/app/data \
  --name libu libu
```
或用 compose：`APP_PASSWORD=xxx docker compose up -d --build`

访问 `http://<host>:8080`，浏览器会弹用户名密码框（nginx Basic Auth）。
> ⚠️ 公网访问请在前面叠一层 HTTPS；`APP_PASSWORD` 为空 = 不启用鉴权（站点裸奔）。

备份 = 复制数据卷里的 `libu.db` 一个文件。

## 本地开发
后端：
```bash
cd backend
python3.12 -m venv venv && ./venv/bin/pip install -r requirements.txt
PYTHONPATH=. ./venv/bin/uvicorn app.main:app --reload --port 8000
```
前端：
```bash
cd frontend
npm install && npm run dev   # 开发期 /api 代理到 127.0.0.1:8000
```

## 许可证

本项目采用 **[GNU General Public License v3.0](LICENSE)**。

Copyright (C) 2026 byl0561

本程序是自由软件：你可以依据自由软件基金会发布的 GNU GPL v3（或更新版本）重新分发和/或修改它。发布本程序是希望它有用，但**不附带任何担保**；详见 GPLv3 全文。
