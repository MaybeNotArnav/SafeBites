import { useState, useRef, useEffect } from 'react';
import './SearchChat.css';

interface Message {
  id: string;
  type: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  results?: any[]; // For dish/menu results
}

function SearchChat() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  // Example queries for quick start
  const exampleQueries = [
    "Show me vegan pasta options",
    "Dishes without gluten under $15",
    "What are the calories in chocolate cake?",
    "List all desserts with nuts"
  ];

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  // Handle textarea auto-resize
  const handleInputChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setInputValue(e.target.value);
    
    // Auto-resize textarea
    e.target.style.height = 'auto';
    e.target.style.height = `${Math.min(e.target.scrollHeight, 120)}px`;
  };

  // Handle Enter key (Shift+Enter for new line)
  const handleKeyPress = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const handleSendMessage = async () => {
    if (!inputValue.trim() || isLoading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      type: 'user',
      content: inputValue.trim(),
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setIsLoading(true);

    // Reset textarea height
    if (inputRef.current) {
      inputRef.current.style.height = 'auto';
    }

    try {
      // TODO: Replace with actual API call to /restaurants/search
      // const response = await fetch('/api/restaurants/search', {
      //   method: 'POST',
      //   headers: { 'Content-Type': 'application/json' },
      //   body: JSON.stringify({
      //     query: inputValue.trim(),
      //     restaurant_id: "rest_1" // Should come from context/state
      //   })
      // });
      // const data = await response.json();

      // Simulate API delay (1.5-3 seconds for realism)
      const delay = Math.random() * 1500 + 1500;
      await new Promise(resolve => setTimeout(resolve, delay));

      // ============================================
      // MOCK RESPONSES FOR TESTING
      // Replace this entire section with real API call later
      // ============================================
      
      const query = userMessage.content.toLowerCase();
      let mockResponse: Message;

      // Scenario 1: Menu search query
      if (query.includes('vegan') || query.includes('pasta') || query.includes('pizza')) {
        mockResponse = {
          id: (Date.now() + 1).toString(),
          type: 'assistant',
          content: `I found 3 delicious options for "${userMessage.content}"! 🍝`,
          timestamp: new Date(),
          results: [
            {
              name: "Margherita Pizza",
              description: "Classic pizza with fresh mozzarella and basil",
              price: 12.99,
              allergens: ["dairy", "wheat_gluten"]
            },
            {
              name: "Penne Arrabbiata",
              description: "Spicy tomato sauce with garlic and red chili",
              price: 14.99,
              allergens: ["wheat_gluten"]
            },
            {
              name: "Vegan Buddha Bowl",
              description: "Quinoa, roasted vegetables, and tahini dressing",
              price: 11.99,
              allergens: []
            }
          ]
        };
      }
      // Scenario 2: Allergen/nutrition query
      else if (query.includes('calories') || query.includes('allergen') || query.includes('gluten')) {
        mockResponse = {
          id: (Date.now() + 1).toString(),
          type: 'assistant',
          content: `Here's what I found about "${userMessage.content}":\n\nThe Chocolate Lava Cake contains approximately 450 calories per serving. It contains the following allergens: dairy, eggs, and wheat gluten. Would you like to see alternative dessert options?`,
          timestamp: new Date()
        };
      }
      // Scenario 3: Price filter
      else if (query.includes('under') || query.includes('$') || query.includes('cheap')) {
        mockResponse = {
          id: (Date.now() + 1).toString(),
          type: 'assistant',
          content: `Great! I found 2 budget-friendly options under $15:`,
          timestamp: new Date(),
          results: [
            {
              name: "Caesar Salad",
              description: "Romaine lettuce with Caesar dressing and croutons",
              price: 8.99,
              allergens: ["dairy", "egg"]
            },
            {
              name: "Tomato Soup",
              description: "Creamy tomato soup with fresh basil",
              price: 6.50,
              allergens: ["dairy"]
            }
          ]
        };
      }
      // Scenario 4: No results
      else if (query.includes('xyz') || query.length < 3) {
        mockResponse = {
          id: (Date.now() + 1).toString(),
          type: 'assistant',
          content: `I couldn't find any dishes matching "${userMessage.content}". Could you try rephrasing your search or ask about specific dietary preferences?`,
          timestamp: new Date()
        };
      }
      // Default: Generic helpful response
      else {
        mockResponse = {
          id: (Date.now() + 1).toString(),
          type: 'assistant',
          content: `I found some results for "${userMessage.content}". Here are the top matches:`,
          timestamp: new Date(),
          results: [
            {
              name: "Chef's Special",
              description: "Today's special prepared by our head chef",
              price: 18.99,
              allergens: ["dairy", "shellfish"]
            }
          ]
        };
      }
      
      // ============================================
      // END MOCK RESPONSES
      // ============================================

      setMessages(prev => [...prev, mockResponse]);
    } catch (error) {
      console.error('Error sending message:', error);
      
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        type: 'assistant',
        content: 'Sorry, I encountered an error processing your request. Please try again.',
        timestamp: new Date()
      };
      
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleExampleQuery = (query: string) => {
    setInputValue(query);
    inputRef.current?.focus();
  };

  const formatTime = (date: Date) => {
    return date.toLocaleTimeString('en-US', { 
      hour: 'numeric', 
      minute: '2-digit',
      hour12: true 
    });
  };

  return (
    <div className="search-chat-container">
      {/* Header with Instructions */}
      <div className="chat-header">
        <h1 className="chat-title">Search Chat</h1>
        <div className="chat-instructions">
          <h3>💬 How to use:</h3>
          <ul>
            <li>Ask questions in natural language, like <code>"Show me vegan options"</code></li>
            <li>Filter by allergens: <code>"Dishes without nuts"</code></li>
            <li>Set price limits: <code>"Under $20"</code></li>
            <li>Ask about nutrition: <code>"How many calories in this dish?"</code></li>
            <li>Combine filters: <code>"Gluten-free pasta under $15"</code></li>
            <li>Press <strong>Enter</strong> to send, <strong>Shift+Enter</strong> for new line</li>
          </ul>
        </div>
      </div>

      {/* Messages Area */}
      <div className="chat-messages-area">
        {messages.length === 0 ? (
          <div className="empty-chat-state">
            <img src="/icons/hugeicon_ai_search.png" alt="Chat" className="empty-chat-icon" />
            <h3>Start a Conversation</h3>
            <p>Ask me anything about the menu, allergens, nutrition, or dietary preferences!</p>
            
            {/* Example Queries */}
            <div className="example-queries">
              {exampleQueries.map((query, index) => (
                <button
                  key={index}
                  className="example-query-btn"
                  onClick={() => handleExampleQuery(query)}
                >
                  {query}
                </button>
              ))}
            </div>
          </div>
        ) : (
          <>
            {messages.map((message) => (
              <div key={message.id} className={`message-wrapper ${message.type}`}>
                <div className={`message-bubble ${message.type}`}>
                  <p className="message-content">{message.content}</p>
                  
                  {/* Render results if present */}
                  {message.results && message.results.length > 0 && (
                    <div>
                      {message.results.map((result, idx) => (
                        <div key={idx} className="result-card">
                          <h4>{result.name}</h4>
                          <p>{result.description}</p>
                          <p className="price">${result.price.toFixed(2)}</p>
                          {result.allergens && result.allergens.length > 0 && (
                            <p>
                              <strong>Allergens:</strong> {result.allergens.join(', ')}
                            </p>
                          )}
                        </div>
                      ))}
                    </div>
                  )}
                  
                  <div className="message-timestamp">{formatTime(message.timestamp)}</div>
                </div>
              </div>
            ))}

            {/* Loading Indicator */}
            {isLoading && (
              <div className="loading-wrapper">
                <div className="loading-bubble">
                  <div className="loading-dots">
                    <div className="loading-dot"></div>
                    <div className="loading-dot"></div>
                    <div className="loading-dot"></div>
                  </div>
                  <span className="loading-text">Thinking...</span>
                </div>
              </div>
            )}
            
            {/* Auto-scroll anchor */}
            <div ref={messagesEndRef} />
          </>
        )}
      </div>

      {/* Input Bar (Fixed at Bottom) */}
      <div className="chat-input-container">
        <div className="chat-input-wrapper">
          <textarea
            ref={inputRef}
            className="chat-input"
            placeholder="Ask about dishes, allergens, nutrition, or dietary preferences..."
            value={inputValue}
            onChange={handleInputChange}
            onKeyPress={handleKeyPress}
            rows={1}
            disabled={isLoading}
          />
          <button
            className="chat-send-btn"
            onClick={handleSendMessage}
            disabled={!inputValue.trim() || isLoading}
          >
            {isLoading ? 'Sending...' : 'Send'}
            {!isLoading && (
              <img src="/icons/icons8-search-24.png" alt="Send" className="send-icon" />
            )}
          </button>
        </div>
      </div>
    </div>
  );
}

export default SearchChat;