FROM python:3.9-slim

# 安装依赖（包括编译工具）
RUN apt-get update && \
    apt-get install -y \
    build-essential \
    python3-dev \
    git \
    postgresql-client \
    apache2 && \
    rm -rf /var/lib/apt/lists/*

# 复制启动脚本和修复脚本
COPY entrypoint.sh /entrypoint.sh
COPY fix_autosploit.py /fix_autosploit.py
RUN chmod +x /entrypoint.sh /fix_autosploit.py

# 克隆 AutoSploit
RUN git clone https://github.com/20240608/AutoSploit.git /AutoSploit
WORKDIR /AutoSploit

# 运行修复脚本
RUN python3 /fix_autosploit.py

# 安装 Python 依赖
RUN pip install -r requirements.txt

EXPOSE 4444

CMD ["/entrypoint.sh"]

