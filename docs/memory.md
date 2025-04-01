# Memory in Moya

The Memory module in Moya is designed to manage and store information about conversations that agents can use during their interactions. It provides a structured way to retain context, track conversations, and store message history for future use.

## Overview

Memory in Moya serves the following purposes:

- **Context Retention**: Store and retrieve conversation data to maintain context across interactions.
- **Conversation History**: Keep track of user-agent conversations through thread and message storage.
- **Persistence Options**: Store conversation data either in memory or in a file system.

## Key Components

### 1. Repository

**File:** `moya/memory/repository.py`

The `Repository` class is an abstract base class that defines the interface for all memory repository implementations in Moya. It specifies the methods that must be implemented to store and retrieve conversation threads and messages.

#### Key Methods:
- `create_thread(thread: Thread) -> None`: Stores a new conversation thread.
- `get_thread(thread_id: str) -> Optional[Thread]`: Retrieves a thread by its ID.
- `append_message(thread_id: str, message: Message) -> None`: Adds a message to an existing thread.
- `list_threads() -> List[str]`: Lists all thread IDs in the repository.
- `delete_thread(thread_id: str) -> None`: Removes a thread and its messages from the repository.

#### Example Usage:
```python
from moya.memory.repository import Repository
from moya.conversation.thread import Thread
from moya.conversation.message import Message

# Using a concrete implementation of Repository
repository = ConcreteRepository()

# Create a new thread
thread = Thread(thread_id="conversation_1")
repository.create_thread(thread)

# Add a message to the thread
message = Message(thread_id="conversation_1", sender="user", content="Hello, Moya!")
repository.append_message("conversation_1", message)

# Retrieve the thread
retrieved_thread = repository.get_thread("conversation_1")
```

### 2. InMemoryRepository

**File:** `moya/memory/in_memory_repository.py`

The `InMemoryRepository` class is a concrete implementation of the `Repository` interface that stores conversation threads and messages in memory using Python dictionaries.

#### Key Features:
- Provides in-memory storage of threads and messages
- Fast access but data is lost when the program terminates
- Useful for testing and simple applications

#### Example Usage:
```python
from moya.memory.in_memory_repository import InMemoryRepository
from moya.conversation.thread import Thread
from moya.conversation.message import Message

# Create an in-memory repository
repository = InMemoryRepository()

# Create and store a thread
thread = Thread(thread_id="conversation_1")
repository.create_thread(thread)

# Add messages to the thread
message1 = Message(thread_id="conversation_1", sender="user", content="What is Moya?")
repository.append_message("conversation_1", message1)

message2 = Message(thread_id="conversation_1", sender="agent", content="Moya is an AI framework.")
repository.append_message("conversation_1", message2)

# Get the thread with its messages
thread = repository.get_thread("conversation_1")
for message in thread.messages:
    print(f"{message.sender}: {message.content}")
```

### 3. FileSystemRepository

**File:** `moya/memory/file_system_repo.py`

The `FileSystemRepository` class is a concrete implementation of the `Repository` interface that stores conversation threads and messages as JSON files in the file system.

#### Key Features:
- Provides persistent storage using JSON files
- Each thread is stored as a separate file with thread metadata and messages
- Data persists across program restarts
- Suitable for applications that need to maintain conversation history

#### Example Usage:
```python
from moya.memory.file_system_repo import FileSystemRepository
from moya.conversation.thread import Thread
from moya.conversation.message import Message

# Create a file system repository
repository = FileSystemRepository(base_path="./moya_memory")

# Create and store a thread
thread = Thread(thread_id="conversation_1", metadata={"user_id": "user123"})
repository.create_thread(thread)

# Add a message to the thread
message = Message(
    thread_id="conversation_1",
    sender="user",
    content="Hello, Moya!",
    metadata={"timestamp": "2025-04-01T12:00:00"}
)
repository.append_message("conversation_1", message)

# List all threads
thread_ids = repository.list_threads()
print(f"Available threads: {thread_ids}")
```

## Working with Threads and Messages

The memory repositories in Moya work with two primary data types:

1. **Thread**: Represents a conversation thread that contains messages
2. **Message**: Represents a single message within a thread

These classes are defined in:
- `moya/conversation/thread.py`
- `moya/conversation/message.py`

### Thread Usage:
```python
from moya.conversation.thread import Thread
from moya.conversation.message import Message

# Create a new thread
thread = Thread(thread_id="conversation_1", metadata={"user": "john_doe"})

# Add messages to the thread
thread.add_message(Message(thread_id="conversation_1", sender="user", content="Hello!"))
thread.add_message(Message(thread_id="conversation_1", sender="agent", content="Hi there!"))

# Access thread information
print(f"Thread ID: {thread.thread_id}")
print(f"Message count: {len(thread.messages)}")
```

## Implementation Notes

- When implementing a custom repository, ensure it properly handles thread creation, message appending, and thread retrieval.
- The `FileSystemRepository` stores each thread as a separate JSON file, with thread metadata at the top and messages as JSON lines.
- For high-volume applications, consider extending the repository pattern to use a database backend.
- Thread and message IDs should be unique to ensure proper identification and retrieval.