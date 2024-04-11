import streamlit as st
import pandas as pd
from datetime import datetime
import functions as func

func.check_requirements()
cities = func.get_country_city_list()


def requests_history_operation():
    if "history_table" in st.session_state:
        requests_history = func.get_requests_history()
        edited_rows = st.session_state["history_table"]["edited_rows"]

        if edited_rows:
            for index, value in edited_rows.items():
                if "Delete" in value:
                    if value["Delete"]:
                        func.delete_request_history(requests_history[index][0])
        pass


st.set_page_config(
    page_title="Open Weather Map API",
    page_icon="🌤️",
    layout="centered",
)

requests_history_operation()
current_datetime = datetime.now()

st.markdown("<h1 style='text-align: center;'>🌤️<br/>Open Weather Map API</h1>", unsafe_allow_html=True)
st.markdown("<div style='text-align: center;'>" + current_datetime.strftime("%d %b %Y") + "</div>",
            unsafe_allow_html=True)

st.selectbox('Select the city', [f"{city[1]}, {city[2]}" for city in cities], key="country_city")

weather_status = None

predict_tab, history_tab = st.tabs(["Predict", "Request history"])

with predict_tab:
    st.selectbox("Forcast type", options=["24 Hours", "5 Days"], key="forecast_type")

    if st.button("Show weather forecast", key="forecast_button"):

        country_city = st.session_state["country_city"].split(',')
        country_city = [item.strip() for item in country_city]

        city_selected = country_city[0]
        country_selected = country_city[1]

        city_index = [index for index, item in enumerate(cities) if
                      item[1] == city_selected and item[2] == country_selected]

        if city_index:
            weather_status = func.get_weather_status(cities[city_index[0]], st.session_state["forecast_type"])

with history_tab:
    if st.button("Clear history", key="clear_history_button", type="primary"):
        func.clear_requests_history()

    df = pd.DataFrame(
        [(f"{item[8]}/{item[9]}", item[2].strftime('%Y/%m/%d'), item[3], f"{item[4]}°C", f"{item[5]}hPa", f"{item[6]}%",
          func.meters_to_km(int(item[7])), False)
         for item in func.get_requests_history()],
        columns=["Location", "Req. Date", "Type", "Temp.", "Pressure", "Humidity",
                 "visibility", "Delete"])
    df_config = st.data_editor(
        df,
        column_config={
            "Location": st.column_config.TextColumn(
                width="medium",
                disabled=True
            ),
            "Req. Date": st.column_config.TextColumn(
                disabled=True,
            ),
            "Type": st.column_config.TextColumn(
                disabled=True,
            ),
            "Temp.": st.column_config.TextColumn(
                disabled=True,
            ),
            "Pressure": st.column_config.TextColumn(
                disabled=True,
            ),
            "Humidity": st.column_config.TextColumn(
                disabled=True,
            ),
            "visibility": st.column_config.TextColumn(
                disabled=True,
            )
        },
        hide_index=True,
        key="history_table"
    )

st.markdown(func.weather_card_html_layout(weather_status), unsafe_allow_html=True)

footer = """
<div class="st-emotion-cache-h5rgaw ea3mdgi1" style="text-align:center;margin-top:30px">
    &#169;2024 Meysam Davoudi, All Rights Reserved.
    <a href="https://github.com/Meysam-Davoudi/open_weather_api_streamlit" target="_blank" style="text-decoration:none;">
        (GITHUB)
    </a>
</div>
"""

st.markdown(footer, unsafe_allow_html=True)
