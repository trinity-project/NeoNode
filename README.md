# NEO  增强节点
> 通过josn rpc的方式对外提供与链交互的一些rpc 接口

## 服务运行步骤
- 安装python3.6, Mysql数据库
- 安装requirements.txt 所依赖的python库

    `pip install requirements_whl/*.whl`
    
- 在根目录下创建log文件夹
- 设置环境变量 CURRENT_ENVIRON  ,  PRIVTKEY , REMOTE_ADDRESS，WEB_API
- 运行2个脚本：
   + store_raw_block_data.py
   将块里面所有的交易存到本地Mysql
   + store_account_info.py
    从mysql读出所有的交易信息，计算出所有的地址的余额，零钱信息，存储交易记录
    
   + runserver.py
   启动  rpc 服务
   
   