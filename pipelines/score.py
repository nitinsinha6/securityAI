import argparse, os, pandas as pd
from core.model import infer, ai_summary

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="inp", required=True)
    ap.add_argument("--model_dir", default="models")
    ap.add_argument("--out", default="data/insights.csv")
    ap.add_argument("--limit", type=int, default=1000)
    args = ap.parse_args()

    df = pd.read_csv(args.inp)
    df_scored = infer(df, model_dir=args.model_dir)
    df_scored["summary"] = df_scored.apply(ai_summary, axis=1)
    df_scored.sort_values("risk_score", ascending=False).head(args.limit).to_csv(args.out, index=False)
    print("Wrote insights to", args.out)

if __name__ == "__main__":
    main()
