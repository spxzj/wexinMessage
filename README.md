# 微信公众号爆款文章分析与仿写（Python）

这个项目可以：
1. 自动分析爆款微信公众号文章（HTML）结构特征。
2. 根据分析结果构造提示词，调用 AI 大模型模仿生成新文章。
3. 支持配置多个 API Keys，失败时自动切换重试。
4. 支持自由切换模型提供方：OpenAI、DeepSeek、阿里云百练（OpenAI 兼容模式）。

## 安装

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

## 配置

复制并修改示例配置：

```bash
cp configs/config.example.yaml configs/config.yaml
```

### provider 配置

`provider` 可选值：
- `openai`
- `deepseek`
- `aliyun_bailian`

每个 provider 都有默认 `base_url`、`model` 和环境变量名：

- `openai`：
  - 默认 base_url: `https://api.openai.com/v1`
  - 默认 model: `gpt-4o-mini`
  - 环境变量: `OPENAI_API_KEY`
- `deepseek`：
  - 默认 base_url: `https://api.deepseek.com/v1`
  - 默认 model: `deepseek-chat`
  - 环境变量: `DEEPSEEK_API_KEY`
- `aliyun_bailian`：
  - 默认 base_url: `https://dashscope.aliyuncs.com/compatible-mode/v1`
  - 默认 model: `qwen-plus`
  - 环境变量: `DASHSCOPE_API_KEY`

如果配置文件没有填写 `api_keys`，程序会自动读取对应 provider 的环境变量。

## 使用方式

```bash
wechat-writer \
  --source "https://mp.weixin.qq.com/s/xxxx" \
  --topic "普通人如何用 AI 提升工作效率" \
  --config "configs/config.yaml" \
  --extra "语气更接地气，加入一个真实感案例" \
  --output "generated_article.md"
```

也支持本地 HTML：

```bash
wechat-writer --source samples/demo_article.html --topic "你的主题"
```

## 输出

- 生成的文章默认写入 `output.md`（可通过 `--output` 修改）。
- 控制台会打印文章结构分析数据和当前 provider/model 信息。

## 注意事项

- 请确保对抓取或使用的文章内容符合平台规则与版权规范。
- 本项目默认调用 OpenAI 兼容 `chat/completions` 接口。
