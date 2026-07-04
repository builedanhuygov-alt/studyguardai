from studyguard.demo_mode import run_demo


def test_demo_runs_and_prints(capsys):
    summary = run_demo(cycles=1, sleep_s=0.0)
    assert summary["hours"] > 0
    out = capsys.readouterr().out
    assert "DEMO MODE" in out
    assert "Weekly AI-Coach summary" in out


def test_presentation_mode_runs():
    summary = run_demo(present=True, cycles=1, sleep_s=0.0)
    assert "narrative" in summary
