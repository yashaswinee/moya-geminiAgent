# Memory in Moya

The Memory module in Moya is designed to manage and store information that agents can use during their interactions. It provides a structured way to retain context, track conversations, and store relevant data for future use.

## Overview

Memory in Moya serves the following purposes:

- **Context Retention**: Store and retrieve information to maintain context across interactions.
- **Conversation History**: Keep track of user-agent conversations.
- **Data Storage**: Save relevant data for agents to access during task execution.

## Key Components

### 1. BaseMemory

**File:** `moya/memory/base_memory.py`

The `BaseMemory` class is the foundation for all memory implementations in Moya. It defines the basic structure and methods that all memory classes must implement.

#### Key Methods:
- `store(key: str, value: Any) -> None`: Stores a value with the given key.
- `retrieve(key: str) -> Any`: Retrieves the value associated with the given key.
- `clear() -> None`: Clears all stored data.

#### Example Usage:
```python
from moya.memory.base_memory import BaseMemory

class CustomMemory(BaseMemory):
    def __init__(self):
        self.data = {}

    def store(self, key: str, value: Any) -> None:
        self.data[key] = value

    def retrieve(self, key: str) -> Any:
        return self.data.get(key)

    def clear(self) -> None:
        self.data.clear()

memory = CustomMemory()
memory.store("greeting", "Hello, world!")
print(memory.retrieve("greeting"))
```

### 2. ConversationMemory

**File:** `moya/memory/conversation_memory.py`

The `ConversationMemory` class is a specialized memory implementation for storing conversation history. It is used to maintain context in multi-turn interactions.

#### Key Features:
- Stores conversation history as a list of messages.
- Provides methods to add and retrieve messages.

#### Example Usage:
```python
from moya.memory.conversation_memory import ConversationMemory

memory = ConversationMemory()
memory.add_message("user", "What is Moya?")
memory.add_message("agent", "Moya is an AI framework.")
print(memory.get_history())
```

### 3. PersistentMemory

**File:** `moya/memory/persistent_memory.py`

The `PersistentMemory` class extends `BaseMemory` to provide persistent storage. It uses a database or file system to store data that persists across sessions.

#### Key Features:
- Supports persistent storage using SQLite or JSON files.
- Provides methods to save and load data.

#### Example Usage:
```python
from moya.memory.persistent_memory import PersistentMemory

memory = PersistentMemory(file_path="memory.json")
memory.store("session_id", "12345")
print(memory.retrieve("session_id"))
```

## Custom Memory Implementations

You can create custom memory classes by extending the `BaseMemory` class. This allows you to implement memory tailored to your specific use case.

#### Example:
```python
from moya.memory.base_memory import BaseMemory

class CustomMemory(BaseMemory):
    def __init__(self):
        self.data = {}

    def store(self, key: str, value: Any) -> None:
        self.data[key] = value

    def retrieve(self, key: str) -> Any:
        return self.data.get(key)

    def clear(self) -> None:
        self.data.clear()

memory = CustomMemory()
memory.store("example", "This is a custom memory implementation.")
print(memory.retrieve("example"))
```

## Additional Notes

- Ensure that memory implementations are thread-safe if used in multi-threaded environments.
- Use `PersistentMemory` for scenarios where data needs to persist across sessions.
- Refer to the individual memory class files for more details on configuration and usage.