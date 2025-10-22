import pandas as pd
from core.synth import synthesize
from core.model import train, infer, ai_summary
from tempfile import TemporaryDirectory
from core.model import save_artifacts, load_artifacts

def test_train_infer_roundtrip():
    df = synthesize(days=3, users=20, seed=7)
    art = train(df)
    with TemporaryDirectory() as td:
        save_artifacts(art, td)
        _ = load_artifacts(td)
        df_out = infer(df, model_dir=td)
        assert "risk_score" in df_out.columns
        s = ai_summary(df_out.iloc[0])
        assert isinstance(s, str) and len(s) > 10
