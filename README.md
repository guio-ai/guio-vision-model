<a href="https://livekit.io/">
  <img src="./.github/assets/livekit-mark.png" alt="LiveKit logo" width="100" height="100">
</a>

# LiveKit Agents Starter - Python

A complete starter project for building voice AI apps with [LiveKit Agents for Python](https://github.com/livekit/agents) and [LiveKit Cloud](https://cloud.livekit.io/).

The starter project includes:

- A simple voice AI assistant, ready for extension and customization
- A voice AI pipeline built on [LiveKit Inference](https://docs.livekit.io/agents/models/inference), providing zero-configuration access to [models](https://docs.livekit.io/agents/models) from top labs
  - Uses the fast, open-weight Gemma 4 31B model, [hosted by LiveKit](https://docs.livekit.io/agents/models/llm/livekit/) and tuned for optimal performance in voice AI, as the default LLM
  - Uses Fish Audio S2.1 Pro for TTS, which renders the inline delivery markup that expressive mode relies on
  - Supports more than 50 models from OpenAI, Cartesia, Deepgram, and other providers
  - Access to a wide range of other models, including [Realtime models](https://docs.livekit.io/agents/models/realtime), through extensive plugin ecosystem
- Expressive mode, enabled by default: the framework injects the TTS provider's markup guide into the LLM prompt, so the model emits inline delivery tags (emotion, pacing, non-verbal sounds) that the TTS renders and the transcript never shows
- Eval suite based on the LiveKit Agents [testing & evaluation framework](https://docs.livekit.io/agents/start/testing/)
- [LiveKit Turn Detector](https://docs.livekit.io/agents/logic/turns/turn-detector/), an end-of-turn model that listens to the user's audio directly, combining semantic understanding with acoustic cues for state-of-the-art accuracy across 14 languages
- [Background voice cancellation](https://docs.livekit.io/transport/media/noise-cancellation/)
- Deep session insights from LiveKit [Agent Observability](https://docs.livekit.io/deploy/observability/)
- A Dockerfile ready for [production deployment to LiveKit Cloud](https://docs.livekit.io/deploy/agents/)

This starter app is compatible with any [custom web/mobile frontend](https://docs.livekit.io/frontends/) or [telephony](https://docs.livekit.io/telephony/).

## Using coding agents

This project is designed to work with coding agents like [Claude Code](https://claude.com/product/claude-code), [Cursor](https://www.cursor.com/), and [Codex](https://openai.com/codex/).

For your convenience, LiveKit offers both a CLI and an [MCP server](https://docs.livekit.io/reference/developer-tools/docs-mcp/) that can be used to browse and search its documentation. The [LiveKit CLI](https://docs.livekit.io/intro/basics/cli/) (`lk docs`) works with any coding agent that can run shell commands. Install it for your platform:

**macOS:**

```console
brew install livekit-cli
```

**Linux:**

```console
curl -sSL https://get.livekit.io/cli | bash
```

**Windows:**

```console
winget install LiveKit.LiveKitCLI
```

The `lk docs` subcommand requires version 2.15.0 or higher. Check your version with `lk --version` and update if needed. Once installed, your coding agent can search and browse LiveKit documentation directly from the terminal:

```console
lk docs search "voice agents"
lk docs get-page /agents/start/voice-ai-quickstart
```

See the [Using coding agents](https://docs.livekit.io/intro/coding-agents/) guide for more details, including MCP server setup.

The project includes a complete [AGENTS.md](AGENTS.md) file for these assistants. You can modify this file to suit your needs. To learn more about this file, see [https://agents.md](https://agents.md).

## Dev Setup

Create a project from this template with the LiveKit CLI (recommended):

```bash
lk cloud auth
lk agent init my-agent --template agent-starter-python
```

The CLI clones the template and configures your environment. Then follow the rest of this guide from [Run the agent](#run-the-agent).

<details>
<summary>Alternative: Manual setup without the CLI</summary>

Clone the repository and install dependencies to a virtual environment:

```console
cd agent-starter-python
uv sync
```

Sign up for [LiveKit Cloud](https://cloud.livekit.io/) then set up the environment by copying `.env.example` to `.env.local` and filling in the required keys:

- `LIVEKIT_URL`
- `LIVEKIT_API_KEY`
- `LIVEKIT_API_SECRET`

You can load the LiveKit environment automatically using the [LiveKit CLI](https://docs.livekit.io/intro/basics/cli/):

```bash
lk cloud auth
lk app env --write --destination .env.local
```

</details>

## Run the agent

Run this command to speak to your agent directly in your terminal:

```console
uv run python src/agent.py console
```

To run the agent for use with a frontend or telephony, use the `dev` command:

```console
uv run python src/agent.py dev
```

In production, use the `start` command:

```console
uv run python src/agent.py start
```

## Run with Docker Compose

[`docker-compose.yaml`](docker-compose.yaml) builds the image from the `Dockerfile`, injects secrets from `.env.local`, persists downloaded model files in the named volume `guio-agent-cache`, and runs the agent on its own bridge network `guio-livekit`. The agent only dials out to LiveKit, so the sole published port is the health check on `127.0.0.1:8081`.

Copy `.env.example` to `.env.local`, fill in your LiveKit Cloud credentials and `OPENAI_API_KEY`, then:

```console
docker compose up --build -d
docker compose logs -f agent
curl -i http://127.0.0.1:8081/
```

The health check returns `200` once the agent server is registered with LiveKit and `503` otherwise.

### Local LiveKit server

[`docker-compose.local.yaml`](docker-compose.local.yaml) adds a self-hosted `livekit-server` on the same network. Both containers read the LiveKit settings from `.env.local`: the agent connects to `LIVEKIT_URL`, and the server registers `LIVEKIT_API_KEY` / `LIVEKIT_API_SECRET` as its API key pair, so they cannot drift apart. Set these in `.env.local` (the secret must be at least 32 characters):

```ini
LIVEKIT_URL=ws://livekit-server:7880
LIVEKIT_API_KEY=devkey
LIVEKIT_API_SECRET=local-dev-secret-not-for-production
```

Then start the stack. Nothing leaves your machine:

```console
docker compose -f docker-compose.yaml -f docker-compose.local.yaml up --build
```

Clients on this machine connect to `ws://localhost:7880` with a token minted from the same key and secret:

```console
set -a; source .env.local; set +a
lk token create --join --room demo --identity me --valid-for 24h
```

The server is configured in [`livekit/livekit.yaml`](livekit/livekit.yaml) and publishes 7880 (signaling), 7881/tcp and 7882/udp (media). If a browser or app on your machine joins a room but gets no media, the server is advertising its container IP. Pass your machine's LAN IP so it advertises a reachable address instead:

```console
LIVEKIT_NODE_IP=192.168.1.20 docker compose -f docker-compose.yaml -f docker-compose.local.yaml up
```

### Stopping

`docker compose down` sends `SIGTERM`, which puts the agent server in draining mode, and waits up to 10 minutes (`stop_grace_period`) for active sessions to finish. Use `docker compose down -t 5` to cut that short during development. The model cache volume survives `down`; add `-v` to delete it.

## Frontend & Telephony

Get started quickly with our pre-built frontend starter apps, or add telephony support:

| Platform | Link | Description |
|----------|----------|-------------|
| **Web** | [`livekit-examples/agent-starter-react`](https://github.com/livekit-examples/agent-starter-react) | Web voice AI assistant with React & Next.js |
| **iOS/macOS** | [`livekit-examples/agent-starter-swift`](https://github.com/livekit-examples/agent-starter-swift) | Native iOS, macOS, and visionOS voice AI assistant |
| **Flutter** | [`livekit-examples/agent-starter-flutter`](https://github.com/livekit-examples/agent-starter-flutter) | Cross-platform voice AI assistant app |
| **React Native** | [`livekit-examples/voice-assistant-react-native`](https://github.com/livekit-examples/voice-assistant-react-native) | Native mobile app with React Native & Expo |
| **Android** | [`livekit-examples/agent-starter-android`](https://github.com/livekit-examples/agent-starter-android) | Native Android app with Kotlin & Jetpack Compose |
| **Web Embed** | [`livekit-examples/agent-starter-embed`](https://github.com/livekit-examples/agent-starter-embed) | Voice AI widget for any website |
| **Telephony** | [Documentation](https://docs.livekit.io/telephony/) | Add inbound or outbound calling to your agent |

For advanced customization, see the [complete frontend guide](https://docs.livekit.io/frontends/).

## Tests and evals

Simulations run full multi-turn conversations between a simulated user and your agent on LiveKit Cloud, then judge each transcript. The scenarios live in [`scenarios.yaml`](scenarios.yaml). Run them locally with the [LiveKit CLI](https://docs.livekit.io/intro/basics/cli/):

```console
lk agent simulate --scenarios scenarios.yaml
```

The `Simulations` workflow in `.github/workflows/simulations.yml` runs the same file on every merge to `main` and on demand from the Actions tab. It runs there rather than on every pull request push because each run spends real inference. See the [simulations guide](https://docs.livekit.io/agents/start/testing/simulations/) for how to write scenarios and read results.

For turn-level checks that don't need a live session, the LiveKit Agents [testing & evaluation framework](https://docs.livekit.io/agents/start/testing/) runs your agent in-process under `pytest`. A commented-out example lives in [`tests/test_agent.py`](tests/test_agent.py).

## Using this template repo for your own project

Once you've started your own project based on this repo, you should:

1. **Check in your `uv.lock`**: This file is currently untracked for the template, but you should commit it to your repository for reproducible builds and proper configuration management. (The same applies to `livekit.toml`, if you run your agents in LiveKit Cloud)

2. **Add your own repository secrets**: You must [add secrets](https://docs.github.com/en/actions/how-tos/writing-workflows/choosing-what-your-workflow-does/using-secrets-in-github-actions) for `LIVEKIT_URL`, `LIVEKIT_API_KEY`, and `LIVEKIT_API_SECRET` so that the simulations can run in CI.

## Deploying to production

This project is production-ready and includes a working `Dockerfile`. To deploy it to LiveKit Cloud or another environment, see the [deploying to production](https://docs.livekit.io/deploy/agents/) guide.

### Continuous deployment with GitHub Actions

[`.github/workflows/deploy.yml`](.github/workflows/deploy.yml) deploys the agent to LiveKit Cloud with the LiveKit CLI. Every push to `main` that changes a file shipped in the image runs `lk agent deploy`. LiveKit Cloud builds the `Dockerfile` and rolls the new version out without interrupting active sessions.

Configure these GitHub Actions secrets at the organization or repository level:

| Secret | Used for |
|--------|----------|
| `LIVEKIT_URL`, `LIVEKIT_API_KEY`, `LIVEKIT_API_SECRET` | Authenticating the CLI against your LiveKit Cloud project |
| `OPENAI_API_KEY` | Injected into the agent container at runtime |

Add further runtime secrets in the "Write agent secrets" step of the workflow. A placeholder whose GitHub secret is not set yet is skipped with a warning. LiveKit Cloud supplies the agent's own `LIVEKIT_*` variables, so those are never passed as agent secrets.

**First deployment:** run the workflow from the Actions tab with `operation` set to `create`. It registers the agent, deploys it, and opens a pull request that adds the generated `livekit.toml` (project subdomain and agent id, no secrets). Merge it, and later pushes deploy automatically. Opening the pull request requires "Allow GitHub Actions to create and approve pull requests" in the repository or organization Actions settings. If that is off, download the `livekit-toml` artifact from the run and commit the file yourself.

Manual runs can also target a [non-production deployment](https://docs.livekit.io/deploy/agents/deployments/) through the `deployment` input.

## Self-hosted LiveKit

You can also self-host LiveKit instead of using LiveKit Cloud. See the [self-hosting](https://docs.livekit.io/transport/self-hosting/local/) guide for more information. If you choose to self-host, you'll need to also use [model plugins](https://docs.livekit.io/agents/models/#plugins) instead of LiveKit Inference and will need to remove the [LiveKit Cloud noise cancellation](https://docs.livekit.io/transport/media/noise-cancellation/) plugin.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
