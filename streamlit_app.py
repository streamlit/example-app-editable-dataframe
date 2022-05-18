from pytz import country_names
import streamlit as st
import pandas as pd
from st_aggrid import AgGrid, GridUpdateMode, JsCode
from st_aggrid.grid_options_builder import GridOptionsBuilder

import streamlit as st
import snowflake.connector
from snowflake.connector.pandas_tools import write_pandas
from snowflake.connector import connect


# The code below is to control the layout width of the app.
if "widen" not in st.session_state:
    layout = "centered"
else:
    layout = "wide" if st.session_state.widen else "centered"

# The code below is for the title and logo.
st.set_page_config(
    layout=layout, page_title="Dataframe with editable cells", page_icon="💾"
)

st.image(
    "https://emojipedia-us.s3.dualstack.us-west-1.amazonaws.com/thumbs/240/apple/325/floppy-disk_1f4be.png",
    width=100,
)

@st.cache
def data_upload():
    df = pd.read_csv("CSV_samples/country-list.csv")
    # df = pd.read_csv("CSV_samples/african_countries.csv")
    return df


df = data_upload()

st.title("Dataframe with editable cells")
st.write("")
st.markdown(
    "This is a demo of a dataframe with editable cells, powered by [streamlit-aggrid](https://pypi.org/project/streamlit-aggrid/). You can edit the cells by clicking on them and then export your selection to a `.csv` file."
)
st.write("")
st.write("")

st.subheader("① Select and edit cells")

st.checkbox(
    "Widen layout",
    key="widen",
    help="Tick this box to toggle the layout to 'Wide' mode",
)
st.info("💡 Hold the `Shift` (⇧) key to select multiple rows at once.")

st.caption("")

gd = GridOptionsBuilder.from_dataframe(df)
gd.configure_pagination(enabled=True)
gd.configure_default_column(editable=True, groupable=True)
gd.configure_selection(selection_mode="multiple", use_checkbox=True)

gridoptions = gd.build()
grid_table = AgGrid(
    df,
    gridOptions=gridoptions,
    update_mode=GridUpdateMode.SELECTION_CHANGED,
    theme="material",
)

sel_row = grid_table["selected_rows"]

col1, col2 = st.columns(2)

with col1:

    st.subheader(" ② Check your selection")

    df_sel_row = pd.DataFrame(sel_row)

    @st.cache
    def convert_df(df):
        # IMPORTANT: Cache the conversion to prevent computation on every rerun
        return df.to_csv().encode("utf-8")

    csv = convert_df(df_sel_row)
    st.write("")
    st.download_button(
        label="Download to CSV",
        data=csv,
        file_name="results.csv",
        mime="text/csv",
    )

    st.write("")
    st.write(sel_row)

with col2:

    st.subheader("③ Send to Snowflake Db ❄️")

    st.write("")

    # Initialize connection.
    # Uses st.experimental_singleton to only run once.
    @st.experimental_singleton
    def init_connection():
        return snowflake.connector.connect(**st.secrets["snowflake"])

    conn = init_connection()

    Run_query2 = st.button("Add to Db")

    if Run_query2:

        conn.cursor().execute(
            "CREATE OR REPLACE TABLE "
            "NEW_TABLE(COUNTRY string, CAPITAL string, TYPE string)"
        )

        # conn.cursor().execute(
        #     "INSERT INTO NEW_TABLE(COUNTRY, CAPITAL, TYPE) VALUES "
        #     #  + "    (123, 'test string1'), "
        #     + "    ('0000', '0000', '0000')"
        # )
        # write_pandas(df, "test_table10", conn)

        write_pandas(
            conn=conn,
            df=df_sel_row,
            table_name="NEW_TABLE",
            database="PETS",
            schema="PUBLIC",
        )

        st.success("✅ Dataframe added to Db")

