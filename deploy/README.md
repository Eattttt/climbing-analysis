# 部署说明

## 服务器端 (47.253.86.69)

```bash
# 1. 下载 frp
wget https://github.com/fatedier/frp/releases/download/v0.61.1/frp_0.61.1_linux_amd64.tar.gz
tar xzf frp_0.61.1_linux_amd64.tar.gz
cd frp_0.61.1_linux_amd64

# 2. 复制配置文件
# 把 deploy/frps.toml 传到服务器，放到 frps.toml

# 3. 启动
./frps -c frps.toml
```

## 本地 PC

```bash
# 1. 下载 frp (Windows)
# https://github.com/fatedier/frp/releases/download/v0.61.1/frp_0.61.1_windows_amd64.zip

# 2. 把 deploy/frpc.toml 放到 frp 目录

# 3. 启动客户端
frpc.exe -c frpc.toml

# 4. 启动服务
cd backend && uvicorn app.main:app --host 0.0.0.0 --port 8001
cd frontend && npm run dev
```

## 访问

公网地址: http://47.253.86.69:8889
