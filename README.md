# DIPR-research

**DIPR** is a **D**ecomposing, **I**nformation-gathering, **P**lan-based, and **R**easoning Framework for Large Language Model Deep Research.

---

## 使用方式
### 后端服务启动

进入 `/backend` 目录，运行后端服务器：

```bash
python ws_web.py
```

注意：必须在 `/backend` 目录下创建 `.env` 文件，自行输入`BASE_URL`及`API_KEY`等敏感信息

### 前端服务启动

进入前端目录 `/frontend/`，然后运行：

```bash
npm install  # 若未安装依赖，先执行一次
npm run serve
```


### 单元测试

使用 `test.ipynb` 进行功能函数单元测试，在 Jupyter Notebook 中运行即可

## 实验数据

所有实验输出保存在 `/output_eval_FRAMES-50/` 目录下

## 注意事项

* `.env` 文件是必须的，否则无法正常访问 LLM 接口。
* 前后端默认运行在本地，若需部署到生产环境，请自行调整相关配置。

