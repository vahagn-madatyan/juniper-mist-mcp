---
version: 1
models:
  research:
    model: moonshotai/kimi-k2.5
    fallbacks:
      - deepseek/deepseek-v3.2
      - minimax/minimax-m2.5

  planning:
    model: deepseek/deepseek-v3.2
    fallbacks:
      - moonshotai/kimi-k2.5
      - x-ai/grok-4.1-fast

  execution:
    model: minimax/minimax-m2.5
    fallbacks:
      - qwen/qwen3-coder
      - qwen/qwen3-coder-next

  completion:
    model: google/gemini-3-flash-preview
    fallbacks:
      - google/gemini-2.5-flash
      - anthropic/claude-sonnet-4.6
---