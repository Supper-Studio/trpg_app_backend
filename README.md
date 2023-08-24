<h1 align="center">Welcome to trpg_app_backend 👋</h1>

> 一个跑团解决方案，简化准备和游玩中的一些繁琐重复的过程。让新玩家更快上手，老玩家更有的放矢，尽可能让每一个人都有良好的游玩体验。
> 本仓库为后端服务，客户端代码见 [trpg_app_client]

## 🏠 克隆仓库

> 使用 SSH 地址克隆仓库，可以实现免密操作。具体配置方法见 [Github 密钥配置说明] 。
> 文档中所有以 `<>` 或者 `[]` 包围的内容都需要删除并替换为相应的值。例如：
>
> - `<branch>` -> `main`
> - `<your email>` -> `example@mail.com`

```bash
# 使用 SSH 克隆
git clone git@github.com:Supper-Studio/trpg_app_backend.git

# 使用 HTTPS 克隆
git clone https://github.com/Supper-Studio/trpg_app_backend.git

# 进入项目目录
cd ./trpg_app_backend

# 设置和 github 上相同的用户名和 Email
git config --local user.name <username>
git config --local user.email <email@example.com>
```

## 🐋 安装依赖

> 推荐使用 pipenv 新建一个虚拟环境来管理 pip 包，防止依赖冲突。具体使用方法见 [Pipenv 使用说明] 。

```bash
# 使用 pipenv 安装依赖并创建虚拟环境
# 安装完成后需要在 VS Code 中选择虚拟环境
pipenv sync -d

# 或使用 pip 直接在本地环境安装依赖
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

## ⚙️ 环境变量

> 请将敏感数据存放在根目录的 `.env` 文件中（需要手动创建，可以从 `.env.example` 文件中复制）

用到的环境变量参见 [环境配置示例]

## ⚠️ 注意事项

- 请不要使用 uvicorn 的 `reload` 参数，可能会导致日志分文件时出现错误
- 如果 VS Code 终端自动启动虚拟环境显示不能执行脚本，可以使用如下指令修改设置：

    ```bash
    # 需要以管理员权限启动 PowerShell
    Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
    ```

- 如果在碰到类型检查误报，在保证代码可运行的前提下可以在行尾添加注释暂时禁用类型检查：

    ```python
    with self._session_factory() as session:  # type: ignore
        yield session
    ```

- 在调试前需要在打开了虚拟环境的终端中使用指令启动一个 pysnowflake 服务，用来生成数据库所需的 ID ，指令的具体使用方法见 [pysnowflake 官方文档] ：

    ```shell
    snowflake_start_server [--port=PORT]
    ```

    > 请保证指定的端口与 `.env` 文件中 `ID_SERVICE_PORT` 的值一致

- 默认的调试信息将显示在调试控制台中，如果没有显示可以使用 `Ctrl + Shift + Y` 快捷键打开，也可以手动修改为使用内置终端显示：

    1. 打开项目目录下的 `.vscode/launch.json` 文件
    2. 修改其中 `console` 的值为 `integratedTerminal` 即可

## 🧩 所需插件

- [Python] 提供 Python 提示和类型检查。
- [git-commit-plugin] 用于生成 Commit 。

## 📋 更新日志

查看 [更新日志]

## 📄 相关文档

- [Git 简单使用说明]
- [Github 工作流程]
- [Fast API 官方文档]
- [Pydantic 官方文档]

<!-- Links -->

[环境配置示例]: ./.env.example
[更新日志]: ./CHANGELOG.md

[Pipenv 使用说明]: ./docs/pipenv-useages.md
[Github 密钥配置说明]: ./docs/github-key-generate.md
[Git 简单使用说明]: ./docs/git-useages.md
[Github 工作流程]: ./docs/github-workflow.md

[trpg_app_client]: https://github.com/Supper-Studio/trpg_app_client
[Python]: https://marketplace.visualstudio.com/items?itemName=ms-python.python
[git-commit-plugin]: https://marketplace.visualstudio.com/items?itemName=redjue.git-commit-plugin

[Fast API 官方文档]: https://fastapi.tiangolo.com/zh/
[Pydantic 官方文档]: https://pydantic-docs.helpmanual.io/
[pysnowflake 官方文档]: https://pysnowflake.readthedocs.io/en/latest/
