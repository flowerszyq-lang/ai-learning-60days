## src/agent/executor.py

**作用**：根据工具名和参数，动态执行对应的异步函数。
**Java 类比**：反射调用 `method.invoke()`。
**关键代码**：
```python
func = TOOL_REGISTRY[tool_name]["function"]
result = await func(**parameters)