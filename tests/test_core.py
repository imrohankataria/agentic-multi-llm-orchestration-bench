"""
Simple tests to verify core functionality
Run with: python -m pytest tests/ -v
Or simply: python tests/test_core.py
"""
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from cost_tracker.core import CostTracker, CostEvent


def test_cost_tracker_initialization():
    """Test that cost tracker initializes correctly"""
    tracker = CostTracker()
    assert tracker.events == []
    assert tracker.agent_summaries == {}
    assert tracker.workflow_start_time is None
    print("✓ Cost tracker initialization test passed")


def test_track_llm_call():
    """Test tracking an LLM call"""
    tracker = CostTracker()
    tracker.start_workflow()
    
    tracker.track_llm_call(
        agent_name="TestAgent",
        model="gpt-4o-mini",
        input_tokens=100,
        output_tokens=50
    )
    
    assert len(tracker.events) == 1
    assert tracker.events[0].agent_name == "TestAgent"
    assert tracker.events[0].input_tokens == 100
    assert tracker.events[0].output_tokens == 50
    assert tracker.events[0].cost > 0  # Should calculate cost
    print("✓ LLM call tracking test passed")


def test_track_tool_call():
    """Test tracking a tool call"""
    tracker = CostTracker()
    tracker.start_workflow()
    
    tracker.track_tool_call(
        agent_name="TestAgent",
        tool_name="test_tool",
        duration_ms=500
    )
    
    assert len(tracker.events) == 1
    assert tracker.events[0].event_type == "tool_call"
    assert tracker.events[0].metadata["tool_name"] == "test_tool"
    print("✓ Tool call tracking test passed")


def test_track_agent_step():
    """Test tracking an agent step"""
    tracker = CostTracker()
    tracker.start_workflow()
    
    tracker.track_agent_step(
        agent_name="TestAgent",
        step_name="test_step",
        duration_ms=1000
    )
    
    assert len(tracker.events) == 1
    assert tracker.events[0].event_type == "agent_step"
    assert tracker.events[0].metadata["step_name"] == "test_step"
    print("✓ Agent step tracking test passed")


def test_agent_summaries():
    """Test that agent summaries are created correctly"""
    tracker = CostTracker()
    tracker.start_workflow()
    
    tracker.track_llm_call("Agent1", "gpt-4o-mini", 100, 50)
    tracker.track_llm_call("Agent1", "gpt-4o-mini", 150, 75)
    tracker.track_llm_call("Agent2", "gpt-4o-mini", 200, 100)
    
    assert "Agent1" in tracker.agent_summaries
    assert "Agent2" in tracker.agent_summaries
    assert tracker.agent_summaries["Agent1"].num_llm_calls == 2
    assert tracker.agent_summaries["Agent2"].num_llm_calls == 1
    print("✓ Agent summaries test passed")


def test_cost_calculation():
    """Test that costs are calculated correctly"""
    tracker = CostTracker()
    tracker.start_workflow()
    
    # gpt-4o-mini pricing: $0.00015 per 1K input, $0.0006 per 1K output
    tracker.track_llm_call(
        agent_name="TestAgent",
        model="gpt-4o-mini",
        input_tokens=1000,  # Should cost $0.00015
        output_tokens=1000  # Should cost $0.0006
    )
    
    expected_cost = 0.00015 + 0.0006  # $0.00075
    actual_cost = tracker.get_total_cost()
    
    assert abs(actual_cost - expected_cost) < 0.0001  # Allow small floating point difference
    print("✓ Cost calculation test passed")


def test_spike_detection():
    """Test that cost spikes are detected correctly"""
    tracker = CostTracker()
    tracker.start_workflow()
    
    # Agent1: Low cost
    tracker.track_llm_call("Agent1", "gpt-4o-mini", 100, 50)
    
    # Agent2: Low cost
    tracker.track_llm_call("Agent2", "gpt-4o-mini", 100, 50)
    
    # Agent3: Very high cost (should be detected as spike)
    tracker.track_llm_call("Agent3", "gpt-4o-mini", 5000, 5000)
    
    spikes = tracker.identify_cost_spikes(threshold=2.0)
    assert "Agent3" in spikes
    assert "Agent1" not in spikes
    assert "Agent2" not in spikes
    print("✓ Spike detection test passed")


def test_summary_generation():
    """Test that summary is generated correctly"""
    tracker = CostTracker()
    tracker.start_workflow()
    
    tracker.track_llm_call("Agent1", "gpt-4o-mini", 100, 50)
    tracker.track_tool_call("Agent1", "test_tool")
    tracker.track_agent_step("Agent2", "test_step")
    
    tracker.end_workflow()
    summary = tracker.get_summary()
    
    assert "total_cost" in summary
    assert "agent_costs" in summary
    assert "cost_spikes" in summary
    assert len(summary["agent_costs"]) == 2
    print("✓ Summary generation test passed")


def test_json_export():
    """Test JSON export functionality"""
    import tempfile
    import json
    
    tracker = CostTracker()
    tracker.start_workflow()
    tracker.track_llm_call("TestAgent", "gpt-4o-mini", 100, 50)
    tracker.end_workflow()
    
    # Export to temporary file
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
        temp_path = f.name
    
    try:
        tracker.export_to_json(temp_path)
        
        # Read and verify
        with open(temp_path, 'r') as f:
            data = json.load(f)
        
        assert "summary" in data
        assert "events" in data
        assert len(data["events"]) == 1
        print("✓ JSON export test passed")
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)


def run_all_tests():
    """Run all tests"""
    print("=" * 60)
    print("Running Core Functionality Tests")
    print("=" * 60)
    print()
    
    tests = [
        test_cost_tracker_initialization,
        test_track_llm_call,
        test_track_tool_call,
        test_track_agent_step,
        test_agent_summaries,
        test_cost_calculation,
        test_spike_detection,
        test_summary_generation,
        test_json_export
    ]
    
    failed = []
    for test in tests:
        try:
            test()
        except Exception as e:
            print(f"✗ {test.__name__} failed: {e}")
            failed.append(test.__name__)
    
    print()
    print("=" * 60)
    if not failed:
        print("✅ ALL TESTS PASSED")
    else:
        print(f"❌ {len(failed)} TEST(S) FAILED:")
        for name in failed:
            print(f"  - {name}")
    print("=" * 60)
    
    return len(failed) == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
