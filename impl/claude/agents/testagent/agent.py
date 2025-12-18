"""
Testagent: A Lambda agent.

Type: Lambda[str, str]
Capabilities: Observable only (stateless function)
"""

from __future__ import annotations

from agents.a import Lambda


class TestagentAgent(Lambda[str, str]):
    """
    A Lambda agent.

    Input: str
    Output: str
    """

    @property
    def name(self) -> str:
        return "testagent"

    async def invoke(self, input: str) -> str:
        """Process input and return output.

        TODO: Implement your logic here.
        """
        raise NotImplementedError("Implement me!")
