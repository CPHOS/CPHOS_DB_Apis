# CPHOS_DB_Apis

本仓库以 Python 作为数据库操作入口，通过 `db_api` 中封装的事务与操作类，对 CPHOS 后台阅卷系统数据库进行查询、审核、角色调整和学校信息维护。

## 目录结构

```text
db_api/
  DataQueryApis/        查询类 API
  DataManagingApis/     修改类 API
scripts/                常用批处理脚本模板
.env.example            数据库连接环境变量示例
.gitignore              本地环境、表格、缓存文件忽略规则
requirements.txt        Python 依赖
test.py                 API 使用示例
```

## 安装依赖

在仓库根目录执行：

```bash
pip install -r requirements.txt
```

Linux 或 macOS 环境中，如默认命令为 `python3`，可对应使用：

```bash
python3 -m pip install -r requirements.txt
```

## 数据库连接配置

复制示例文件并填写：

```powershell
Copy-Item .env.example .env
```

`CPHOS_DB_SHOW_TABLES=1` 时，连接成功后会打印数据库表名；设为 `0` 时跳过打印。

## 使用 API

脚本通常从 `db_api` 引入全局事务对象和具体操作类：

```python
from db_api import customTransaction
from db_api.DataQueryApis.GetTeacherInfoApis import GetTeacherInfoByName

teachers = customTransaction.executeOperation(GetTeacherInfoByName("张三"))
```

修改类操作执行后，需要明确调用事务提交：

```python
customTransaction.commit()
```

调试或试运行时，可调用：

```python
customTransaction.rollBack()
```

如果脚本结束前没有提交，`customTransaction` 析构时会回滚事务。

## scripts 目录

`scripts/` 中保存常用批处理脚本模板：

```text
Verify_individuals.py                 个人报名审核
Verify_teachers_leaders.py            领队教练审核
Verify_teachers_vice_leaders.py       副领队教练审核
ShowLeaders_unfinished.py             查看未完成批阅数量
AllCphosLeaders_RollBackToBeSup.py    将组委会学校下成员调整为负责人并设置科目
```

这些脚本中的 xlsx 输入、输出路径，运行前在本地填写对应路径变量。

**涉及数据库修改的脚本默认应在确认后再打开 `customTransaction.commit()`。运行前需要检查输入表格列规则、目标数据库环境和脚本最后的提交状态。**

