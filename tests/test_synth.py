from core.synth import synthesize

def test_synth_basic():
    df = synthesize(days=2, users=10, seed=123)
    assert len(df) > 0
    assert {"timestamp","user_id","event_type","amount","country","lat","lon"}.issubset(df.columns)
