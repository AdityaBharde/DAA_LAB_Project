import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import itertools

st.markdown(
    """
    <style>
        [data-testid="stSidebar"] {
            min-width: 400px;
            max-width: 400px;
        }
    </style>
    """,
    unsafe_allow_html=True
)

st.set_page_config(page_title="Job Scheduling", page_icon="💼", layout="centered")
st.title("Job Scheduling Algorithm Comparison")
st.sidebar.header("Input Options")

mode = st.sidebar.radio("Mode", ["Upload CSV", "Manual Entry"])

default = [
    {'id': 'J1', 'start': 1, 'finish': 3, 'profit': 50},
    {'id': 'J2', 'start': 3, 'finish': 5, 'profit': 60},
    {'id': 'J3', 'start': 0, 'finish': 6, 'profit': 120},
    {'id': 'J4', 'start': 5, 'finish': 7, 'profit': 30},
    {'id': 'J5', 'start': 5, 'finish': 9, 'profit': 80},
    {'id': 'J6', 'start': 7, 'finish': 8, 'profit': 25}
]

if mode == "Upload CSV":
    f = st.sidebar.file_uploader("Upload CSV", type=["csv"])
    if f:
        jobs_df = pd.read_csv(f)
    else:
        jobs_df = pd.DataFrame(default)
else:
    n = st.sidebar.number_input("No. of Jobs", 1, 10, 6)
    data = []
    for i in range(n):
        with st.sidebar.expander(f"Job {i+1}"):
            jid = st.text_input(f"ID {i+1}", f"J{i+1}")
            s = st.number_input(f"Start {jid}", 0, value=default[i]['start'] if i < len(default) else 0)
            fsh = st.number_input(f"Finish {jid}", 0, value=default[i]['finish'] if i < len(default) else 0)
            p = st.number_input(f"Profit {jid}", 0, value=default[i]['profit'] if i < len(default) else 0)
            data.append({'id': jid, 'start': s, 'finish': fsh, 'profit': p})
    jobs_df = pd.DataFrame(data)

st.subheader("Jobs Data")
st.dataframe(jobs_df)

jobs = jobs_df.to_dict('records')

def greedy(jobs):
    jobs = sorted(jobs, key=lambda x: (x['finish'] - x['start']))
    res = []
    last = -1
    profit = 0
    for j in jobs:
        if j['start'] >= last:
            res.append(j)
            last = j['finish']
            profit += j['profit']
    return res, profit

def last_non_conflict(jobs, i):
    for j in range(i-1, -1, -1):
        if jobs[j]['finish'] <= jobs[i]['start']:
            return j
    return -1

def dp_interval(jobs):
    jobs = sorted(jobs, key=lambda x: x['finish'])
    n = len(jobs)
    dp = [0] * n
    dp[0] = jobs[0]['profit']
    for i in range(1, n):
        inc = jobs[i]['profit']
        l = last_non_conflict(jobs, i)
        if l != -1:
            inc += dp[l]
        dp[i] = max(inc, dp[i-1])
    sel = []
    i = n - 1
    while i >= 0:
        inc = jobs[i]['profit']
        l = last_non_conflict(jobs, i)
        if l != -1:
            inc += dp[l]
        if inc > (dp[i-1] if i >= 1 else 0):
            sel.append(jobs[i])
            i = l
        else:
            i -= 1
    sel.reverse()
    return sel, dp[-1]

def compatible(s):
    for i in range(len(s)):
        for j in range(i+1, len(s)):
            if not (s[i]['finish'] <= s[j]['start'] or s[j]['finish'] <= s[i]['start']):
                return False
    return True

def backtrack(jobs):
    best = 0
    comb = []
    for r in range(1, len(jobs)+1):
        for sub in itertools.combinations(jobs, r):
            if compatible(sub):
                p = sum(j['profit'] for j in sub)
                if p > best:
                    best = p
                    comb = sub
    return list(comb), best

g_jobs, g_prof = greedy(jobs)
d_jobs, d_prof = dp_interval(jobs)
b_jobs, b_prof = backtrack(jobs)

comp = pd.DataFrame({
    'Algorithm': ['Greedy', 'DP', 'Backtracking'],
    'Jobs': [','.join(j['id'] for j in g_jobs),
             ','.join(j['id'] for j in d_jobs),
             ','.join(j['id'] for j in b_jobs)],
    'Profit': [g_prof, d_prof, b_prof]
})

st.subheader("Comparison")
st.dataframe(comp)

def gantt(sel, title):
    fig, ax = plt.subplots(figsize=(6, 2))
    for j in sel:
        ax.barh(j['id'], j['finish'] - j['start'], left=j['start'])
    ax.set_xlabel("Time")
    ax.set_ylabel("Job")
    ax.set_title(title)
    ax.grid(True)
    st.pyplot(fig)

st.subheader("Schedules")

c1, c2 = st.columns(2)

with c1:
    st.write("Greedy")
    gantt(g_jobs, "Greedy")

with c2:
    st.write("DP")
    gantt(d_jobs, "DP")

st.write("Backtracking")
gantt(b_jobs, "Backtracking")

st.subheader("Profit Chart")
fig, ax = plt.subplots(figsize=(6, 3))
ax.bar(comp['Algorithm'], comp['Profit'], color=['#1f77b4', '#2ca02c', '#d62728'])
ax.set_ylabel("Profit")
ax.grid(axis='y')
st.pyplot(fig)
