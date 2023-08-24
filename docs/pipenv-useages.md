# Pipenv 简单使用说明

> 简单介绍如何安装和使用 pipenv 设置部分可以看： [修改pip源和虚拟环境位置]

## 安装

```bash
pip install pipenv
```

## 虚拟环境操作

```bash
# 创建虚拟环境
pipenv install

# 激活虚拟环境
pipenv shell

# 退出虚拟环境
exit

# 删除虚拟环境
pipenv --rm
```

## 管理 pip 包

> 建议先启动虚拟环境再管理 pip 包，pipenv 兼容 pip 的所有指令，完整指令见 [pip官方文档]

```bash
# 安装 pip 包
pipenv install <package>

# 安装只有开发环境用到的 pip 包
pipenv install --dev <package>

# 卸载 pip 包
pipenv uninstall <package>

# 升级全部 pip 包
# 一次性更新全部 pip 包很危险，建议先确定可行后单独更新包
pipenv update

# 升级指定 pip 包
pipenv update <package>

# 更新依赖记录文件
# 进行任何对于依赖的修改之后都必须使用此指令
pipenv requirements > requirements.txt
pipenv requirements --dev-only > requirements-dev.txt
```

## 附录

最后附上我自己常用的 PowerShell 的相关配置，只需要打 `venv` 然后按 `Tab` 看提示选择即可，有不想记指令的可以拿走。

### 使用方式

1. 使用下面的指令用 VS Code 打开 PowerShell 配置文件（用别的编辑器也可以）：

    ```bash
    code $PROFILE
    ```

2. 将下面的配置文件粘贴进去然后保存重新打开 PowerShell 。

### 配置内容

```powershell
# 创建虚拟环境
function CreateVirtualEnvironment {
    pipenv install
    pipenv install --dev
    venv-activate
}
Set-Alias -Name 'venv-setup' -Value 'CreateVirtualEnvironment'

# 激活虚拟环境
function ActivateVirtualEnvironment {
    if (-not (Test-Path -Path $("$(Get-Location)" + "\PIPENV_VENV_IN_PROJECT\*"))) {
        pipenv shell -nologo
    } else {
        ./PIPENV_VENV_IN_PROJECT/*/Scripts/Activate.ps1
    }
}
Set-Alias -Name 'venv-activate' -Value 'ActivateVirtualEnvironment'

# 关闭虚拟环境
function DeactivateVirtualEnvironment {
    exit
}
Set-Alias -Name 'venv-deactivate' -Value 'DeactivateVirtualEnvironment'

# 移除虚拟环境
function RemoveVirtualEnvironment {
    pipenv --rm
}
Set-Alias -Name 'venv-remove' -Value 'RemoveVirtualEnvironment'

# 通过文件安装依赖
function InstallRequirement {
    if (Test-Path -Path $("$(Get-Location)" + "\requirements.txt")) {
        pipenv install -r requirements.txt
    } else {
        pipenv install
    }
    if (Test-Path -Path  $("$(Get-Location)" + "\requirements-dev.txt")) {
        pipenv install --dev -r requirements-dev.txt
    } else {
        pipenv install --dev
    }
}
Set-Alias -Name 'venv-install' -Value 'InstallRequirement'

# 生成依赖列表
function RecordRequirement {
    pipenv requirements > requirements.txt
    pipenv requirements --dev-only > requirements-dev.txt
}
Set-Alias -Name 'venv-record' -Value 'RecordRequirement'
```

<!-- Links -->

[修改pip源和虚拟环境位置]: https://blog.csdn.net/maixiaochai/article/details/107689387
[pip官方文档]: https://pip.pypa.io/en/stable/user_guide/#installing-packages
