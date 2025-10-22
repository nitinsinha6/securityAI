import argparse, os, pandas as pd
from core.model import train, save_artifacts

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="inp", required=True, help="Input CSV of events")
    ap.add_argument("--model_dir", default="models")
    args = ap.parse_args()

    df = pd.read_csv(args.inp)
    art = train(df)
    save_artifacts(art, args.model_dir)
    print("Saved model to", args.model_dir)

if __name__ == "__main__":
    main()
