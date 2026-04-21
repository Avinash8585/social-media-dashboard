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

# ================= AUTO REFRESH (30s SAFE) =================
st_autorefresh(interval=30000, key="refresh")

# ================= PAGE CONFIG =================
st.set_page_config(
    page_title="Ultimate Enterprise Social Intelligence",
    layout="wide",
    page_icon="🚀"
)

# ================= UI =================
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
box-shadow:0 4px 25px rgba(0,0,0,0.5);
}
.live-card{
background:rgba(255,255,255,0.1);
padding:10px;
border-radius:10px;
margin:5px 0;
}
</style>
""", unsafe_allow_html=True)

# ================= FIREBASE =================
firebase_config = dict(st.secrets["firebase"])

if not firebase_admin._apps:
    cred = credentials.Certificate(firebase_config)
    firebase_admin.initialize_app(cred)

db = firestore.client()

# ================= LOAD DATA =================
@st.cache_data(ttl=30)
def load_data():
    try:
        docs = db.collection("posts") \
            .order_by("timestamp", direction=firestore.Query.DESCENDING) \
            .limit(50) \
            .stream()
        return [doc.to_dict() for doc in docs]
    except Exception as e:
        st.error(f"Firebase Error: {e}")
        return []

data = load_data()

if not data:
    st.warning("Waiting for live data...")
    st.stop()

df = pd.DataFrame(data)

# ================= PROCESS =================
df["timestamp"] = pd.to_datetime(df["timestamp"])
df["engagement"] = df["likes"] + df["comments"] + df["shares"]
df["sentiment"] = df["text"].apply(lambda x: TextBlob(x).sentiment.polarity)
df["hour"] = df["timestamp"].dt.hour
df["day"] = df["timestamp"].dt.day_name()

# ================= HEADER =================
st.title("🚀 Enterprise Social Media Dashboard")
st.caption(f"Last Updated: {datetime.now().strftime('%H:%M:%S')}")

# ================= KPIs =================
c1,c2,c3,c4 = st.columns(4)
c1.metric("Posts", len(df))
c2.metric("Engagement", int(df["engagement"].sum()))
c3.metric("Avg Engagement", int(df["engagement"].mean()))
c4.metric("Sentiment", round(df["sentiment"].mean(),2))

st.divider()

# ================= GAUGE =================
def gauge(title,val,max_val,color):
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=val,
        title={'text':title},
        gauge={'axis':{'range':[0,max_val]}, 'bar':{'color':color}}
    ))
    fig.update_layout(template="plotly_dark")
    return fig

g1,g2,g3 = st.columns(3)
g1.plotly_chart(gauge("Engagement", df["engagement"].mean(),2000,"cyan"))
g2.plotly_chart(gauge("Sentiment", df["sentiment"].mean()*100,100,"green"))
g3.plotly_chart(gauge("Posts", len(df),500,"orange"))

st.divider()

# ================= CHARTS =================

col1,col2 = st.columns(2)

with col1:
    st.subheader("📊 Topic Engagement")
    fig = px.bar(df, x="topic", y="engagement", color="topic")
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("📈 Time Trend")
    fig = px.line(df, x="timestamp", y="engagement")
    st.plotly_chart(fig, use_container_width=True)

# ================= AREA CHART =================
st.subheader("📉 Engagement Area")
fig = px.area(df, x="timestamp", y="engagement", color="topic")
st.plotly_chart(fig, use_container_width=True)

# ================= PIE =================
st.subheader("🥧 Post Type")
fig = px.pie(df, names="type")
st.plotly_chart(fig, use_container_width=True)

# ================= DONUT =================
st.subheader("🍩 Topic Share")
fig = px.pie(df, names="topic", hole=0.5)
st.plotly_chart(fig, use_container_width=True)

# ================= HEATMAP =================
st.subheader("🔥 Activity Heatmap")
heat = df.pivot_table(values="engagement", index="hour", columns="topic", aggfunc="sum")
fig = px.imshow(heat, aspect="auto")
st.plotly_chart(fig, use_container_width=True)

# ================= SCATTER =================
st.subheader("🎯 Sentiment vs Engagement")
fig = px.scatter(df, x="sentiment", y="engagement", color="type")
st.plotly_chart(fig, use_container_width=True)

# ================= BOX =================
st.subheader("📦 Engagement Distribution")
fig = px.box(df, x="topic", y="engagement")
st.plotly_chart(fig, use_container_width=True)

# ================= LEADERBOARD =================
st.subheader("🏆 Top Users")
top_users = df.groupby("user")["engagement"].sum().sort_values(ascending=False).head(5)
st.dataframe(top_users)

# ================= ALERT =================
if df["engagement"].mean() > 1000:
    st.warning("⚡ High Engagement Detected")

# ================= WORD CLOUD =================
st.subheader("☁️ Word Cloud")
text = " ".join(df["text"])
wc = WordCloud(width=800, height=400).generate(text)
plt.imshow(wc)
plt.axis("off")
st.pyplot(plt)

# ================= LIVE FEED =================
st.subheader("📡 Live Feed")
for _,row in df.head(5).iterrows():
    st.markdown(f"""
    <div class="live-card">
    <b>{row['user']}</b> — #{row['topic']}<br>
    ❤️ {row['likes']} | 💬 {row['comments']} | 🔁 {row['shares']}
    </div>
    """, unsafe_allow_html=True)

# ================= DOWNLOAD =================
st.download_button("Download CSV", df.to_csv(index=False), "data.csv")
