# Guides

Moya provides detailed guides to help you understand and utilize its features effectively. Below are some of the key guides available:

## Creating Agents

Learn how to create and configure agents in Moya. Agents are the core components that perform tasks and interact with users.

### Example:
```python
from moya.agents.openai_agent import OpenAIAgent

agent = OpenAIAgent(api_key="your-api-key")
response = agent.generate_text(prompt="Hello, Moya!")
print(response)
```

## Managing Memory

Understand how to use Moya's memory module to store and retrieve information during interactions.

### Example:
```python
from moya.memory.conversation_memory import ConversationMemory

memory = ConversationMemory()
memory.add_message("user", "What is Moya?")
memory.add_message("agent", "Moya is an AI framework.")
print(memory.get_history())
```

## Building Multi-Agent Systems

Learn how to create systems with multiple agents that collaborate to solve complex tasks.

### Example:
```python
from moya.orchestrators.sequential_orchestrator import SequentialOrchestrator

orchestrator = SequentialOrchestrator()
orchestrator.add_agent("Agent1")
orchestrator.add_agent("Agent2")
result = orchestrator.execute_workflow({"tasks": ["task1", "task2"]})
print(result)
```

## Streaming Responses

Explore how to implement streaming responses for real-time interactions.

### Example:
```python
from moya.agents.openai_agent import OpenAIAgent

agent = OpenAIAgent(api_key="your-api-key")
for chunk in agent.stream_response(prompt="Stream this response."):
    print(chunk)
```