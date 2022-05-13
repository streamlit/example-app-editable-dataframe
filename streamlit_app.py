import streamlit as st
import pandas as pd
from st_aggrid import AgGrid, GridUpdateMode, JsCode
from st_aggrid.grid_options_builder import GridOptionsBuilder

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
    df = pd.read_csv("covid-variants.csv")
    return df


df = data_upload()

st.title("Dataframe with editable cells")
st.write("")
st.markdown(
    "This is a demo of a dataframe with editable cells, powered by [streamlit-aggrid](https://pypi.org/project/streamlit-aggrid/). You can edit the cells by clicking on them and then export your selection to a `.csv` file."
)
st.write("")
st.write("")

st.subheader("① Select and Edit cells")

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
    height=500,
    theme="material",
    allow_unsafe_jscode=True,
    # enable_enterprise_modules = True,
    # theme="fresh",
)

sel_row = grid_table["selected_rows"]

# st.write("---")

st.subheader(" ② Check your selection")

df_sel_row = pd.DataFrame(sel_row)


@st.cache
def convert_df(df):
    # IMPORTANT: Cache the conversion to prevent computation on every rerun
    return df.to_csv().encode("utf-8")


csv = convert_df(df_sel_row)
st.write("")
st.download_button(
    label="Download your selection to CSV",
    data=csv,
    file_name="results.csv",
    mime="text/csv",
)

st.write("")
st.write(sel_row)
