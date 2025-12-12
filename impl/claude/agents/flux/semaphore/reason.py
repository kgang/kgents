"""
SemaphoreReason: Why the agent yielded to human.

The Rodizio Pattern taxonomy of semaphore types.
Each reason maps to a specific human-agent interaction pattern.
"""

from enum import Enum


class SemaphoreReason(Enum):
    """
    Why the agent yielded to human.

    The Rodizio Pattern:
    - Agent returns SemaphoreToken with reason
    - Human understands WHY their input is needed
    - UI can adapt display based on reason

    Categories align with the Semaphore Types taxonomy:
    - APPROVAL_NEEDED → 🛡️ Approval
    - CONTEXT_REQUIRED → 📖 Context
    - SENSITIVE_ACTION → 🔒 Sensitive
    - AMBIGUOUS_CHOICE → 🤔 Ambiguity
    - RESOURCE_DECISION → 💰 Resource
    - ERROR_RECOVERY → 🔧 Recovery
    """

    APPROVAL_NEEDED = "approval_needed"
    """Sensitive action requiring explicit approval. Example: 'Delete 47 user records?'"""

    CONTEXT_REQUIRED = "context_required"
    """Agent needs information only human has. Example: 'Which database environment?'"""

    SENSITIVE_ACTION = "sensitive_action"
    """Privacy/security implications require human review. Example: 'Access PII data?'"""

    AMBIGUOUS_CHOICE = "ambiguous_choice"
    """Multiple valid interpretations exist. Example: '"Bank" means financial or river?'"""

    RESOURCE_DECISION = "resource_decision"
    """Resource allocation decision needed. Example: 'Scaling requires 4 GPUs ($2,400/day)'"""

    ERROR_RECOVERY = "error_recovery"
    """Error occurred, human guidance needed. Example: 'API rate limited. Wait or switch?'"""
