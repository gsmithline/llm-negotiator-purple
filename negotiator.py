"""
LLM-based Negotiator using Claude API.

Uses Claude to reason about negotiation strategy and make decisions.
"""
import json
import os
import anthropic
from typing import Any

# Initialize Anthropic client
client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

SYSTEM_PROMPT = """You are an expert negotiator in a bargaining game. You will receive game state information and must make strategic decisions.

IMPORTANT RULES:
1. Always respond with valid JSON only - no extra text
2. Be strategic but fair - aim for mutually beneficial outcomes when possible
3. Consider your BATNA (Best Alternative To Negotiated Agreement) carefully
4. Factor in the discount rate - delayed agreements lose value

For PROPOSE actions, respond with:
{"allocation_self": [list of integers], "allocation_other": [list of integers], "reason": "brief explanation"}

For ACCEPT_OR_REJECT actions, respond with:
{"accept": true/false, "reason": "brief explanation"}

The allocations must sum to the total quantities available."""


def parse_game_state(message_text: str) -> dict:
    """Extract game state from the message."""
    try:
        # Find JSON block in message
        if "```json" in message_text:
            start = message_text.find("```json") + 7
            end = message_text.find("```", start)
            json_str = message_text[start:end].strip()
        elif "{" in message_text:
            # Try to find JSON object
            start = message_text.find("{")
            # Find matching closing brace
            depth = 0
            end = start
            for i, c in enumerate(message_text[start:], start):
                if c == "{":
                    depth += 1
                elif c == "}":
                    depth -= 1
                    if depth == 0:
                        end = i + 1
                        break
            json_str = message_text[start:end]
        else:
            return {}

        return json.loads(json_str)
    except (json.JSONDecodeError, ValueError):
        return {}


def get_action_type(message_text: str) -> str:
    """Determine the action type from the message."""
    if "Action: PROPOSE" in message_text:
        return "PROPOSE"
    elif "Action: ACCEPT_OR_REJECT" in message_text:
        return "ACCEPT_OR_REJECT"
    return "UNKNOWN"


def call_claude(game_state: dict, action_type: str, message_text: str) -> dict:
    """Call Claude to get negotiation decision."""

    # Build context for Claude
    user_prompt = f"""Game State:
- Your valuations: {game_state.get('valuations_self', 'unknown')}
- Your BATNA: {game_state.get('batna_self', 'unknown')}
- Total quantities: {game_state.get('quantities', 'unknown')}
- Discount factor: {game_state.get('discount', 0.98)}
- Current round: {game_state.get('round', 1)}
- Role: {game_state.get('role', 'unknown')}

Action Required: {action_type}
"""

    if action_type == "ACCEPT_OR_REJECT":
        offer = game_state.get('current_offer', {})
        user_prompt += f"""
Current Offer to You: {offer.get('allocation_self', 'unknown')}
Their Allocation: {offer.get('allocation_other', 'unknown')}

Calculate the value of this offer based on your valuations and compare to your BATNA.
Should you accept this offer?
"""
    else:
        user_prompt += """
Make a strategic proposal. Consider:
1. What allocation gives you good value while being acceptable to the other party?
2. Remember they have different valuations than you.
3. A rejected offer means another round with discounting.

Propose an allocation.
"""

    try:
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=500,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_prompt}]
        )

        # Parse Claude's response
        response_text = response.content[0].text.strip()

        # Try to extract JSON from response
        if response_text.startswith("{"):
            return json.loads(response_text)
        elif "{" in response_text:
            start = response_text.find("{")
            end = response_text.rfind("}") + 1
            return json.loads(response_text[start:end])
        else:
            # Fallback
            return {"error": "Could not parse Claude response", "raw": response_text}

    except Exception as e:
        return {"error": str(e)}


def handle_negotiation_message(message_text: str) -> dict:
    """
    Process a negotiation message using Claude.

    Args:
        message_text: The raw message from the green agent

    Returns:
        Response dict with negotiation action
    """
    action_type = get_action_type(message_text)
    game_state = parse_game_state(message_text)

    if action_type == "UNKNOWN":
        return {"error": "Unknown action type", "action": "WALK"}

    # Call Claude for decision
    result = call_claude(game_state, action_type, message_text)

    if "error" in result:
        # Fallback behavior on error
        if action_type == "PROPOSE":
            # Default to even split
            quantities = game_state.get("quantities", [1, 1, 1])
            half = [q // 2 for q in quantities]
            other = [q - h for q, h in zip(quantities, half)]
            return {
                "allocation_self": half,
                "allocation_other": other,
                "reason": f"Fallback proposal due to error: {result.get('error', 'unknown')}"
            }
        else:
            # Default to reject on error
            return {
                "accept": False,
                "reason": f"Fallback rejection due to error: {result.get('error', 'unknown')}"
            }

    return result
