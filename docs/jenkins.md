# Jenkins 配置与失败排查

## 环境变量

`.env` 被 Git 忽略，本机配置不会随 Jenkins 的 Git 检出自动同步。完整测试需要
`DB_PASSWORD`，供注册用例清理新建账号使用。其余数据库配置按 `.env.example`
提供的变量设置，指向专用测试库。

在 Jenkins 凭据中保存数据库密码（Secret text），然后在任务的构建环境中使用
Credentials Binding 将对应凭据绑定为 `DB_PASSWORD`。不要把密码写入仓库或
构建脚本。凭据 ID 使用 Jenkins 中实际创建的 ID。

## Execute shell 示例

以下 Python 和 Java 路径对应当前构建机；更换机器时调整路径：

```sh
set -eu
export JAVA_HOME=/opt/homebrew/opt/openjdk@21
export PATH=/Users/charlieliu/miniforge3/envs/pytest/bin:$JAVA_HOME/bin:/opt/homebrew/bin:/usr/bin:/bin

python --version
python -m pip install -r requirements.txt
python -c 'from settings import settings; settings.validate_database()'
python main.py --no-report
```

`validate_database()` 会在未提供密码时立即给出配置错误。`--no-report` 保留
`report/json_report` 下的测试结果，由 Jenkins 的 Allure 构建后操作生成 HTML，
避免 `main.py` 和插件各生成一次报告。

Allure 构建后操作的结果目录填写 `report/json_report`，与 pytest 配置一致。
测试失败时保留非零退出码，以便 Jenkins 正确标记失败并归档失败报告。

## 本次日志中的原因

- 商品创建返回 400：请求缺少必填 `mainImageUrl`，参数校验在分类校验之前失败，
  同时影响商品创建以及依赖临时商品的上架、下架、删除和图片用例。
- 订单前置返回 400：写死的地址 9 已不存在。订单和退款前置现改为创建当前用户
  的临时地址，并在结束后清理；HTTP 断言会显示业务 `code` 和 `msg`。
- 已上架商品改价返回 200：当前业务允许改价。用例已按确认后的规则验证改价成功，
  并查询保存后的价格和商品状态。
- 数据库用例跳过：Jenkins 未绑定 `DB_PASSWORD`。库存测试现使用临时商品，
  已移除数据库依赖；6 条注册用例仍需数据库权限完成账号清理。

修改后应提交并推送源码到任务跟踪的分支。只编辑 Jenkins 工作目录的文件可能会
被下一次 Git 检出覆盖；开始构建前应确认控制台记录的新提交号。
