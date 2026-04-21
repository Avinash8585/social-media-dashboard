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
st_autorefresh(interval=30000, key="refresh")

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
firebase_config = dict(st.secrets["firebase"])

if not firebase_admin._apps:
    cred = credentials.Certificate(firebase_config)
    firebase_admin.initialize_app(cred)

db = firestore.client()

# 🔥 CACHE + LIMIT FIX + SAFE DEBUG
@st.cache_data(ttl=30)
def load_data():
    try:
        docs = db.collection("posts") \
            .order_by("timestamp", direction=firestore.Query.DESCENDING) \
            .limit(20) \
            .stream()

        data = [doc.to_dict() for doc in docs]

        return data

    except Exception as e:
        st.error(f"Firebase Error: {e}")
        return []

data = load_data()

if not data:
    st.error("❌ No data received from Firebase")
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

# ================= (REST OF YOUR CODE UNCHANGED) =================
# 👉 everything below remains EXACT SAME
