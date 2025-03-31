# Agents in Moya

Agents are the core components of the Moya framework. They represent different AI models or services that can perform tasks, interact with users, or collaborate with other agents. Moya provides several built-in agents, each tailored for specific use cases.

## Overview

Agents in Moya are designed to:

- Interface with external AI services (e.g., OpenAI, Azure OpenAI, Bedrock).
- Perform specific tasks such as text generation, classification, or conversation.
- Collaborate with other agents to solve complex problems.

## Built-in Agents

### 1. OpenAI Agent

**File:** `moya/agents/openai_agent.py`

The OpenAI Agent integrates with OpenAI's GPT models. It supports text generation, conversation, and other GPT-based tasks.

#### Key Features:
- Supports GPT-3.5 and GPT-4 models.
- Configurable temperature and max tokens.
- Handles API key authentication.

#### Example Usage:
```python
from moya.agents.openai_agent import OpenAIAgent

agent = OpenAIAgent(api_key="your-api-key")
response = agent.generate_text(prompt="What is Moya?")
print(response)
```

### 2. Azure OpenAI Agent

**File:** `moya/agents/azure_openai_agent.py`

The Azure OpenAI Agent integrates with Azure's OpenAI service. It is similar to the OpenAI Agent but uses Azure's infrastructure.

#### Key Features:
- Supports Azure-specific authentication.
- Configurable endpoint and deployment ID.

#### Example Usage:
```python
from moya.agents.azure_openai_agent import AzureOpenAIAgent

agent = AzureOpenAIAgent(api_key="your-api-key", endpoint="your-endpoint")
response = agent.generate_text(prompt="Explain Azure OpenAI integration.")
print(response)
```

### 3. Bedrock Agent

**File:** `moya/agents/bedrock_agent.py`

The Bedrock Agent integrates with AWS Bedrock, enabling access to foundation models hosted on AWS.

#### Key Features:
- Supports multiple foundation models.
- AWS-specific authentication using boto3.

#### Example Usage:
```python
from moya.agents.bedrock_agent import BedrockAgent

agent = BedrockAgent(region="us-east-1")
response = agent.generate_text(prompt="What is AWS Bedrock?")
print(response)
```

### 4. Ollama Agent

**File:** `moya/agents/ollama_agent.py`

The Ollama Agent integrates with Ollama's AI services for text generation and conversation.

#### Key Features:
- Lightweight and easy to configure.
- Supports Ollama-specific APIs.

#### Example Usage:
```python
from moya.agents.ollama_agent import OllamaAgent

agent = OllamaAgent(api_key="your-api-key")
response = agent.generate_text(prompt="Tell me about Ollama.")
print(response)
```

### 5. Remote Agent

**File:** `moya/agents/remote_agent.py`

The Remote Agent allows interaction with agents hosted on remote servers. It supports authentication and secure communication.

#### Key Features:
- Supports token-based authentication.
- Configurable server URL.

#### Example Usage:
```python
from moya.agents.remote_agent import RemoteAgent

agent = RemoteAgent(server_url="http://localhost:8000", auth_token="your-token")
response = agent.send_request(data={"task": "summarize", "text": "Moya is a framework..."})
print(response)
```

## Custom Agents

Moya allows you to create custom agents by extending the base `Agent` class. This is useful for integrating with new AI services or implementing custom logic.

#### Example:
```python
from moya.agents.agent import Agent

class CustomAgent(Agent):
    def perform_task(self, task_data: dict) -> dict:
        # Custom logic here
        return {"result": "Task completed"}

agent = CustomAgent()
response = agent.perform_task(task_data={"task": "example"})
print(response)
```

## Additional Notes

- Refer to the individual agent files for more details on configuration and usage.
- Ensure you have the necessary API keys and credentials set up before using the agents.
- For further assistance, consult the [Getting Started Guide](getting-started.md).