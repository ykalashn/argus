import streamlit as st
import pandas as pd
import sqlite3
import os

# Database connection helper
def get_db_connection():
    db_path = os.path.join(os.path.dirname(__file__), "..", "argus.db")
    return sqlite3.connect(db_path)

# Removed cache to ensure live database syncs
def load_cases_data():
    conn = get_db_connection()
    cases = pd.read_sql("SELECT * FROM cases", conn)
    metrics = pd.read_sql("SELECT * FROM case_metrics", conn)
    conn.close()
    return cases, metrics

cases_df, metrics_df = load_cases_data()

if 'selected_case' in st.session_state and st.session_state['selected_case'] is not None:
    case_id = st.session_state['selected_case']
        
    # Fetch Dynamic Detail Data
    conn = get_db_connection()
    case_data = pd.read_sql(f"SELECT * FROM cases WHERE ID = '{case_id}'", conn)
    conn.close()

    if case_data.empty:
        st.error("Case data not found.")
        st.stop()
        
    row = case_data.iloc[0]

    st.markdown("<br>", unsafe_allow_html=True)
    header_col1, header_col2, header_col3 = st.columns([1, 8, 3], vertical_alignment="bottom")

    with header_col1:
        st.markdown(f"""
        <div style="width: 80px; height: 80px; background-color: #471524; color: white; border-radius: 16px; display: flex; align-items: center; justify-content: center; font-size: 32px; font-weight: bold; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
            {row['ENTITY_NAME'][:2].upper()}
        </div>
        """, unsafe_allow_html=True)

    with header_col2:
        flag_color = "#ffdad6" if row["STATUS"] != "AUTO-CLEARED" else "#b3ebff"
        text_color = "#93000a" if row["STATUS"] != "AUTO-CLEARED" else "#004e5f"
        flag_label = "HIGH RISK HIT" if row["RISK_SCORE"] > 70 else ("REVIEW TRIGGERED" if row["RISK_SCORE"] > 40 else "CLEARED")
        
        st.markdown(f"<div style='display:flex; align-items:center; gap: 12px; margin-bottom: 4px;'><h1 style='margin:0; padding:0; color: #2c0210;'>{row['ENTITY_NAME']}</h1><span style='background-color: {flag_color}; color: {text_color}; padding: 4px 12px; border-radius: 16px; font-size: 12px; font-weight: bold; display:flex; align-items:center; gap:4px;'><span class='material-symbols-rounded' style='font-size:16px;'>flag</span> {flag_label}</span></div>", unsafe_allow_html=True)
        st.caption(f"**ID:** {row['ID']} &nbsp;&nbsp;•&nbsp;&nbsp; **Location:** {row['COUNTRY']} &nbsp;&nbsp;•&nbsp;&nbsp; **Created:** {row['CREATED_DATE']}")

    with header_col3:
        st.markdown("""
        <style>
        .icon-btn { color: #8C7C83; font-size: 24px; cursor: pointer; transition: color 0.15s ease; }
        .icon-btn:hover { color: #2c0210; }
        </style>
        <div style='display:flex; gap: 16px; justify-content:flex-end; align-items:center; height:100%; padding-bottom:4px;'>
            <span class='material-symbols-rounded icon-btn' title="Share Case">share</span>
            <span class='material-symbols-rounded icon-btn' title="Print View">print</span>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    col_left, col_right = st.columns([7, 4])

    with col_left:
        with st.container(border=True):
            st.markdown(f"<div style='display:flex; gap:16px; align-items:flex-start;'><div style='background-color:#2c0210; color:white; padding:8px; border-radius:8px;'><span class='material-symbols-rounded'>auto_awesome</span></div><div><h4 style='margin:0; color:#2c0210;'>{row['AI_INSIGHT_TITLE']}</h4><p style='margin-top:8px; font-size:14px; color:#1a1c1d;'>{row['AI_INSIGHT_DESC']}</p></div></div>", unsafe_allow_html=True)

        with st.container(border=True):
            conn_wl = get_db_connection()
            wl_hits_df = pd.read_sql(f"SELECT * FROM watchlist_hits WHERE CASE_ID = '{case_id}'", conn_wl)
            conn_wl.close()

            st.markdown("<div style='display:flex; justify-content:space-between; align-items:center; margin-bottom: 24px;'><h4 style='margin:0;'>Watchlist Hit Details</h4><span style='font-size:10px; font-weight:600; color:#524346; letter-spacing: 0.5px; text-transform: uppercase;'>Source: World-Check Global</span></div>", unsafe_allow_html=True)
            
            if not wl_hits_df.empty:
                table_html = """<div style="border-radius: 8px; overflow: hidden; border: 1px solid #EFEBEB; width: 100%;">
<table style="width: 100%; text-align: left; border-collapse: collapse; font-family: 'Inter', sans-serif;">
<thead style="background-color: #f3f3f5; border-bottom: 1px solid #EFEBEB;">
<tr>
<th style="padding: 12px 24px; font-size: 10px; text-transform: uppercase; letter-spacing: 1px; color: #524346; font-weight: 700;">Attribute</th>
<th style="padding: 12px 24px; font-size: 10px; text-transform: uppercase; letter-spacing: 1px; color: #524346; font-weight: 700;">Subject Data</th>
<th style="padding: 12px 24px; font-size: 10px; text-transform: uppercase; letter-spacing: 1px; color: #524346; font-weight: 700;">Watchlist Hit</th>
<th style="padding: 12px 24px; font-size: 10px; text-transform: uppercase; letter-spacing: 1px; color: #524346; font-weight: 700;">Status</th>
</tr>
</thead>
<tbody style="background-color: #ffffff;">"""
                for idx, h_row in wl_hits_df.iterrows():
                    match_stat = h_row['MATCH_STATUS']
                    bg_col = "#b3ebff" if match_stat == "MATCH" else ("#cfc4c6" if match_stat == "MISMATCH" else "#e8dddf")
                    txt_col = "#001f27" if match_stat == "MATCH" else "#4c4547"
                    bb_style = 'border-bottom: 1px solid #EFEBEB;' if idx < len(wl_hits_df) - 1 else ''
                    table_html += f"""
<tr style="{bb_style}">
<td style="padding: 16px 24px; font-weight: 600; font-size: 14px; color: #1a1c1d;">{h_row['ATTRIBUTE']}</td>
<td style="padding: 16px 24px; font-size: 14px; color: #524346;">{h_row['SUBJECT_DATA']}</td>
<td style="padding: 16px 24px; font-weight: 700; font-size: 14px; color: #2c0210;">{h_row['WATCHLIST_DATA']}</td>
<td style="padding: 16px 24px;"><span style="background-color: {bg_col}; color: {txt_col}; padding: 4px 8px; border-radius: 4px; font-size: 10px; font-weight: 700;">{match_stat}</span></td>
</tr>"""
                table_html += """</tbody>
</table>
</div>"""
                st.markdown(table_html, unsafe_allow_html=True)
            else:
                st.markdown("<div style='padding:16px; background-color:#f3f3f5; border-radius:8px; font-size:14px; color:#524346;'>No watchlist attributes flagged for this entity.</div>", unsafe_allow_html=True)
            
        st.markdown("<div style='display:flex; justify-content:space-between; align-items:center; margin-top:24px; margin-bottom: 16px;'><h3 style='margin:0; font-size: 18px; font-weight: 700; color: #1a1c1d;'>Decision History</h3><span style='font-size: 14px; font-weight: 600; color: #471524; cursor: pointer;'>View Audit Log</span></div>", unsafe_allow_html=True)
            
        conn_hist = get_db_connection()
        history_df = pd.read_sql(f"SELECT * FROM decision_history WHERE CASE_ID = '{case_id}' ORDER BY SORT_ORDER DESC", conn_hist)
        conn_hist.close()
        
        timeline_parts = ["<div style='margin-left: 20px; border-left: 2px solid #e2e2e4; position: relative; padding-bottom: 4px; font-family: \"Inter\", sans-serif;'>"]
        for idx, h_row in history_df.iterrows():
            title = h_row['TITLE']
            desc = h_row['DESCRIPTION']
            date = h_row['TIMESTAMP']
            dot_color = "#2c0210" if idx == 0 else "#e2e2e4" 
            margin_bottom = "24px" if idx < len(history_df) - 1 else "0"
            timeline_parts.append(f"""
<div style='position: relative; padding-left: 24px; margin-bottom: {margin_bottom};'>
    <div style='position: absolute; left: -9px; top: 0px; width: 16px; height: 16px; border-radius: 50%; background-color: {dot_color}; box-shadow: 0 0 0 4px #f9f9fb;'></div>
    <div style='display: flex; flex-direction: column;'>
        <span style='font-size: 10px; text-transform: uppercase; color: #524346; font-weight: 600; letter-spacing: 0.5px;'>{date}</span>
        <p style='margin: 4px 0 2px 0; font-size: 14px; font-weight: 600; color: #1a1c1d;'>{title}</p>
        <p style='margin: 0; font-size: 12px; color: #524346;'>{desc}</p>
    </div>
</div>
""")
        timeline_parts.append("</div>")
        st.markdown("".join(timeline_parts), unsafe_allow_html=True)

        # Unified Review Decision Module
        st.markdown("<div style='margin-top:24px;'></div>", unsafe_allow_html=True)
        with st.form(key=f"review_form_{case_id}", clear_on_submit=True, border=True):
            new_note = st.text_area("Leave a comment with your review decision...", label_visibility="collapsed", placeholder="Leave a comment with your review decision...")
            
            st.markdown("<hr style='margin: 16px 0; border: none; border-top: 1px solid #EFEBEB;'>", unsafe_allow_html=True)
            
            rc1, rc2, rc3, rc4 = st.columns([3, 1.2, 2.5, 2.5], vertical_alignment="center")
            with rc1:
                st.markdown("<div style='display:flex; align-items:center; gap:8px;'><span class='material-symbols-rounded' style='color:#4A192C; font-size:20px;'>verified_user</span><span style='font-size:14px; font-weight:700; color:#1a1c1d;'>Your Review Decision</span></div>", unsafe_allow_html=True)
            with rc2:
                st.markdown("<div style='font-size:14px; font-weight:700; color:#1a1c1d; text-align:right;'>Recommend</div>", unsafe_allow_html=True)
            with rc3:
                decision = st.selectbox("Decision", ["Cleared", "Escalate", "Reject & Block"], label_visibility="collapsed")
            with rc4:
                submit_review = st.form_submit_button("Submit Review", type="primary", use_container_width=True)
                
            if submit_review:
                conn_n = get_db_connection()
                from datetime import datetime
                now_str = datetime.now().strftime("Today, %I:%M %p")
                
                desc_str = new_note if new_note.strip() else "No additional rationale provided."
                title_str = f"Analyst Review: {decision}"
                
                cur_hist = pd.read_sql(f"SELECT MAX(SORT_ORDER) as m FROM decision_history WHERE CASE_ID='{case_id}'", conn_n)
                max_order = int(cur_hist['m'].iloc[0]) if not cur_hist.empty and pd.notna(cur_hist['m'].iloc[0]) else 0
                
                conn_n.execute("INSERT INTO decision_history (CASE_ID, SORT_ORDER, TIMESTAMP, TITLE, DESCRIPTION) VALUES (?, ?, ?, ?, ?)",
                               (case_id, max_order + 1, now_str, title_str, f"Analyst Julian Thome ({decision}): " + desc_str))
                
                new_stat = "AUTO-CLEARED" if decision == "Cleared" else ("Investigation" if decision == "Escalate" else "Blocked")
                conn_n.execute("UPDATE cases SET STATUS = ? WHERE ID = ?", (new_stat, case_id))
                
                conn_n.commit()
                conn_n.close()
                st.rerun()

    with col_right:
        # Re-assigned Resolution block to timeline builder
        pass

        with st.container(border=True):
            conn_ev = get_db_connection()
            ev_df = pd.read_sql(f"SELECT * FROM evidence_files WHERE CASE_ID = '{case_id}'", conn_ev)
            conn_ev.close()
            
            st.markdown(f"<div style='display:flex; justify-content:space-between; align-items:center;'><h4 style='margin:0;'>Evidence & Files</h4><span style='background-color:#e8dddf; color:#696163; padding:2px 8px; border-radius:4px; font-size:10px; font-weight:bold;'>{len(ev_df)} FILES</span></div>", unsafe_allow_html=True)
            st.divider()
            
            for idx, e_row in ev_df.iterrows():
                fname = e_row['FILE_NAME']
                fdate = e_row['UPLOAD_DATE']
                icon = "receipt_long" if ".pdf" in fname else "image"
                st.markdown(f"<div style='display:flex; align-items:center; gap:12px; margin-bottom:12px;'><div style='background-color:#f3f3f5; color:#1a1c1d; width:40px; height:40px; border-radius:8px; display:flex; align-items:center; justify-content:center;'><span class='material-symbols-rounded'>{icon}</span></div><div><div style='font-size:12px; font-weight:bold;'>{fname}</div><div style='font-size:10px; color:#524346;'>{fdate}</div></div></div>", unsafe_allow_html=True)
            
            st.markdown("<div style='margin-top:12px;'></div>", unsafe_allow_html=True)
            st.file_uploader("Drop additional evidence", accept_multiple_files=True, label_visibility="collapsed")



else:
    st.title("Case Management")

    # Top Metrics Row
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        val = metrics_df[metrics_df['metric'] == 'Active Cases']['value'].values[0]
        delta = metrics_df[metrics_df['metric'] == 'Active Cases']['delta'].values[0]
        st.metric("Active Cases", val, delta=delta, delta_color="normal")

    with col2:
        val = metrics_df[metrics_df['metric'] == 'Pending Review (High Risk)']['value'].values[0]
        delta = metrics_df[metrics_df['metric'] == 'Pending Review (High Risk)']['delta'].values[0]
        st.metric("Pending Review (High Risk)", val, delta=delta, delta_color="inverse")

    with col3:
        val = metrics_df[metrics_df['metric'] == 'AI Auto-Cleared (24H)']['value'].values[0]
        delta = metrics_df[metrics_df['metric'] == 'AI Auto-Cleared (24H)']['delta'].values[0]
        st.metric("AI Auto-Cleared (24H)", val, delta=delta, delta_color="normal")

    with col4:
        val = metrics_df[metrics_df['metric'] == 'Avg. Resolution Time']['value'].values[0]
        delta = metrics_df[metrics_df['metric'] == 'Avg. Resolution Time']['delta'].values[0]
        st.metric("Avg. Resolution Time", f"{val} hrs", delta=delta if delta else None)

    st.markdown("<br>", unsafe_allow_html=True)

    # Filters Row
    f_col1, f_col2, f_col3, f_col_empty, f_col4 = st.columns([2, 2, 2, 5, 3])
    with f_col1:
        st.selectbox("Filters", ["All Statuses", "Requires Review", "In Progress"], label_visibility="collapsed")
    with f_col2:
        st.selectbox("Risk", ["Risk: All Levels", "High", "Medium", "Low"], label_visibility="collapsed")
    with f_col3:
        st.selectbox("Entity", ["Entity: All", "Corporate", "Individual"], label_visibility="collapsed")
    with f_col4:
        st.button("+ New Case", type="primary", use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Responsive Case HTML Interactive Anchor Cards 
    st.markdown("""
<style>
.case-card {
    border: 1px solid #EFEBEB;
    border-radius: 8px;
    padding: 16px 24px;
    background-color: #ffffff;
    transition: box-shadow 0.2s ease, background-color 0.2s ease;
    margin-bottom: 16px;
    display: block;
    text-decoration: none !important;
    color: inherit !important;
}
.case-card:hover {
    background-color: #fafafa;
    box-shadow: 0 4px 12px rgba(0,0,0,0.05);
}
</style>
""", unsafe_allow_html=True)
    
    for idx, row in cases_df.iterrows():
        color = "#E53E3E" if row['STATUS'] == "Pending Review" else ("#D69E2E" if "Investigation" in row['STATUS'] else "#38A169")
        
        card_html = f"""<a href="?selected_case={row['ID']}" target="_self" class="case-card">
<div style="display: flex; align-items: center; justify-content: space-between; font-family: 'Inter', sans-serif;">
<div style="display: flex; flex-direction: column; width: 40%;">
<div style="display: flex; align-items: center; gap: 12px; margin-bottom: 4px;">
<img src="https://cdnjs.cloudflare.com/ajax/libs/twemoji/14.0.2/72x72/{row['FLAG_URL']}" style="width: 24px; height: 24px;" alt="Flag" />
<span style="font-weight: 700; font-size: 16px; color: #1a1c1d;">{row['ENTITY_NAME']}</span>
</div>
<span style="font-size: 11px; color: #8C7C83; font-weight: 700; letter-spacing: 0.5px; margin-left: 36px;">{row['TYPE']}</span>
</div>
<div style="width: 25%;">
<div style="font-size: 10px; font-weight: 700; color: #524346; margin-bottom: 6px;">RISK SCORE: {row['RISK_SCORE']:.1f}</div>
<div style="width: 100%; height: 6px; background-color: #f3f3f5; border-radius: 3px; overflow: hidden;">
<div style="width: {row['RISK_SCORE']}%; height: 100%; background-color: #4A192C; border-radius: 3px;"></div>
</div>
</div>
<div style="width: 15%;">
<div style="font-size: 10px; font-weight: 700; color: #8C7C83; margin-bottom: 2px;">AI CONFIDENCE</div>
<div style="font-weight: 700; font-size: 14px; color: #1a1c1d;">{row['AI_CONFIDENCE']}</div>
</div>
<div style="width: 15%; text-align: right;">
<span style="background-color: {color}; color: white; padding: 6px 14px; border-radius: 4px; font-size: 12px; font-weight: 700; display: inline-block;">{row['STATUS']}</span>
</div>
</div>
</a>"""
        st.markdown(card_html, unsafe_allow_html=True)

