# 🏦 AI Banking Service

> 一个专为银行场景设计的 AI 后端服务，融合了 **Java 后端经验 + 银行业务理解 + LLM 应用开发** 能力。

---

## 📖 项目简介

本项目是我在 **7 年 Java 后端开发（银行行业）** 基础上，完成 **60 天 AI 工程师转型计划** 的阶段性成果。项目完整实现了从 API 设计、数据库持久化到 **RAG（检索增强生成）** 的全链路开发，展现了一名后端工程师如何将 AI 能力接入真实业务系统。

### 核心亮点

- ✅ **完整的 FastAPI 后端**：类比 Spring Boot，提供 RESTful API
- ✅ **PostgreSQL + SQLAlchemy**：异步 ORM，支持银行领域数据模型（客户、账户、交易）
- ✅ **RAG 检索增强生成**：基于 ChromaDB + Sentence-Transformers，实现银行政策文档的智能问答
- ✅ **数学背景赋能**：利用统计学知识实现风险评分接口（均值、标准差、变异系数）
- ✅ **工程化实践**：Pydantic 数据校验、Docker 容器化、环境配置管理、日志监控

---

## 🛠️ 技术栈

| 分类 | 技术 |
|---|---|
| **后端框架** | FastAPI, Uvicorn |
| **AI / LLM** | ChromaDB, Sentence-Transformers, Hugging Face |
| **数据库** | PostgreSQL, SQLAlchemy (async), asyncpg |
| **数据校验** | Pydantic v2 |
| **容器化** | Docker, Docker Compose |
| **包管理** | uv (替代 pip/conda) |
| **开发环境** | Python 3.12, IntelliJ IDEA 2025.2.5 |

---

## 📁 项目结构
