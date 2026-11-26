import sys, os, numpy as np, pandas as pd, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
D,O=sys.argv[1],sys.argv[2]; os.makedirs(f"{O}/figures",exist_ok=True)
BLUE,ORANGE,AQUA="#257de0","#f47230","#00b894"; INK="#191919"; INK2="#666666"; GRID="#e7e7e7"; AXIS="#c2c2c2"
plt.rcParams.update({"font.family":["Lato","DejaVu Sans"],"font.size":10,"axes.edgecolor":AXIS,"axes.labelcolor":INK2,"xtick.color":INK2,"ytick.color":INK2,
 "axes.spines.top":False,"axes.spines.right":False,"axes.grid":True,"grid.color":GRID,"grid.linewidth":1,"axes.axisbelow":True,"figure.facecolor":"white","axes.facecolor":"white","text.color":INK})
def legend(fig,items,loc="lower center",ncol=3,y=-0.01):
    h=[Line2D([0],[0],marker="o",color="none",markerfacecolor=c,markeredgecolor="white",markeredgewidth=1.5,markersize=9,label=l) for l,c in items]
    fig.legend(handles=h,loc=loc,ncol=ncol,frameon=False,bbox_to_anchor=(0.5,y),labelcolor=INK2,fontsize=10,handletextpad=0.3,columnspacing=1.6)
# ---------- Fig 1: reliability vs redundancy of 40-yard-dash tracking features
cr=pd.read_csv(f"{D}/combine_results.csv",na_values=["NA"]).set_index("nfl_id"); f=pd.read_csv(f"{O}/forty_run_features.csv")
names={"v10":"Speed at 10 yd","v20":"Speed at 20 yd","v30":"Speed at 30 yd","vmax":"Top speed","t40":"Time to 38 yd","t10":"Time to 10 yd","peak_acc":"Peak acceleration","d95":"Yards to 95% of top speed","t_vmax":"Time of top speed","maint":"Speed maintenance"}
speed={"v10","v20","v30","vmax","t40"}
two=f[f.run<=2].pivot(index="nfl_id",columns="run",values=list(names)).dropna()
P=f.groupby("nfl_id")[list(names)].mean().join(cr[["forty","ten_yd_split","combine_weight"]]).dropna()
X=np.c_[np.ones(len(P)),P.forty,P.ten_yd_split,P.combine_weight]; pts={}
for m in names:
    y=P[m].values; b=np.linalg.lstsq(X,y,rcond=None)[0]; r2=1-((y-X@b)**2).sum()/((y-y.mean())**2).sum()
    pts[m]=(r2,np.corrcoef(two[(m,1)],two[(m,2)])[0,1])
fig,ax=plt.subplots(figsize=(7.4,5.2))
for m,(x,y) in pts.items(): ax.plot(x,y,"o",color=BLUE if m in speed else ORANGE,markersize=9,markeredgecolor="white",markeredgewidth=2,zorder=3)
off={"v10":(-9,-12,"right"),"v20":(-12,-3,"right"),"v30":None,"vmax":None,"t40":(9,-4,"left"),"t10":(9,-4,"left"),"peak_acc":(9,-4,"left"),"d95":(0,10,"center"),"t_vmax":(9,-10,"left"),"maint":(-9,6,"right")}
for m,o in off.items():
    if o is None: continue
    lab="Speed at 20 and 30 yd,\ntop speed" if m=="v20" else names[m]
    ax.annotate(lab,pts[m],xytext=(o[0],o[1]),textcoords="offset points",ha=o[2],fontsize=9.5,color=INK2)
ax.set_xlim(0,1.04); ax.set_ylim(0,1.05); ax.set_xlabel("Share already explained by official 40 time, 10-yd split and weight (R²)"); ax.set_ylabel("Test-retest reliability (run 1 vs run 2, r)")
ax.text(0.02,1.0,"Reliable and not redundant would sit here: no feature does",fontsize=9.5,color=INK2,style="italic",va="top")
for s in ("left","bottom"): ax.spines[s].set_color(AXIS)
fig.suptitle("Figure 1. Tracked 40-yard-dash speed repeats well but repeats the stopwatch",x=0.02,ha="left",fontsize=12,fontweight="semibold",y=0.985)
legend(fig,[("Overall speed and time",BLUE),("Acceleration shape and split timing",ORANGE)],ncol=2,y=0.0); fig.tight_layout(rect=(0,0.05,1,0.95)); fig.savefig(f"{O}/figures/fig1_reliability_vs_redundancy.png",dpi=200); plt.close(fig)
# ---------- Fig 2: error vs snaps
R=pd.read_csv(f"{O}/snaps_equivalent_results.csv")
panels=[("WR adjusted separation","WR separation (yd²)"),("DL get-off (lower=faster)","DL get-off (s²)"),("DL in-game top speed","DL in-game top speed ((yd/s)²)")]
fig,axs=plt.subplots(1,3,figsize=(11,4.1))
for ax,(key,title) in zip(axs,panels):
    d=R[R.outcome==key].sort_values("k")
    for col,c in (("mse_raw",AQUA),("mse_pos",ORANGE),("mse_comb",BLUE)):
        ax.plot(d.k,d[col],color=c,linewidth=2,marker="o",markersize=8,markeredgecolor="white",markeredgewidth=2,solid_capstyle="round",zorder=3)
    ax.set_yscale("log"); ax.set_xticks([0,10,25,50,100]); ax.set_title(title,loc="left",fontsize=10.5,color=INK,fontweight="semibold"); ax.set_xlabel("NFL snaps used (first k plays)")
    for s in ("left","bottom"): ax.spines[s].set_color(AXIS)
axs[0].set_ylabel("Squared error vs last-100-play average (log scale)")
fig.suptitle("Figure 2. Most of the gain over raw early averages comes from shrinking toward a prior",x=0.01,ha="left",fontsize=12,fontweight="semibold",y=0.99)
legend(fig,[("Average of early snaps only",AQUA),("Shrunk to position average",ORANGE),("Shrunk to Combine prior",BLUE)],ncol=3,y=0.0); fig.tight_layout(rect=(0,0.07,1,0.93)); fig.savefig(f"{O}/figures/fig2_error_vs_snaps.png",dpi=200); plt.close(fig)
# ---------- Fig 3: prior-weight dumbbell
S=R.drop_duplicates("outcome").copy(); lab={"DL get-off (lower=faster)":"DL get-off","WR adjusted separation":"WR separation","OL pressure allowed":"OL pressure allowed","WR in-game top speed":"WR top speed","DL in-game top speed":"DL top speed","DB in-game top speed":"DB top speed","OL in-game top speed":"OL top speed"}
B3=pd.read_csv(f"{O}/n0_bootstrap.csv").set_index("outcome"); S["lab"]=S.outcome.map(lab); S=S.sort_values("n0_comb").reset_index(drop=True)
H=pd.read_csv(f"{O}/robustness_holm.csv").set_index("outcome")
def verdict(o):
    h=H.loc[o]
    if h.rule_met_in_seeds_of_5>=5: return "rule met; survives Holm" if h["holm_reject_at_.05"] else "rule met; fails Holm"
    return "rule not met"
fig,ax=plt.subplots(figsize=(8.4,4.5)); ax.grid(axis="y",visible=False)
for i,r in S.iterrows():
    ax.plot([B3.loc[r.outcome,"n0_lo"],B3.loc[r.outcome,"n0_hi"]],[i,i],color=BLUE,linewidth=1.5,alpha=0.45,zorder=1,solid_capstyle="butt")
    ax.plot([r.n0_pos,r.n0_comb],[i,i],color=AXIS,linewidth=2,zorder=2,solid_capstyle="round")
    ax.plot(r.n0_pos,i,"o",color=ORANGE,markersize=11,markeredgecolor="white",markeredgewidth=2,zorder=3)
    ax.plot(r.n0_comb,i,"o",color=BLUE,markersize=8,markeredgecolor="white",markeredgewidth=2,zorder=4)
    ax.text(1000,i,verdict(r.outcome),va="center",fontsize=9.5,color=INK2,clip_on=False)
ax.set_xscale("log"); ax.set_xlim(5,700); ax.set_xticks([10,30,100,300]); ax.set_xticklabels(["10","30","100","300"]); ax.set_yticks(range(len(S))); ax.set_yticklabels(S.lab); ax.set_xlabel("Model-implied prior weight, in independent-play equivalents (log scale)\nBlue band: 95% player-bootstrap range for the Combine-informed weight")
for s in ("left","bottom"): ax.spines[s].set_color(AXIS)
fig.suptitle("Figure 3. Model-implied weight of a Combine-informed prior",x=0.02,ha="left",fontsize=12,fontweight="semibold",y=0.985)
legend(fig,[("Prior = position average",ORANGE),("Prior = 40 time, 10-yd split, weight",BLUE)],ncol=2,y=0.0); fig.tight_layout(rect=(0,0.06,0.78,0.95)); fig.savefig(f"{O}/figures/fig3_snaps_equivalent.png",dpi=200); plt.close(fig)
# ---------- Fig 4: sensor vs stopwatch, paired held-out error difference (forest plot)
Q=pd.read_csv(f"{O}/sensor_vs_stopwatch.csv"); Q=Q[Q.k.isin([0,25])].copy()
Q["rel"]=Q.gain/Q.mse_pos; Q["rlo"]=Q.lo/Q.mse_pos; Q["rhi"]=Q.hi/Q.mse_pos
order=["DL get-off","WR adj separation","WR top speed","DL top speed","DB top speed","OL top speed"]
Q["o"]=Q.outcome.str.replace(" (lower=faster)","",regex=False); Q["o"]=Q.o.replace({"WR adj separation":"WR separation"}); order=["DL get-off","WR separation","WR top speed","DL top speed","DB top speed","OL top speed"]
fig,ax=plt.subplots(figsize=(8.2,4.4)); ax.grid(axis="y",visible=False)
for j,(kk,col,dy) in enumerate(((0,BLUE,0.14),(25,ORANGE,-0.14))):
    for i,o in enumerate(order[::-1]):
        r=Q[(Q.o==o)&(Q.k==kk)]
        if r.empty: continue
        r=r.iloc[0]; ax.plot([r.rlo,r.rhi],[i+dy,i+dy],color=col,linewidth=2,zorder=3,solid_capstyle="butt"); ax.plot(r.rel,i+dy,"o",color=col,markersize=8,markeredgecolor="white",markeredgewidth=2,zorder=4)
ax.axvline(0,color=INK2,linewidth=1,zorder=2)
ax.set_yticks(range(len(order))); ax.set_yticklabels(order[::-1]); ax.set_ylim(-0.6,len(order)-0.4)
ax.set_xlabel("Stopwatch-prior error minus sensor-prior error, as a share of position-average error (95% CI)\nRight of zero: sensor prior better; left: stopwatch prior better")
for s_ in ("left","bottom"): ax.spines[s_].set_color(AXIS)
fig.suptitle("Figure 4. No detectable difference between sensor and stopwatch priors",x=0.02,ha="left",fontsize=12,fontweight="semibold",y=0.985)
legend(fig,[("k = 0 early plays",BLUE),("k = 25 early plays",ORANGE)],ncol=2,y=0.0); fig.tight_layout(rect=(0,0.06,1,0.95)); fig.savefig(f"{O}/figures/fig4_sensor_vs_stopwatch.png",dpi=200); plt.close(fig)
print("figures:",sorted(os.listdir(f"{O}/figures")))
