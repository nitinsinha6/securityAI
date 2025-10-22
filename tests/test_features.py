import pandas as pd
from core.synth import synthesize
from core.features import add_features

def test_features_shape():
    df = synthesize(days=1, users=5, seed=1)
    df_f, cols = add_features(df, 8, 18)
    assert len(cols) > 5
    assert all(c in df_f.columns for c in cols)
