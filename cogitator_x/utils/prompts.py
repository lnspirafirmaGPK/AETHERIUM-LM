from typing import List

class MixedCoTPrompter:
    """
    Utility to implement the 'Language-Mixed Chain-of-Thought' (English Pivot) strategy.
    """

    SYSTEM_PROMPT = """You are Cogitator-X, a reasoning AI.
To solve complex problems in non-English languages, follow these rules:
1. Use <think> tags for your internal monologue.
2. Inside <think>, use English as a logical pivot for mathematical, logical, and technical steps to maintain high precision.
3. Switch back to the user's language (e.g., Thai) when handling cultural context or names.
4. Your final answer must be entirely in the user's language unless requested otherwise.
5. If you detect a mistake in your logic, backtrack and correct it within the <think> tag."""

    @staticmethod
    def format_reasoning_prompt(query: str, current_path: List[str]) -> str:
        """
        Formats the prompt for the generator to continue the reasoning trace.
        """
        path_str = "\n".join([f"Step {i+1}: {step}" for i, step in enumerate(current_path)])

        prompt = f"{MixedCoTPrompter.SYSTEM_PROMPT}\n\nUser Question: {query}\n\n"
        if current_path:
            prompt += f"Current reasoning path:\n{path_str}\n\nWhat is the next logical step?"
        else:
            prompt += "Begin your reasoning process using the Mixed-CoT strategy."

        return prompt

    @staticmethod
    def extract_thought(model_output: str) -> str:
        """
        Extracts content from <think> tags if present.
        """
        import re
        match = re.search(r'<think>(.*?)</think>', model_output, re.DOTALL)
        if match:
            return match.group(1).strip()
        return model_output.strip()
