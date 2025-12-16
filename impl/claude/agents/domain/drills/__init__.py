"""
Drills: Enterprise Crisis Simulation Drills.

Two canonical drill templates:

1. ServiceOutageDrill - Critical service outage response
   - Citizens: on_call_engineer, incident_commander, executive, customer_success
   - No compliance timers
   - Injects: media_story, executive_call, social_media

2. DataBreachDrill - Data breach response with compliance
   - Citizens: security_analyst, legal_counsel, pr_director, ciso
   - Timer: GDPR 72h notification deadline
   - Injects: media_story, regulator_inquiry, executive_call

Usage:
    from agents.domain.drills import create_service_outage_drill, create_data_breach_drill

    # Create and start a service outage drill
    drill = create_service_outage_drill()
    output = drill.start()

    # Create a data breach drill with GDPR timer
    breach_drill = create_data_breach_drill()
    output = breach_drill.start()
    # GDPR 72h timer is now running!

See: plans/core-apps/domain-simulation.md
"""

from .archetypes import (
    CRISIS_ARCHETYPE_SPECS,
    CrisisArchetype,
    CrisisArchetypeSpec,
    create_crisis_citizen,
    create_data_breach_team,
    create_service_outage_team,
    get_archetype_emoji,
    get_archetype_responsibilities,
)
from .injects import (
    PREDEFINED_INJECTS,
    InjectSequence,
    InjectSpec,
    InjectState,
    InjectStatus,
    InjectTrigger,
    InjectType,
    create_data_breach_injects,
    create_inject,
    create_service_outage_injects,
)
from .operad import (
    CLOSE_METABOLICS,
    COMMUNICATE_METABOLICS,
    CONTAIN_METABOLICS,
    CRISIS_OPERAD,
    DETECT_METABOLICS,
    ESCALATE_METABOLICS,
    INVESTIGATE_METABOLICS,
    PRECONDITION_CHECKER,
    RECOVER_METABOLICS,
    RESOLVE_METABOLICS,
    CrisisAuditEvent,
    CrisisAuditStore,
    CrisisPreconditionChecker,
    OperationMetabolics,
    PreconditionResult,
    emit_crisis_audit,
    get_audit_store,
)
from .polynomial import (
    CRISIS_POLYNOMIAL,
    CloseInput,
    CommunicateInput,
    ContainInput,
    CrisisInput,
    CrisisOutput,
    CrisisPhase,
    DetectInput,
    EscalateInput,
    InvestigateInput,
    RecoverInput,
    ResolveInput,
)
from .templates import (
    DATA_BREACH_SPEC,
    DATA_BREACH_SUCCESS_CRITERIA,
    DRILL_TEMPLATES,
    SERVICE_OUTAGE_SPEC,
    SERVICE_OUTAGE_SUCCESS_CRITERIA,
    DrillDifficulty,
    DrillError,
    DrillInstance,
    DrillPreconditionError,
    DrillStateError,
    DrillStatus,
    DrillTemplateSpec,
    DrillType,
    DrillValidationError,
    SuccessCriterion,
    SuccessEvaluation,
    create_data_breach_drill,
    create_drill,
    create_service_outage_drill,
    get_drill_template,
    list_drill_types,
)
from .timers import (
    GDPR_72H_CONFIG,
    HIPAA_60DAY_CONFIG,
    SEC_4DAY_CONFIG,
    TIMER_CONFIGS,
    TimerConfig,
    TimerState,
    TimerStatus,
    TimerType,
    create_gdpr_timer,
    create_hipaa_timer,
    create_sec_timer,
    create_timer,
    format_countdown,
    get_status_color,
)

__all__ = [
    # Polynomial
    "CrisisPhase",
    "CrisisInput",
    "CrisisOutput",
    "CRISIS_POLYNOMIAL",
    "DetectInput",
    "EscalateInput",
    "ContainInput",
    "CommunicateInput",
    "InvestigateInput",
    "ResolveInput",
    "RecoverInput",
    "CloseInput",
    # Archetypes
    "CrisisArchetype",
    "CrisisArchetypeSpec",
    "CRISIS_ARCHETYPE_SPECS",
    "create_crisis_citizen",
    "create_service_outage_team",
    "create_data_breach_team",
    "get_archetype_emoji",
    "get_archetype_responsibilities",
    # Timers
    "TimerType",
    "TimerStatus",
    "TimerConfig",
    "TimerState",
    "GDPR_72H_CONFIG",
    "SEC_4DAY_CONFIG",
    "HIPAA_60DAY_CONFIG",
    "TIMER_CONFIGS",
    "create_timer",
    "create_gdpr_timer",
    "create_sec_timer",
    "create_hipaa_timer",
    "format_countdown",
    "get_status_color",
    # Injects
    "InjectType",
    "InjectTrigger",
    "InjectStatus",
    "InjectSpec",
    "InjectState",
    "InjectSequence",
    "PREDEFINED_INJECTS",
    "create_inject",
    "create_service_outage_injects",
    "create_data_breach_injects",
    # Templates - Exceptions
    "DrillError",
    "DrillStateError",
    "DrillValidationError",
    "DrillPreconditionError",
    # Templates - Enums
    "DrillType",
    "DrillDifficulty",
    "DrillStatus",
    "SuccessCriterion",
    "SuccessEvaluation",
    "DrillTemplateSpec",
    "DrillInstance",
    "SERVICE_OUTAGE_SPEC",
    "DATA_BREACH_SPEC",
    "SERVICE_OUTAGE_SUCCESS_CRITERIA",
    "DATA_BREACH_SUCCESS_CRITERIA",
    "DRILL_TEMPLATES",
    "create_service_outage_drill",
    "create_data_breach_drill",
    "create_drill",
    "get_drill_template",
    "list_drill_types",
    # Operad
    "CRISIS_OPERAD",
    "OperationMetabolics",
    "DETECT_METABOLICS",
    "ESCALATE_METABOLICS",
    "CONTAIN_METABOLICS",
    "COMMUNICATE_METABOLICS",
    "INVESTIGATE_METABOLICS",
    "RESOLVE_METABOLICS",
    "RECOVER_METABOLICS",
    "CLOSE_METABOLICS",
    "CrisisAuditEvent",
    "CrisisAuditStore",
    "get_audit_store",
    "emit_crisis_audit",
    "PreconditionResult",
    "CrisisPreconditionChecker",
    "PRECONDITION_CHECKER",
]
