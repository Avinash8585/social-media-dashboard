import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import firebase_admin
from firebase_admin import credentials, firestore
from streamlit_autorefresh import st_autorefresh
from textblob import TextBlob
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from datetime import datetime
import numpy as np

# ================= AUTO REFRESH =================
st_autorefresh(interval=5000, key="refresh")

# ================= PAGE CONFIG =================
st.set_page_config(
    page_title="Ultimate Enterprise Social Intelligence",
    layout="wide",
    page_icon="🚀"
)

# ================= PREMIUM UI =================
st.markdown("""
<style>

body {
    background: linear-gradient(-45deg,#1e3c72,#2a5298,#141e30,#243b55);
    background-size:400% 400%;
    animation:gradientBG 15s ease infinite;
}

@keyframes gradientBG {
0% {background-position:0% 50%;}
50% {background-position:100% 50%;}
100% {background-position:0% 50%;}
}

.metric-card{
background:rgba(20,30,48,0.85);
padding:20px;
border-radius:15px;
color:white;
backdrop-filter:blur(10px);
box-shadow:0 4px 25px rgba(0,0,0,0.5);
transition:0.4s;
}

.metric-card:hover{
transform:scale(1.08);
}

.live-card{
background:rgba(255,255,255,0.1);
padding:10px;
border-radius:10px;
margin:5px 0;
transition:0.3s;
}

.live-card:hover{
transform:scale(1.05);
}

.ticker{
overflow:hidden;
white-space:nowrap;
background:rgba(0,0,0,0.4);
padding:10px;
border-radius:10px;
margin-bottom:15px;
}

.ticker span{
display:inline-block;
padding-left:100%;
animation:ticker 25s linear infinite;
}

@keyframes ticker{
0%{transform:translateX(0);}
100%{transform:translateX(-100%);}
}

</style>
""", unsafe_allow_html=True)

# ================= FIREBASE =================
if not firebase_admin._apps:
    cred = credentials.Certificate("firebase_key.json")
    firebase_admin.initialize_app(cred)

db = firestore.client()
docs = db.collection("posts").stream()
data = [doc.to_dict() for doc in docs]

if not data:
    st.warning("Waiting for streaming data...")
    st.stop()

df = pd.DataFrame(data)

# ================= DATA PROCESSING =================
df["timestamp"] = pd.to_datetime(df["timestamp"])
df["engagement"] = df["likes"] + df["comments"] + df["shares"]
df["sentiment"] = df["text"].apply(lambda x: TextBlob(x).sentiment.polarity)

df["engagement_index"] = (
(df["engagement"]-df["engagement"].min()) /
(df["engagement"].max()-df["engagement"].min())
)*100

# ================= HEADER =================
st.title("🚀 Real-Time Social Media Enterprise Dashboard")
st.caption(f"Last Updated: {datetime.now().strftime('%H:%M:%S')}")

# ================= TICKER =================
top_topic = df["topic"].value_counts().idxmax()
top_user = df.groupby("user")["engagement"].sum().idxmax()

st.markdown(f"""
<div class="ticker">
<span>
🔥 Trending Topic: {top_topic} |
👑 Top User: {top_user} |
📊 Total Posts: {len(df)} |
📈 Avg Engagement: {int(df["engagement"].mean())}
</span>
</div>
""", unsafe_allow_html=True)

# ================= KPI SECTION =================
col1,col2,col3,col4,col5 = st.columns(5)

def kpi(title,value):
    st.markdown(f"""
    <div class="metric-card">
        <h4>{title}</h4>
        <h2>{value}</h2>
    </div>
    """, unsafe_allow_html=True)

with col1:
    kpi("Total Posts",len(df))

with col2:
    kpi("Total Engagement",int(df["engagement"].sum()))

with col3:
    kpi("Avg Engagement",int(df["engagement"].mean()))

with col4:
    kpi("Sentiment Score",round(df["sentiment"].mean(),2))

with col5:
    kpi("Engagement Index",round(df["engagement_index"].mean(),2))

st.divider()

# ================= GAUGES =================
g1,g2,g3 = st.columns(3)

def gauge(title,value,max_val,color):

    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        title={'text':title},
        gauge={'axis':{'range':[0,max_val]},
               'bar':{'color':color}}
    ))

    fig.update_layout(template="plotly_dark")

    return fig

g1.plotly_chart(
gauge("Engagement Score",df["engagement"].mean(),2000,"cyan"),
use_container_width=True)

g2.plotly_chart(
gauge("Sentiment Score",df["sentiment"].mean()*100,100,"green"),
use_container_width=True)

g3.plotly_chart(
gauge("Activity Volume",len(df),500,"orange"),
use_container_width=True)

st.divider()

# ================= WEEKLY TREND =================
df["day"]=df["timestamp"].dt.day_name()

trend=df.groupby("day")["engagement"].sum().reset_index()

fig_trend=px.line(
trend,
x="day",
y="engagement",
markers=True,
title="Weekly Engagement Trend")

fig_trend.update_layout(template="plotly_dark")

st.plotly_chart(fig_trend,use_container_width=True)

# ================= TOPIC DISTRIBUTION =================
topic_dist=df["topic"].value_counts().reset_index()
topic_dist.columns=["Topic","Count"]

fig_topic=px.bar(
topic_dist,
x="Topic",
y="Count",
color="Count",
title="Topic Distribution")

fig_topic.update_layout(template="plotly_dark")

st.plotly_chart(fig_topic,use_container_width=True)

# ================= POST TYPE =================
type_dist=df["type"].value_counts().reset_index()
type_dist.columns=["Type","Count"]

fig_type=px.pie(
type_dist,
values="Count",
names="Type",
title="Post Type Distribution")

fig_type.update_layout(template="plotly_dark")

st.plotly_chart(fig_type,use_container_width=True)

# ================= LEADERBOARD =================
st.subheader("🏆 Top Users")

leader=df.groupby("user")["engagement"]\
.sum().sort_values(ascending=False).head(5)

for user,score in leader.items():
    st.write(f"👤 {user} — {score}")

# ================= VIRAL POSTS =================
st.subheader("🔥 Top Viral Posts")

viral=df.sort_values("engagement",
ascending=False).head(5)

st.dataframe(viral[["user","topic","engagement"]])

# ================= ALERT =================
avg_eng=df["engagement"].mean()

if avg_eng>1500:
    st.error("⚠ High Engagement Spike Detected!")

elif avg_eng>1000:
    st.warning("⚡ Engagement Rising")

else:
    st.success("✅ Engagement Stable")

# ================= HEATMAP =================
heat=df.groupby(df["timestamp"].dt.hour)\
.size().reset_index(name="Posts")

fig_heat=px.density_heatmap(
heat,
x="timestamp",
y="Posts",
title="Hourly Activity Heatmap")

fig_heat.update_layout(template="plotly_dark")

st.plotly_chart(fig_heat,use_container_width=True)

# ================= SENTIMENT SCATTER =================
fig_scatter=px.scatter(
df,
x="sentiment",
y="engagement",
color="type",
title="Sentiment vs Engagement")

fig_scatter.update_layout(template="plotly_dark")

st.plotly_chart(fig_scatter,use_container_width=True)

# ================= WORD CLOUD =================
st.subheader("Topic Word Cloud")

text=" ".join(df["topic"])

wc=WordCloud(
width=800,
height=400,
background_color="#141e30"
).generate(text)

plt.imshow(wc)
plt.axis("off")

st.pyplot(plt)

# ================= LIVE FEED =================
st.subheader("📡 Live Activity Feed")

latest=df.sort_values("timestamp",
ascending=False).head(5)

for _,row in latest.iterrows():

    st.markdown(f"""
    <div class="live-card">
    <b>{row['user']}</b> — {row['topic']} <br>
    ❤️ {row['likes']} |
    💬 {row['comments']} |
    🔁 {row['shares']}
    </div>
    """,unsafe_allow_html=True)

# ================= DOWNLOAD =================
st.download_button(
"Download CSV",
df.to_csv(index=False),
"analytics.csv")