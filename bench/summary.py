import glob, json, os, statistics as st, sys
rows = [json.load(open(f)) for f in glob.glob(os.path.join(sys.argv[1], "*.json"))]
cfgs = sorted({r["cfg"] for r in rows}); tasks = sorted({r["task"] for r in rows})
def agg(rs, k): v = [r[k] for r in rs if r.get(k) is not None]; return st.mean(v) if v else float("nan")
print(f"{'config':18} {'runs':>4} {'pass':>6} {'cost$':>7} {'out_tok':>8} {'ans_chr':>8} {'code_ln':>8} {'turns':>6} {'secs':>6}")
for c in cfgs:
    rs = [r for r in rows if r["cfg"] == c]; graded = [r for r in rs if r["ok"] is not None]
    print(f"{c:18} {len(rs):>4} {sum(r['ok'] for r in graded):>3}/{len(graded):<2} {agg(rs,'cost'):7.3f} {agg(rs,'out_tok'):8.0f} "
          f"{agg(rs,'answer_chars'):8.0f} {agg([r for r in rs if r['task'] in ('T2_bugfix','T3_feature')],'changed_lines'):8.1f} {agg(rs,'turns'):6.1f} {agg(rs,'secs'):6.1f}")
print("\nper task: mean cost $ / mean answer chars")
print(f"{'task':12}" + "".join(f"{c:>22}" for c in cfgs))
for t in tasks:
    print(f"{t:12}" + "".join(f"{agg([r for r in rows if r['cfg']==c and r['task']==t],'cost'):>11.3f}{agg([r for r in rows if r['cfg']==c and r['task']==t],'answer_chars'):>11.0f}" for c in cfgs))
bad = [f"{r['cfg']}/{r['task']}/{r['rep']}" for r in rows if r["ok"] is False or r["error"] or r["rc"]]
print("\nfailed or errored:", bad or "none")
