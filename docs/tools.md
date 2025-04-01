# Tools in Moya

The Tools module in Moya provides utility functions and components that enhance the functionality of agents and orchestrators. These tools are designed to simplify common tasks and extend the capabilities of the framework.

## Overview

Tools in Moya serve the following purposes:

- **Task Automation**: Automate repetitive tasks.
- **Data Processing**: Process and transform data for agents and orchestrators.
- **Integration**: Provide integrations with external services and APIs.

## Key Tools

### 1. TextProcessor

**File:** `moya/tools/text_processor.py`

The `TextProcessor` tool provides utilities for processing and transforming text. It is commonly used for tasks such as text cleaning, tokenization, and summarization.

#### Key Features:
- Text cleaning and normalization.
- Tokenization and word frequency analysis.
- Text summarization.

#### Example Usage:
```python
from moya.tools.text_processor import TextProcessor

processor = TextProcessor()
cleaned_text = processor.clean_text("This is a sample text.")
print(cleaned_text)
```

### 2. APIClient

**File:** `moya/tools/api_client.py`

The `APIClient` tool provides a simple interface for making HTTP requests to external APIs. It supports GET, POST, PUT, and DELETE methods.

#### Key Features:
- Simplified HTTP request handling.
- Support for headers and query parameters.
- JSON response parsing.

#### Example Usage:
```python
from moya.tools.api_client import APIClient

client = APIClient()
response = client.get("https://api.example.com/data")
print(response)
```

### 3. DataTransformer

**File:** `moya/tools/data_transformer.py`

The `DataTransformer` tool provides utilities for transforming and formatting data. It is useful for preparing data for agents and orchestrators.

#### Key Features:
- Data normalization and scaling.
- JSON and CSV parsing.
- Custom data transformation pipelines.

#### Example Usage:
```python
from moya.tools.data_transformer import DataTransformer

transformer = DataTransformer()
normalized_data = transformer.normalize([1, 2, 3, 4, 5])
print(normalized_data)
```

## Custom Tools

You can create custom tools by defining new classes or functions in the `tools` module. This allows you to implement utilities tailored to your specific use case.

#### Example:
```python
class CustomTool:
    def perform_task(self, data):
        # Custom logic here
        return f"Processed: {data}"

tool = CustomTool()
print(tool.perform_task("Sample data"))
```

## Additional Notes

- Use tools to simplify and modularize your code.
- Ensure that tools are well-documented and tested.
- Refer to the individual tool files for more details on configuration and usage.