# Cron Job 调试 Pitfalls（悬案回顾技能修复记录）

## 这次出了什么问题

cron任务的`skills`字段引用了一个不存在的skill名`session_search`。
运行时日志会显示：
```
[IMPORTANT: The following skill(s) were listed for this job but could not be found and skipped: session_search]
```

任务不会报错退出（status仍显示`ok`），但输出内容为空——因为skill加载失败导致prompt里的关键指令被跳过。

## 怎么检查

```bash
# 1. 列出所有cron任务，查看skills字段
hermes cron list

# 2. 查看某个任务的最近运行状态
hermes cron run <job_id>  # 手动触发一次测试

# 3. 检查skill是否存在
ls ~/.hermes/skills/ | grep <skill-name>
```

## 正确的做法

**不要在cron任务的skills字段里引用不存在的skill。**

如果任务需要查询历史对话，应该在prompt里直接调用`session_search`工具（这是内置工具，不是skill）：
```
## 工具
使用 session_search 工具搜索历史对话。
```

而不是：
```
## Skills
session_search   ← 错误：这个skill不存在！
```

## 修复操作记录

| 时间 | 任务 | 操作 |
|------|------|------|
| 2026-06-02 | 晨报-悬案回顾（工作日）job_id=f308c132634f | 清除skills依赖 |
| 2026-06-02 | 晨报-悬案回顾（节假日）job_id=7fe275be0d81 | 清除skills依赖 |

修复后两个任务不再引用任何skills，依赖内置工具完成功能。

## 经验

- cron任务的`sills`字段必须是已存在于`~/.hermes/skills/`的skill名
- 创建cron任务时，如果要用的功能是内置工具（如session_search），**不要**填在skills字段里
- 任务状态`ok`不等于输出正确——还要核验实际推送内容