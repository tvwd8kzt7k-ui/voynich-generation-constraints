#!/usr/bin/env python3
"""Canonical all-seen exact-reuse diagnostic.

This is a new explicit test, not a reconstruction of the historical simulation.
The observed family/context sequence is conditioned on.  Within each held-out
bifolio, every exact form previously generated/observed in the same family gets
the SAME multiplicative weight w.  The base distribution is the canonical
context model from context_hand.py (alpha=.5, tau=100) fit outside the target.

Two outputs are kept separate:
1) conditional LOBO likelihood, which asks whether broad all-seen salience helps;
2) fixed-seed free exact-choice simulations on the observed family/context
   scaffold, which ask whether that mechanism alone reproduces the global exact
   frequency spectrum.
"""
from __future__ import annotations

import argparse, json, math, sys
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from canonical.core import ho, iter_clean42_records, support_for_family

ALPHA=.5; TAU=100.0
FIT_GRID=[1.0,1.1,1.25,1.5,2.0,3.0,4.0,6.0,8.0,12.0]
SIM_WEIGHTS=[1,2,4,8,16,32]
SIM_REPS=8
SEED_BASE=2026092800

class XorShift32:
    def __init__(self,seed): self.x=seed & 0xffffffff
    def random(self):
        x=self.x
        x ^= (x << 13) & 0xffffffff; x ^= x >> 17; x ^= (x << 5) & 0xffffffff
        self.x=x & 0xffffffff
        return self.x/4294967296.0

def add(store,key,exact):
    z=store[key]; z["n"]+=1; z["c"][exact]+=1

def subtract(a,b):
    if a is None:return {"n":0,"c":Counter()}
    bc=b["c"] if b else Counter()
    return {"n":a["n"]-(b["n"] if b else 0),"c":Counter({x:n-bc.get(x,0) for x,n in a["c"].items() if n-bc.get(x,0)>0})}

def spectrum(counts):
    bins={"1":0,"2":0,"3":0,"4-5":0,"6-10":0,"11-20":0,"21+":0}
    for n in counts.values():
        if n==1:bins["1"]+=1
        elif n==2:bins["2"]+=1
        elif n==3:bins["3"]+=1
        elif n<=5:bins["4-5"]+=1
        elif n<=10:bins["6-10"]+=1
        elif n<=20:bins["11-20"]+=1
        else:bins["21+"]+=1
    return {"types":len(counts),"hapax":bins["1"],"mid_2_to_20":sum(bins[k] for k in ("2","3","4-5","6-10","11-20")),"high_21_plus":bins["21+"],"bins":bins}

def analyze(text):
    records=list(iter_clean42_records(text)); by_bif=defaultdict(list)
    empty=lambda:{"n":0,"c":Counter()}
    G=defaultdict(empty); C=defaultdict(empty); bG=defaultdict(empty); bC=defaultdict(empty)
    supports={}
    for r in records:
        by_bif[r["bifolio"]].append(r); fam=r["family"]; ex=r["exact"]
        supports.setdefault(fam,support_for_family(fam))
        add(G,fam,ex);add(C,(r["context"],fam),ex);add(bG,(r["bifolio"],fam),ex);add(bC,(r["bifolio"],r["context"],fam),ex)

    cache={}
    def distribution_excluding(exclude1, exclude2, r):
        # exclude1 is the final held-out bifolio; exclude2 is optionally the
        # training bifolio currently being scored while fitting w.
        ck=(exclude1,exclude2,r["context"],r["family"])
        if ck in cache:return cache[ck]
        fam=r["family"]; sup=supports[fam]
        def sub2(a,b,c):
            if a is None:return {"n":0,"c":Counter()}
            bc=b["c"] if b else Counter(); cc=c["c"] if c else Counter()
            return {
                "n":a["n"]-(b["n"] if b else 0)-(c["n"] if c else 0),
                "c":Counter({x:n-bc.get(x,0)-cc.get(x,0) for x,n in a["c"].items() if n-bc.get(x,0)-cc.get(x,0)>0}),
            }
        g=sub2(G.get(fam),bG.get((exclude1,fam)),bG.get((exclude2,fam)) if exclude2 else None)
        c=sub2(C.get((r["context"],fam)),bC.get((exclude1,r["context"],fam)),bC.get((exclude2,r["context"],fam)) if exclude2 else None)
        k=len(sup); probs=[]
        for ex in sup:
            pg=(g["c"].get(ex,0)+ALPHA)/(g["n"]+ALPHA*k)
            probs.append((c["c"].get(ex,0)+TAU*pg)/(c["n"]+TAU))
        s=sum(probs); probs=[p/s for p in probs]
        z={"support":sup,"probs":probs,"index":{x:i for i,x in enumerate(sup)}};cache[ck]=z;return z

    def sequence_terms(seq_bif, exclude1, exclude2=None):
        seen=defaultdict(dict); ll0=0.0; terms=[]
        for r in by_bif[seq_bif]:
            d=distribution_excluding(exclude1,exclude2,r); idx=d["index"][r["exact"]]; p0=d["probs"][idx]
            ss=seen[r["family"]]
            mass=sum(d["probs"][d["index"][x]] for x in ss if x in d["index"])
            terms.append((r["exact"] in ss,mass)); ll0+=math.log(p0); ss[r["exact"]]=None
        return ll0,terms

    def score_terms(ll0,terms,w):
        ll=ll0
        for hit,mass in terms:
            ll += (math.log(w) if hit else 0.0) - math.log(1+(w-1)*mass)
        return ll

    total0=total1=N=0; positive=0; fits=[]; per=[]
    for target in ho.CLEAN42:
        training_terms=[]
        for train_bif in ho.CLEAN42:
            if train_bif==target:continue
            training_terms.append(sequence_terms(train_bif,target,train_bif))
        bestw=1.0;bestll=-math.inf
        for w in FIT_GRID:
            s=sum(score_terms(ll0,terms,w) for ll0,terms in training_terms)
            if s>bestll:bestll=s;bestw=w
        l0,terms=sequence_terms(target,target,None);l1=score_terms(l0,terms,bestw);n=len(terms)
        total0+=l0;total1+=l1;N+=n;positive+=l1>l0;fits.append(bestw)
        per.append({"bifolio":target,"n":n,"fitted_weight":bestw,"gain_per_token":(l1-l0)/n})
        cache.clear()  # keep nested-LOBO memory bounded target by target

    def base_sample(d,R):
        u=R.random();s=0.0
        for i,p in enumerate(d["probs"]):
            s+=p
            if u<s:return i
        return len(d["probs"])-1

    def simulate(weight,seed):
        R=XorShift32(seed); counts=Counter()
        for target in ho.CLEAN42:
            seen=defaultdict(dict)
            for r in by_bif[target]:
                d=distribution_excluding(target,None,r); ss=seen[r["family"]]
                mass=sum(d["probs"][d["index"][x]] for x in ss if x in d["index"])
                den=1+(weight-1)*mass; p_seen=weight*mass/den
                j=None
                if ss and R.random()<p_seen:
                    u=R.random()*mass;s=0.0
                    for ex in ss:
                        if ex not in d["index"]:continue
                        k=d["index"][ex];s+=d["probs"][k]
                        if u<=s:j=k;break
                else:
                    while True:
                        j=base_sample(d,R)
                        if d["support"][j] not in ss or len(ss)>=len(d["support"]):break
                ex=d["support"][j];counts[ex]+=1;ss[ex]=None
        return spectrum(counts)

    observed=spectrum(Counter(r["exact"] for r in records)); sims={}
    for w in SIM_WEIGHTS:
        reps=[simulate(w,SEED_BASE+rep+round(w*100)) for rep in range(SIM_REPS)]
        summary={}
        for metric in ("types","hapax","mid_2_to_20","high_21_plus"):
            vals=sorted(x[metric] for x in reps); summary[metric]={"median":(vals[3]+vals[4])/2,"min":vals[0],"max":vals[-1]}
        sims[str(w)]={"summary":summary,"replicates":reps}

    fs=sorted(fits)
    return {
        "status":"canonical-current-analysis",
        "model":{"alpha":ALPHA,"tau":TAU,"fit_grid":FIT_GRID,"uniform_seen_scope":"previously seen exact forms within same family and bifolio"},
        "conditional_lobo":{"n_tokens":N,"baseline_ll_per_token":total0/N,"reuse_ll_per_token":total1/N,"gain_per_token":(total1-total0)/N,"positive_bifolios":positive,"fitted_weight":{"median":fs[len(fs)//2],"min":fs[0],"max":fs[-1],"counts":dict(Counter(str(x).rstrip('0').rstrip('.') for x in fits))},"per_bifolio":per},
        "spectrum_simulation":{"observed":observed,"weights":sims,"n_replicates":SIM_REPS,"seed_rule":"2026092800 + replicate_index + round(weight*100)","interpretation_ceiling":"Uniform all-seen reinforcement improves conditional predictive likelihood, but under this fixed generator it does not by itself recover the observed exact-form concentration. Even strong weights retain too many types/hapax. The older claim that uniform reuse necessarily creates too many medium-frequency forms is not retained by this canonical test."},
    }

def compare_subset(actual,expected,path="",tol=1e-10):
    errors=[]
    if isinstance(expected,dict):
        for k,v in expected.items():
            if k not in actual:errors.append(f"missing {path}/{k}")
            else:errors.extend(compare_subset(actual[k],v,f"{path}/{k}",tol))
    elif isinstance(expected,float):
        if not math.isclose(float(actual),expected,rel_tol=tol,abs_tol=tol):errors.append(f"mismatch {path}: {actual!r} != {expected!r}")
    else:
        if actual!=expected:errors.append(f"mismatch {path}: {actual!r} != {expected!r}")
    return errors

def main():
    ap=argparse.ArgumentParser();ap.add_argument("--input",type=Path,required=True);ap.add_argument("--output",type=Path,default=Path("canonical/results/uniform_reuse.json"));ap.add_argument("--check",type=Path);a=ap.parse_args()
    data=a.input.read_bytes()
    if ho.git_blob_sha1(data)!=ho.EXPECTED_GIT_BLOB_SHA1:raise SystemExit("input Git blob SHA-1 mismatch")
    result=analyze(data.decode("utf-8"));a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    if a.check:
        errors=compare_subset(result,json.loads(a.check.read_text(encoding="utf-8")))
        if errors:print("CHECK FAILED");print("\n".join(" - "+x for x in errors));raise SystemExit(1)
        print("CHECK OK")
    print(json.dumps({"conditional_lobo":{k:v for k,v in result["conditional_lobo"].items() if k!="per_bifolio"},"spectrum_simulation":{"observed":result["spectrum_simulation"]["observed"],"weights":{w:z["summary"] for w,z in result["spectrum_simulation"]["weights"].items()}}},indent=2,ensure_ascii=False))
if __name__=="__main__":main()
