# Quickstart Guide

Welcome to Moya! This guide will help you get started with the framework by walking you through installation, prerequisites, and basic usage.

## Installation

To install Moya, use the following command:

```bash
pip install moya-ai
```

## Prerequisites

Before using Moya, ensure you have the following:

- Python 3.11 or higher
- API keys for any external services you plan to use (e.g., OpenAI, AWS Bedrock)

## Basic Usage

Here’s a simple example to create and use an OpenAI agent:

```python
from moya.agents.openai_agent import OpenAIAgent

# Initialize the agent
agent = OpenAIAgent(api_key="your-api-key")

# Generate a response
response = agent.generate_text(prompt="What is Moya?")
print(response)
```

## Running Examples

Moya includes several example scripts to help you get started. To run an example:

1. Navigate to the `examples/` directory.
2. Run the desired script using Python:

```bash
python examples/quick_start_openai.py
```

For more detailed tutorials and guides, explore the other sections of this documentation.