if uploaded_file and 'fda_df' in st.session_state:
    tw_df = pd.read_csv(uploaded_file)
    st.write(f"📦 台灣藥品資料筆數：{len(tw_df)}")

    if st.button("開始比對"):
        with st.spinner("比對中..."):
            result_df, special_df = match_drugs(st.session_state['fda_df'], tw_df)
            st.session_state['result_df'] = result_df
            st.session_state['special_df'] = special_df
            st.success(f"✅ 比對完成，共 {len(result_df)} 筆公告。")

# 顯示結果
if 'result_df' in st.session_state:
    st.subheader("比對結果（完整）")
    st.dataframe(st.session_state['result_df'], use_container_width=True)

if 'special_df' in st.session_state:
    st.subheader("匹配到『中國化學』或『中化裕民』的公告")
    st.dataframe(st.session_state['special_df'], use_container_width=True)
