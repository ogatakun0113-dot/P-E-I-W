import streamlit as st
import math

# --- ページ設定 ---
st.set_page_config(page_title="消費電力計算アシスト (単相/三相対応)", layout="centered")

# --- 見た目の設定（CSS） ---
st.markdown("""
    <style>
    /* クレジット表示用のCSS */
    .credit {
        text-align: right;
        font-size: 14px;
        color: #666;
        margin-bottom: -20px;
    }
    /* 入力欄のラベルスタイル */
    .stNumberInput label, .stSelectbox label {
        font-size: 18px !important;
        color: #4169E1 !important;
        font-weight: 800 !important;
    }
    /* 計算結果ボックス */
    .result-box {
        background-color: #f0f2f6;
        padding: 15px;
        border-radius: 10px;
        border-left: 5px solid #4169E1;
        margin-top: 20px;
    }
    /* 電圧入力枠のスタイル */
    .v-grid-label {
        font-size: 14px;
        color: #555;
        margin-bottom: 5px;
    }
    </style>
    """, unsafe_allow_html=True)

# 右上にクレジットを表示
st.markdown('<p class="credit">開発/制作：緒方</p>', unsafe_allow_html=True)

st.title('⚡ 消費電力計算アシスト')
st.caption("※単相・三相3線式、力率 -1.0 〜 +1.0 対応")
st.markdown("---")

# --- 1. 方式選択 ---
col_opt1, col_opt2 = st.columns(2)
with col_opt1:
    phase = st.selectbox("結線方式を選択", ["単相 (1Φ)", "三相 (3Φ3W)"])
with col_opt2:
    mode = st.selectbox(
        "算出したい項目", 
        ["電力を求める (P)", "電流を求める (I)", "電圧を求める (V)"]
    )

# 三相の場合は係数を√3にする
root3 = math.sqrt(3) if phase == "三相 (3Φ3W)" else 1.0

# --- 三相用：個別電圧入力セクション ---
avg_v = 200.0
if phase == "三相 (3Φ3W)":
    with st.expander("📝 電圧個別の実測値を入力 (RST/UVW)", expanded=True):
        st.markdown('<p class="v-grid-label">電源側 電圧 (V)</p>', unsafe_allow_html=True)
        v_col1, v_col2, v_col3 = st.columns(3)
        vr = v_col1.number_input("R-S", value=0.0, step=0.1, format="%.1f")
        vs = v_col2.number_input("S-T", value=0.0, step=0.1, format="%.1f")
        vt = v_col3.number_input("T-R", value=0.0, step=0.1, format="%.1f")

        st.markdown('<p class="v-grid-label">負荷側 電圧 (V)</p>', unsafe_allow_html=True)
        v_col4, v_col5, v_col6 = st.columns(3)
        vu = v_col4.number_input("U-V", value=0.0, step=0.1, format="%.1f")
        vv = v_col5.number_input("V-W", value=0.0, step=0.1, format="%.1f")
        vw = v_col6.number_input("W-U", value=0.0, step=0.1, format="%.1f")

        # 入力があるものだけで平均値を計算
        v_list = [v for v in [vr, vs, vt, vu, vv, vw] if v > 0]
        if v_list:
            avg_v = sum(v_list) / len(v_list)
            st.info(f"平均電圧: {avg_v:.1f} V が下の計算に使用されます。")

st.markdown("---")

# 初期値
p_val, i_val, v_val, pf_val = 0.0, 0.0, 0.0, 1.0

# --- 2. メイン入力セクション ---
if mode == "電力を求める (P)":
    v_in = st.number_input("電圧 V (V)", value=float(avg_v), step=0.1, format="%.1f")
    i_in = st.number_input("電流 I (A)", value=10.0, step=0.1, format="%.2f")
    pf_in = st.number_input("力率 cosφ (-1.0〜+1.0)", value=1.0, min_value=-1.0, max_value=1.0, step=0.01)
    p_val = root3 * v_in * i_in * pf_in
    v_val, i_val, pf_val = v_in, i_in, pf_in

elif mode == "電流を求める (I)":
    p_in = st.number_input("電力 P (W)", value=2000.0, step=1.0, format="%.1f")
    v_in = st.number_input("電圧 V (V)", value=float(avg_v), step=0.1, format="%.1f")
    pf_in = st.number_input("力率 cosφ (-1.0〜+1.0)", value=1.0, min_value=-1.0, max_value=1.0, step=0.01)
    denom = root3 * v_in * pf_in
    i_val = abs(p_in / denom) if denom != 0 else 0
    p_val, v_val, pf_val = p_in, v_in, pf_in

elif mode == "電圧を求める (V)":
    p_in = st.number_input("電力 P (W)", value=2000.0, step=1.0, format="%.1f")
    i_in = st.number_input("電流 I (A)", value=10.0, step=0.1, format="%.2f")
    pf_in = st.number_input("力率 cosφ (-1.0〜+1.0)", value=1.0, min_value=-1.0, max_value=1.0, step=0.01)
    denom = root3 * i_in * pf_in
    v_val = abs(p_in / denom) if denom != 0 else 0
    p_val, i_val, pf_val = p_in, i_in, pf_in

# --- 3. 結果表示 ---
st.markdown('<div class="result-box">', unsafe_allow_html=True)
st.subheader(f"📊 計算結果 ({phase})")

col1, col2 = st.columns(2)
with col1:
    st.metric("有効電力 (P)", f"{p_val:,.2f} W")
    st.metric("電圧 (V)", f"{v_val:.1f} V")
with col2:
    st.metric("電流 (I)", f"{i_val:.3f} A")
    st.metric("力率 (cosφ)", f"{pf_val:.2f}")

s_val = root3 * v_val * i_val
st.write(f"（参考）皮相電力: **{abs(s_val):,.2f} VA**")
st.markdown('</div>', unsafe_allow_html=True)

if phase == "三相 (3Φ3W)":
    st.caption("※三相の計算式: $P = \\sqrt{3} \\cdot V_{avg} \\cdot I \\cdot \\cos \\phi$ を使用しています。")

# --- 画面下部中央に「戻る」ボタンを配置 ---
st.markdown("---")  # 区切り線
col1, col2, col3 = st.columns([1, 1, 1])

with col2:  # 中央の列を使用
    # 水色のアイコン（🏠）と「戻る」を表示するボタン
    if st.link_button("🏠\n\n戻る", "https://7fjndw39dicdzckugyepb2.streamlit.app/", use_container_width=True):
        pass

# ボタンの色（水色）を調整するカスタム設定
st.markdown("""
    <style>
    div.stLinkButton > a {
        background-color: #00BFFF !important; /* 水色（DeepSkyBlue） */
        color: white !important;
        border-radius: 10px;
        text-align: center;
        border: none;
    }
    </style>
    """, unsafe_allow_html=True)
