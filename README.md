# LLM Negotiator Purple Agent

A **Claude-powered** negotiation agent for the [Meta-Game Negotiation Assessor](https://agentbeats.dev) on AgentBeats.

> **Note**: This agent uses the Anthropic API exclusively. It requires an `ANTHROPIC_API_KEY` and only works with Claude models.

## Overview

This purple agent uses Claude to make strategic negotiation decisions in OpenSpiel bargaining games. It reasons about valuations, BATNAs, and game theory to propose and evaluate offers.

## Quick Start

### Option 1: Use Pre-built Docker Image

```bash
docker pull ghcr.io/gsmithline/llm-negotiator-purple:latest

docker run -p 8080:8080 \
  -e ANTHROPIC_API_KEY=your_key_here \
  -e ANTHROPIC_MODEL=claude-sonnet-4-20250514 \
  ghcr.io/gsmithline/llm-negotiator-purple:latest
```

### Option 2: Run Locally

```bash
# Install dependencies
pip install "a2a-sdk[http-server]>=0.3.0" uvicorn starlette anthropic

# Set environment variables (copy sample.env to .env and edit)
cp sample.env .env
# Edit .env with your API key

# Or export directly
export ANTHROPIC_API_KEY=your_key_here
export ANTHROPIC_MODEL=claude-sonnet-4-20250514  # optional

# Run the agent
python main.py --host 0.0.0.0 --port 8080
```

### Option 3: Build from Source

```bash
docker build -t llm-negotiator-purple .
docker run -p 8080:8080 -e ANTHROPIC_API_KEY=your_key ghcr.io/gsmithline/llm-negotiator-purple
```

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `ANTHROPIC_API_KEY` | Yes | - | Your Anthropic API key |
| `ANTHROPIC_MODEL` | No | `claude-sonnet-4-20250514` | Claude model to use |
| `PORT` | No | `8080` | Server port |

## Supported Models

- `claude-sonnet-4-20250514` (default, recommended)
- `claude-opus-4-20250514`
- `claude-3-5-haiku-20241022`

## Register on AgentBeats

1. Push your image to a public registry (or use the pre-built one)
2. Go to [agentbeats.dev](https://agentbeats.dev)
3. Click "Register Agent"
4. Enter:
   - **Docker Image**: `ghcr.io/gsmithline/llm-negotiator-purple:latest`
   - **Name**: Your agent name
5. Note your `agentbeats_id` for use in scenarios

## Use in Leaderboard Evaluation

Add to your `scenario.toml`:

```toml
[[participants]]
agentbeats_id = "YOUR_AGENT_ID"
name = "challenger"
env = { ANTHROPIC_API_KEY = "${ANTHROPIC_API_KEY}", ANTHROPIC_MODEL = "claude-sonnet-4-20250514" }
```

**Important**: The participant name must be `challenger` (required by the green agent).

## How It Works

1. Receives negotiation state from the green agent (valuations, BATNA, offers)
2. Sends game state to Claude with strategic prompts
3. Claude reasons about optimal moves
4. Returns action: propose allocation, accept, or reject

## Files

- `main.py` - A2A server implementation
- `negotiator.py` - Claude-based negotiation logic
- `agent.toml` - Agent configuration
- `Dockerfile` - Container build

## Links

- **Green Agent**: [Meta-Game Negotiation Assessor](https://github.com/gsmithline/tutorial-agent-beats-comp)
- **Leaderboard**: [Meta-Game Leaderboard](https://github.com/gsmithline/meta-game-leaderboard)
- **AgentBeats**: [agentbeats.dev](https://agentbeats.dev)

## License

MIT
