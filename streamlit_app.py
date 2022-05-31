import streamlit as st
import pandas as pd
from pytz import country_names
from st_aggrid import AgGrid, GridUpdateMode, JsCode
from st_aggrid.grid_options_builder import GridOptionsBuilder
import snowflake.connector
from snowflake.connector.pandas_tools import write_pandas
from snowflake.connector import connect


@st.experimental_memo
def load_data():
    df = pd.read_csv("CSV_samples/country-list.csv")
    return df


@st.experimental_memo
def convert_df(df):
    # IMPORTANT: Cache the conversion to prevent computation on every rerun
    return df.to_csv().encode("utf-8")


def execute_query(conn, df_sel_row, table_name):
    if not df_sel_row.empty:
        conn.cursor().execute(
            "CREATE OR REPLACE TABLE "
            f"{table_name}(COUNTRY string, CAPITAL string, TYPE string)"
        )
        write_pandas(
            conn=conn,
            df=df_sel_row,
            table_name=table_name,
            database="STREAMLIT_DB",
            schema="PUBLIC",
            quote_identifiers=False,
        )


# Initialize connection.
# Uses st.experimental_singleton to only run once.
@st.experimental_singleton
def init_connection():
    return snowflake.connector.connect(**st.secrets["snowflake"])


# The code below is for the title and logo.
st.set_page_config(page_title="Dataframe with editable cells", page_icon="💾")
st.image(
    "https://emojipedia-us.s3.dualstack.us-west-1.amazonaws.com/thumbs/240/apple/325/floppy-disk_1f4be.png",
    width=100,
)
conn = init_connection()
df = load_data()
st.title("Dataframe with editable cells")
st.write("")
st.markdown(
    """This is a demo of a dataframe with editable cells, powered by 
[streamlit-aggrid](https://pypi.org/project/streamlit-aggrid/). 
You can edit the cells by clicking on them, and then export 
your selection to a `.csv` file (or send it to your Snowflake DB!)"""
)
st.write("")
st.write("")
st.subheader("① Edit and select cells")
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

st.subheader(" ② Check your selection")

st.write("")

df_sel_row = pd.DataFrame(sel_row)
csv = convert_df(df_sel_row)
if not df_sel_row.empty:
    st.write(df_sel_row)
st.download_button(
    label="Download to CSV",
    data=csv,
    file_name="results.csv",
    mime="text/csv",
)
st.write("")
st.write("")

st.subheader("③ Send to Snowflake DB ❄️")

st.write("")
table_name = st.text_input("Pick a table name", "YOUR_TABLE_NAME_HERE", help="No spaces allowed")
run_query = st.button(
    "Add to DB", on_click=execute_query, args=(conn, df_sel_row, table_name)
)
if run_query and not df_sel_row.empty:
    st.success(
        f"✔️ Selection added to the `{table_name}` table located in the `STREAMLIT_DB` database."
    )
    st.snow()

if run_query and df_sel_row.empty:
    st.info("Nothing to add to DB, please select some rows")

