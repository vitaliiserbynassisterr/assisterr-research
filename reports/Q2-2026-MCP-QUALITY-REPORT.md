# Q2 2026 MCP Server Quality Report
**Published**: 2026-04-08 · **Source**: Laureum.ai (laureum.ai)

> First public quality benchmark of remotely-accessible MCP servers, evaluated by Laureum's adversarial-probe-aligned evaluation pipeline. Each score is reproducible — every evaluation has a full audit trail (tool calls, judge prompts, sanitization events, probe executions) accessible via `GET /v1/admin/eval/{id}/audit`.

---

## Executive Summary

- **Total servers evaluated**: 27
- **Average overall score**: 68.5/100
- **Median score**: 80/100
- **Tools tested across all servers**: 125
- **Evaluations with full audit trail**: 27/27

### Tier distribution

| Tier | Count | % |
|---|---:|---:|
| Expert | 5 | 19% |
| Proficient | 13 | 48% |
| Basic | 3 | 11% |
| Failed | 6 | 22% |

### Average dimension scores (Laureum 6-axis)

| Dimension | Weight | Avg Score |
|---|:---:|---:|
| Accuracy | 35% | 61/100 |
| Safety | 20% | 66/100 |
| Reliability | 15% | 70/100 |
| Process Quality | 10% | 56/100 |
| Latency | 10% | 52/100 |
| Schema Quality | 10% | 83/100 |

---

## Top 10 by Overall Score

| # | Server | Score | Tier | Tools | Dimensions (acc/saf/rel/proc/lat/sch) |
|:---:|---|:---:|:---:|:---:|---|
| 1 | [Hf.Co](https://hf.co/mcp) | **93** | basic | 8 | 57/64/100/64/52/83 |
| 2 | [Coingecko](https://mcp.api.coingecko.com/mcp) | **93** | expert | 3 | 95/50/50/47/50/83 |
| 3 | [Javadocs](https://javadocs.dev/mcp) | **92** | expert | 3 | 93/50/50/45/50/83 |
| 4 | [Deepwiki](https://mcp.deepwiki.com/mcp) | **87** | expert | 3 | 88/71/50/61/93/83 |
| 5 | [Gitio](https://gitmcp.io/microsoft/TypeScript) | **86** | expert | 3 | 86/50/50/45/45/83 |
| 6 | [Gitio](https://gitmcp.io/anthropics/anthropic-cookbook) | **85** | expert | 3 | 85/50/50/45/0/83 |
| 7 | [Context7](https://mcp.context7.com/mcp) | **84** | proficient | 2 | 84/98/50/65/61/83 |
| 8 | [Openzeppelin](https://mcp.openzeppelin.com/contracts/solidity/mcp) | **82** | proficient | 8 | 73/92/100/61/85/83 |
| 9 | [Open.Dexter](https://open.dexter.cash/mcp) | **82** | proficient | 6 | 69/94/100/74/86/83 |
| 10 | [Gitio](https://gitmcp.io/facebook/react) | **82** | proficient | 3 | 81/50/50/45/49/83 |

---

## Spotlight: Solana DeFi (Dexter x402 Gateway)

**Server**: [Dexter x402 Gateway](https://open.dexter.cash/mcp)
**Score**: 82/100 · **Tier**: proficient · **Confidence**: 0.89

Dexter exposes 6 x402 protocol tools for Solana DeFi: search, pay, fetch, check, access, wallet. The flagship Solana case demonstrates Laureum's evaluation methodology applied to crypto-native infrastructure.

**Per-tool breakdown**:

| Tool | Score | Tests Passed |
|---|:---:|:---:|
| `x402_search` | 62 | 3/5 |
| `x402_pay` | 66 | 4/5 |
| `x402_fetch` | 66 | 4/5 |
| `x402_check` | 85 | 5/5 |
| `x402_access` | 76 | 5/5 |
| `x402_wallet` | 53 | 1/3 |

**Audit trail**: 195 records (166 tool calls + 28 judge calls + 1 sanitization event)
`GET /v1/admin/eval/93df9afe-06af-4e4a-801a-3a61b90b515e/audit`

---

## Methodology

All evaluations use Laureum's `certified` mode (Level 2 functional testing):

- **Tool functional tests**: Each tool exercised with 3-5 test cases (happy_path, edge_case, error_handling)
- **6-axis scoring**: accuracy (35%), safety (20%), reliability (15%), process_quality (10%), latency (10%), schema_quality (10%)
- **Adversarial probes**: 25 probe types covering OWASP LLM/Agentic/MCP Top 10 + 6 DeepMind Agent Trap categories
- **Multi-judge consensus**: Cerebras (llama3.1-8b) primary, Groq + OpenRouter fallback
- **Audit trail**: Every tool call, judge call, sanitization event, and probe execution persisted in MongoDB and queryable via admin endpoint

**Reference**: Laureum's evaluation pipeline implements coverage of:
- OWASP Top 10 for LLM Applications (8/10)
- OWASP Top 10 for Agentic Applications (9/10)
- OWASP MCP Top 10 (8/10)
- DeepMind "AI Agent Traps" taxonomy — Franklin et al. 2026 (15/19 testable trap types)

---

## Full Leaderboard

| Rank | Server | Score | Tier |
|:---:|---|:---:|:---:|
| 1 | [Hf.Co](https://hf.co/mcp) | 93 | basic |
| 2 | [Coingecko](https://mcp.api.coingecko.com/mcp) | 93 | expert |
| 3 | [Javadocs](https://javadocs.dev/mcp) | 92 | expert |
| 4 | [Deepwiki](https://mcp.deepwiki.com/mcp) | 87 | expert |
| 5 | [Gitio](https://gitmcp.io/microsoft/TypeScript) | 86 | expert |
| 6 | [Gitio](https://gitmcp.io/anthropics/anthropic-cookbook) | 85 | expert |
| 7 | [Context7](https://mcp.context7.com/mcp) | 84 | proficient |
| 8 | [Openzeppelin](https://mcp.openzeppelin.com/contracts/solidity/mcp) | 82 | proficient |
| 9 | [Open.Dexter](https://open.dexter.cash/mcp) | 82 | proficient |
| 10 | [Gitio](https://gitmcp.io/facebook/react) | 82 | proficient |
| 11 | [Gitio](https://gitmcp.io/openai/openai-python) | 82 | proficient |
| 12 | [Knowledge-Global.Aws](https://knowledge-mcp.global.api.aws) | 80 | proficient |
| 13 | [Usefulai.Fun](https://api.usefulai.fun/mcp) | 80 | proficient |
| 14 | [Gitio](https://gitmcp.io/docs) | 80 | proficient |
| 15 | [Exa](https://mcp.exa.ai/mcp) | 79 | proficient |
| 16 | [Docs.Astro.Build](https://mcp.docs.astro.build/mcp) | 77 | proficient |
| 17 | [Remote-Com](https://mcp.remote-mcp.com) | 72 | proficient |
| 18 | [Zip1](https://zip1.io/mcp) | 71 | proficient |
| 19 | [Manifold.Markets](https://api.manifold.markets/v0/mcp) | 68 | proficient |
| 20 | [Huggingface.Co](https://huggingface.co/mcp) | 63 | basic |
| 21 | [Gitio](https://gitmcp.io/tailwindlabs/tailwindcss) | 39 | failed |
| 22 | [Ferryhopper](https://mcp.ferryhopper.com/mcp) | 39 | basic |
| 23 | [Gitio](https://gitmcp.io/expressjs/express) | 38 | failed |
| 24 | [Gitio](https://gitmcp.io/vercel/next.js) | 31 | failed |
| 25 | [Gitio](https://gitmcp.io/fastapi/fastapi) | 29 | failed |
| 26 | [Gitio](https://gitmcp.io/langchain-ai/langchain) | 29 | failed |
| 27 | [Gitio](https://gitmcp.io/pallets/flask) | 26 | failed |

---

## About Laureum.ai

Laureum is a runtime quality verification platform for AI agents and MCP servers. Unlike static security scanners, Laureum connects to live MCP servers, exercises every tool, runs adversarial probes, and produces verifiable quality credentials (AQVC).

**Try it**: [laureum.ai/evaluate](https://laureum.ai/evaluate) — evaluate your MCP server in 60 seconds, no signup required.

**Battle arena**: [laureum.ai/battle](https://laureum.ai/battle) — head-to-head competitions between AI agents.

---

*Report generated 2026-04-08 from production MongoDB. Methodology, audit trails, and source code: [github.com/assister-xyz/quality-oracle](https://github.com/assister-xyz/quality-oracle)*