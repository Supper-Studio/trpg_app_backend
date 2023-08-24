# Git简单使用

## Git配置和安装

> 安装Git的方法可以看 [廖老师的教程](https://www.liaoxuefeng.com/wiki/896043488029600/896067074338496)

### 防止Git提交乱码

如果你提交时是用中文写的提交注释那在使用 `git log` 指令是会显示出一堆乱码，十分影响体验。可以使用下面的设置来避免。

```bash
# 设置 git 界面编码为 utf-8
git config —-global gui.encoding utf-8

# 设置 git 提交 commit 时使用 utf-8 编码
git config --global i18n.commitencoding utf-8

# 设置使用 git log 指令时使用 gbk 编码
git config --global i18n.logoutputencoding gbk
```

## 常用Git操作

这里收集了一些常用的Git操作，想查看全部指令或 flag 可以在指令后添加 `-h` 参数。

### 新建仓库

```bash
# 使用git init指令初始化本地仓库
git init
```

### 克隆仓库

```bash
# 拉取远程仓库
git clone <repo url>

# 拉取远程仓库指定分支的代码
git clone -b <branch> <repo url>
```

### 操作远程仓库

```bash
# 查看远程仓库
git remote -v

# 添加远程仓库
git remote add <remote> <repo url>

# 修改远程仓库 url
git remote set-url <remote> <new url>

# 删除远程仓库
git remote rm <remote>

# 重命名远程仓库
git remote rename <old remote> <new remote>
```

### 操作本地仓库

```bash
# 从远程仓库拉取
git pull <remote> <branch>

# 推送到远程仓库的新分支
git push -u <remote> <branch>
```

### 分支操作

```bash
# 切换分支
#
# <option> 可选项：
#
#       -f  强制切换
#       -m  切换并合并修改
#       -b  切换并新建分支
#
git checkout [option] <branch>

# 查看分支
#
# <option> 可选项：
#
#       -a  查看全部本地和远程分支
#       -vv 查看仓库中关联的远程分支
#
git branch [option]

# 重命名分支
git branch -m <old branch> <new branch>

# 删除完全合并的分支
git branch -d <branch>

# 指定关联远程分支
git branch -u <remote>/<branch>

# 将指定分支合并到当前所在分支
git merge <branch>
```

### 暂存区

```bash
# 将工作区中的修改放入暂存区
git stash

# 取出暂存区中的修改
git stash pop
```

### 暂存文件和提交

```bash
# 暂存修改过的文件或文件夹
git add <filename1> <filename2> ...
git add <dir>

# 创建提交
git commit -m <message>
