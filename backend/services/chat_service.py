"""
Chat Service - Conversational AI with Gemini

This service handles all user conversations using Google Gemini.
It can:
1. Respond to greetings and general questions
2. Explain the platform capabilities
3. Detect when users want trend research and trigger the research agents
4. Maintain conversation context (last 10 messages)
"""

import json
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

# Try to import LLM connector
try:
    from connectors import get_connector, ConnectorStatus
    LLM_AVAILABLE = True
except ImportError:
    LLM_AVAILABLE = False
    logger.warning("LLM connector not available, chat will use fallback responses")


class ChatAction(str, Enum):
    """Actions the chat service can return"""
    RESPOND = "respond"  # Normal conversational response
    RESEARCH = "research"  # Trigger research agents
    CLARIFY = "clarify"  # Ask for clarification before research


@dataclass
class ChatResponse:
    """Response from chat service"""
    action: ChatAction
    message: str
    research_question: Optional[str] = None
    search_query: Optional[str] = None
    confidence: float = 1.0


# System prompt that defines the AI's behavior
SYSTEM_PROMPT = """You are an AI Research Assistant for a Marketing Trend Research Platform.

## Your Capabilities
You help marketing teams research trends across multiple data sources using 6 specialized AI agents:
1. **Twitter/X Agent** - Analyzes social media discussions and sentiment
2. **Reddit Agent** - Gathers community insights and discussions  
3. **TikTok Agent** - Tracks viral content and creator trends
4. **Google Trends Agent** - Monitors search interest over time
5. **Web Search Agent** - Collects news articles and web sources
6. **Analyst Agent** - Synthesizes all data into actionable insights

## Your Behavior
1. **Greetings**: Be friendly and briefly explain what you can help with
2. **Questions about the platform**: Explain capabilities clearly
3. **Research requests**: When users want trend research, you should trigger the research agents
4. **Unclear requests**: Ask for clarification if the research topic is vague

## Response Format
You MUST respond with valid JSON in this exact format:
{
    "action": "respond" | "research" | "clarify",
    "message": "Your conversational response to the user",
    "research_question": "The full research question (only if action is 'research')",
    "search_query": "2-5 keyword search terms (only if action is 'research')"
}

## Examples

User: "Hi!"
Response: {"action": "respond", "message": "Hello! I'm your AI Research Assistant. I can help you research marketing trends across Twitter, Reddit, TikTok, Google Trends, and more. What topic would you like to explore today?"}

User: "What can you do?"
Response: {"action": "respond", "message": "I specialize in marketing trend research! I coordinate 6 AI agents that gather data from:\\n\\n• **Twitter/X** - Social sentiment & discussions\\n• **Reddit** - Community insights\\n• **TikTok** - Viral content trends\\n• **Google Trends** - Search interest data\\n• **Web Search** - News & articles\\n• **Analyst** - Synthesizes everything into a report\\n\\nJust ask me about any trend, market, or topic you'd like to research!"}

User: "Why do Gen Z in Nigeria prefer Facebook over Google?"
Response: {"action": "research", "message": "Great question! I'll start researching Gen Z social media preferences in Nigeria. My agents will gather data from multiple sources - this usually takes about 20-30 seconds.", "research_question": "Why does Gen Z in Nigeria appear to use Facebook for community and content discovery, while using Google primarily for functional, task-based searches?", "search_query": "Gen Z Nigeria Facebook Google social media"}

User: "Tell me about trends"
Response: {"action": "clarify", "message": "I'd love to help you research trends! Could you be more specific about what you're interested in?\\n\\n• A specific industry? (e.g., fintech, fashion, food)\\n• A demographic? (e.g., Gen Z, millennials)\\n• A platform? (e.g., TikTok trends, Twitter discussions)\\n• A region? (e.g., Nigeria, Southeast Asia)\\n\\nThe more specific, the better insights I can provide!"}

User: "What's trending in AI marketing?"
Response: {"action": "research", "message": "I'll research AI marketing trends for you! Let me gather insights from across the web and social media.", "research_question": "What are the current trends in AI marketing and how are brands leveraging AI for marketing campaigns?", "search_query": "AI marketing trends 2024 brands"}

## Important Rules
1. ALWAYS respond with valid JSON - no markdown code blocks, just raw JSON
2. For research requests, be proactive - if the intent is clear, start researching
3. Keep messages concise but helpful
4. If the user asks something completely unrelated to research (like math problems), politely redirect to your capabilities
"""


class ChatService:
    """
    Service for handling conversational AI with Gemini.
    
    Features:
    - Maintains conversation history (last 10 messages)
    - Detects research intent
    - Returns structured responses with actions
    """
    
    MAX_HISTORY = 10  # Keep last 10 messages for context
    
    def __init__(self):
        """Initialize chat service with LLM connector"""
        self.llm_connector = None
        if LLM_AVAILABLE:
            try:
                self.llm_connector = get_connector("llm")
                logger.info("Chat service initialized with LLM connector")
            except Exception as e:
                logger.error(f"Failed to initialize LLM connector: {e}")
        
        # In-memory conversation storage (keyed by conversation_id)
        self.conversations: Dict[str, List[Dict[str, str]]] = {}
    
    def _get_history(self, conversation_id: str) -> List[Dict[str, str]]:
        """Get conversation history for a session"""
        return self.conversations.get(conversation_id, [])
    
    def _add_to_history(self, conversation_id: str, role: str, content: str):
        """Add a message to conversation history"""
        if conversation_id not in self.conversations:
            self.conversations[conversation_id] = []
        
        self.conversations[conversation_id].append({
            "role": role,
            "content": content
        })
        
        # Trim to max history
        if len(self.conversations[conversation_id]) > self.MAX_HISTORY:
            self.conversations[conversation_id] = self.conversations[conversation_id][-self.MAX_HISTORY:]
    
    def _build_prompt(self, conversation_id: str, user_message: str) -> str:
        """Build the full prompt with system context and history"""
        history = self._get_history(conversation_id)
        
        # Build conversation history string
        history_str = ""
        if history:
            history_str = "\n\n## Recent Conversation\n"
            for msg in history:
                role = "User" if msg["role"] == "user" else "Assistant"
                history_str += f"{role}: {msg['content']}\n"
        
        # Build full prompt
        prompt = f"""{SYSTEM_PROMPT}
{history_str}
## Current Message
User: {user_message}

Remember: Respond with valid JSON only, no markdown formatting."""
        
        return prompt
    
    def _parse_response(self, raw_response: str) -> ChatResponse:
        """Parse LLM response into ChatResponse"""
        try:
            # Try to extract JSON from response
            response_text = raw_response.strip()
            
            # Handle markdown code blocks if present
            if response_text.startswith("```"):
                lines = response_text.split("\n")
                json_lines = []
                in_json = False
                for line in lines:
                    if line.startswith("```") and not in_json:
                        in_json = True
                        continue
                    elif line.startswith("```") and in_json:
                        break
                    elif in_json:
                        json_lines.append(line)
                response_text = "\n".join(json_lines)
            
            # Parse JSON
            data = json.loads(response_text)
            
            action = ChatAction(data.get("action", "respond"))
            message = data.get("message", "I'm here to help with trend research!")
            
            return ChatResponse(
                action=action,
                message=message,
                research_question=data.get("research_question"),
                search_query=data.get("search_query"),
                confidence=1.0
            )
            
        except (json.JSONDecodeError, ValueError) as e:
            logger.warning(f"Failed to parse LLM response as JSON: {e}")
            logger.debug(f"Raw response: {raw_response}")
            
            # Fallback: treat the whole response as a message
            return ChatResponse(
                action=ChatAction.RESPOND,
                message=raw_response if raw_response else "I'm here to help with trend research! What would you like to explore?",
                confidence=0.5
            )
    
    async def chat(self, conversation_id: str, message: str) -> ChatResponse:
        """
        Process a chat message and return a response.
        
        Args:
            conversation_id: Unique ID for the conversation
            message: User's message
            
        Returns:
            ChatResponse with action and message
        """
        # Add user message to history
        self._add_to_history(conversation_id, "user", message)
        
        # If no LLM available, use fallback
        if not self.llm_connector:
            return self._fallback_response(message)
        
        try:
            # Build prompt with history
            prompt = self._build_prompt(conversation_id, message)
            
            # Call LLM
            result = await self.llm_connector.generate(prompt)
            
            if result.status == ConnectorStatus.SUCCESS and result.data:
                # Extract text from response
                raw_text = ""
                if isinstance(result.data, list) and len(result.data) > 0:
                    item = result.data[0]
                    raw_text = item.get("text") or item.get("analysis") or str(item)
                elif isinstance(result.data, str):
                    raw_text = result.data
                
                # Parse into ChatResponse
                response = self._parse_response(raw_text)
                
                # Add assistant response to history
                self._add_to_history(conversation_id, "assistant", response.message)
                
                return response
            else:
                logger.warning(f"LLM returned non-success status: {result.status}")
                return self._fallback_response(message)
                
        except Exception as e:
            logger.error(f"Chat error: {e}", exc_info=True)
            return self._fallback_response(message)
    
    def _fallback_response(self, message: str) -> ChatResponse:
        """Fallback response when LLM is unavailable"""
        message_lower = message.lower()
        
        # Simple keyword matching for fallback
        if any(word in message_lower for word in ["hi", "hello", "hey", "morning", "afternoon"]):
            return ChatResponse(
                action=ChatAction.RESPOND,
                message="Hello! I'm your AI Research Assistant. I can help you research marketing trends across Twitter, Reddit, TikTok, and more. What topic would you like to explore?",
                confidence=0.8
            )
        
        if any(word in message_lower for word in ["help", "what can you", "capabilities", "how do"]):
            return ChatResponse(
                action=ChatAction.RESPOND,
                message="I specialize in marketing trend research! I coordinate 6 AI agents that gather data from Twitter, Reddit, TikTok, Google Trends, and web sources. Just ask me about any trend or topic you'd like to research!",
                confidence=0.8
            )
        
        if any(word in message_lower for word in ["trend", "research", "analyze", "why do", "how are", "what's happening"]):
            return ChatResponse(
                action=ChatAction.CLARIFY,
                message="I'd be happy to research that! Could you tell me more about what specific aspect you're interested in? For example, a particular demographic, region, or platform?",
                confidence=0.6
            )
        
        # Default
        return ChatResponse(
            action=ChatAction.RESPOND,
            message="I'm here to help with trend research! You can ask me to research any marketing trend, or ask about my capabilities. What would you like to explore?",
            confidence=0.5
        )
    
    def clear_history(self, conversation_id: str):
        """Clear conversation history for a session"""
        if conversation_id in self.conversations:
            del self.conversations[conversation_id]


# Singleton instance
_chat_service: Optional[ChatService] = None


def get_chat_service() -> ChatService:
    """Get or create chat service singleton"""
    global _chat_service
    if _chat_service is None:
        _chat_service = ChatService()
    return _chat_service
