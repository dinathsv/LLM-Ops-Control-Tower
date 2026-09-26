from core.schema import LLMCallEvent

def test_llm_call_event_defaults():
    event = LLMCallEvent(
        project_id="prj_test",
        application_name="test_bot",
        model_version="v1.0",
        prompt="Hello",
        response="Hi there!",
        latency_ms=150
    )
    assert event.project_id == "prj_test"
    assert event.input_tokens == 0
    assert event.output_tokens == 0
    assert event.cost_usd == 0.0
    assert event.metadata == {}
    assert event.trace_id is not None
