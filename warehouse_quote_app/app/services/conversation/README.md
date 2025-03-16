# Conversation Handling Module

## Overview

The Conversation Handling Module provides a comprehensive system for managing user conversations within the AU Logistics Warehouse Quote application. This module supports natural language interactions, state tracking, and integration with quote generation services. Note that multilingual support has been removed from this module.

## Date: February 26, 2025

## Components

### 1. ConversationState (`conversation_state.py`)

The ConversationState class manages multiple conversations and their states:

- **Conversation Tracking**: Maintains a registry of active conversations indexed by conversation ID
- **Session Management**: Creates and manages new conversation contexts
- **Database Integration**: Ensures all conversations have access to necessary database sessions

### 2. ConversationContext (`conversation_state.py`)

The ConversationContext class handles the state and flow of individual conversations:

- **State Machine**: Implements a state machine to guide conversation flow (initial → storage_type → quantity → duration)
- **Information Gathering**: Collects and stores user inputs progressively through the conversation
- **Service Integration**: Connects with StorageService and QuoteService to generate quotes based on gathered information

### 3. ConversationResponse (`conversation_state.py`)

Data structure for responses in the conversation flow:

- **Messages**: List of text messages to display to the user
- **Questions**: List of questions to ask the user
- **Suggested Responses**: Optional list of suggested responses for the user to choose from

## Usage

### Initializing Conversation Manager

```python
from sqlalchemy.orm import Session
from warehouse_quote_app.app.services.conversation import ConversationState

# Create conversation state manager with database session
db = Session()  # Get your session from your application context
conversation_manager = ConversationState(db)
```

### Starting a New Conversation

```python
# Create a new conversation context
conversation = conversation_manager.new_conversation()
conversation_id = conversation.conversation_id  # Store this to retrieve the conversation later
```

### Handling User Input

```python
# Process user input
user_message = "I need to store household items for about 3 months"
response = conversation.handle_input(user_message)

# Display response to user
for message in response.messages:
    print(message)
    
# Show questions to user
for question in response.questions:
    print(question)
```

### Generating Quotes

The conversation flow will automatically generate quotes when sufficient information is gathered. The flow follows these states:

1. **Initial State**: Welcome message, ask about storage type
2. **Storage Type**: Ask about quantity based on storage type selection
3. **Quantity**: Ask about duration based on quantity selection
4. **Duration**: Generate a quote based on all gathered information

## Testing

The conversation handling module has been thoroughly tested to ensure proper functionality. The test suite includes:

1. **Progressive Information Gathering** - Tests the step-by-step flow of gathering quote information:
   - Initial vague request → Storage type selection → Quantity selection → Duration selection
   - Verifies proper state transitions and information collection

2. **Conversation State Management** - Tests the management of multiple conversations:
   - Creating and tracking multiple conversation instances
   - Proper state progression through the quote flow
   - Conversation retrieval and cleanup functionality

3. **Error Handling** - Tests system response to invalid inputs:
   - Invalid quantity inputs (system stays in current state and re-prompts)
   - Invalid storage type inputs (system attempts to proceed with best interpretation)

Test results confirm that the conversation handler correctly:
- Manages state transitions
- Collects and stores user information
- Provides appropriate responses and questions
- Handles basic error conditions

### Conversation Flow

The conversation follows this state progression:
1. **initial** → User expresses interest in storage
2. **storage_type** → System asks for storage type (household, business, equipment)
3. **quantity** → System asks for quantity (small, medium, large)
4. **duration** → System asks for duration (short, medium, long term)

Each state transition builds the quote requirements data structure which is ultimately used to generate the final quote.

## Dependencies

- **SQLAlchemy**: For database interactions
- **Pydantic**: For data validation with BaseModel
- **StorageService**: For calculating storage costs
- **QuoteService**: For generating comprehensive quotes

## Integration Notes

1. The conversation module has been fully integrated with the existing services architecture
2. Updated imports in the `services/__init__.py` file to expose conversation handling classes
3. All dependencies properly managed with a database session passed through constructors

## Future Enhancements

- Add support for more complex conversation paths
- Implement NLP for better understanding of user intents
- Add sentiment analysis for improved customer experience
- Support for handling multiple quote types in a single conversation
