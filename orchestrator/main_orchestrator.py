from orchestrator.event_router import route_event
from orchestrator.chain_loader import load_chain, resolve_engine_for_operator
from orchestrator.state_manager import StateManager
from orchestrator.escalation_handler import handle_escalation
from orchestrator.output_finalizer import finalize_output

def orchestrate(event):
    state = StateManager.initialize(event)

    # triggers.yaml maps an event to the operator most responsible for it;
    # that operator's own `engine` attribute tells us which chain to run.
    operator_name = route_event(event)
    engine_name = resolve_engine_for_operator(operator_name)
    chain = load_chain(f"{engine_name}_chain")

    for operator in chain:
        try:
            state = operator.execute(state)
        except Exception as e:
            state = handle_escalation(e, state)
            break

    return finalize_output(state)