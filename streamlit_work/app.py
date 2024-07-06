import pandas as pd
import pulp
import streamlit as st

from src.shift_scheduler.ShiftScheduler import ShiftScheduler

st.title("Shift scheduling app")
tab1, tab2, tab3 = st.tabs(["Calendar", "Staff", "Create Work Shift"])

with st.sidebar:
    st.header("Data Upload")
    calendar_file = st.file_uploader("Calendar", type=["csv"])
    staff_file = st.file_uploader("Staff", type=["csv"])

with tab1:
    if calendar_file is None:
        st.write("## Please upload the calendar information")
        st.write("example: calendar.csv")
        calendar_data = pd.read_csv("data/calendar.csv")
        st.download_button(
            "Download Example Calendar",
            "data/calendar.csv",
            file_name="calendar.csv",
            mime="text/csv"
        )
    else:
        st.markdown("## Calendar Information")
        calendar_data = pd.read_csv(calendar_file)

    st.table(calendar_data)

with tab2:
    if staff_file is None:
        st.write("Please upload the staff information")
        st.write("example: staff.csv")
        staff_data = pd.read_csv("data/staff.csv")
        st.download_button(
            "Download Example Staff",
            "data/staff.csv",
            file_name="staff.csv",
            mime="text/csv"
        )
    else:
        st.markdown("## Staff")
        staff_data = pd.read_csv(staff_file)

    st.table(staff_data)

with tab3:
    if calendar_file is None:
        st.write("Please upload the calendar information")
    if staff_file is None:
        st.write("Please upload the staff information")
    if staff_file is not None and calendar_file is not None:
        optimize_button = st.button("Run Optimization")
    else:
        optimize_button = st.button("Run with Example Data")
    if optimize_button:
        shift_scheduler = ShiftScheduler()
        shift_scheduler.set_data(staff_data, calendar_data)
        shift_scheduler.build_model()
        shift_scheduler.solve()

        st.markdown("## Optimization Results")

        st.write("Execution status:", pulp.LpStatus[shift_scheduler.status])
        st.write("Objective value:", pulp.value(shift_scheduler.model.objective))

        st.markdown("## Shift Table")
        st.table(shift_scheduler.sch_df)

        st.markdown("## Shift Number Satisfaction Confirmation")
        shift_num = shift_scheduler.sch_df.sum(axis=1)
        st.bar_chart(shift_num)

        st.markdown("## Staff's Hope Confirmation")
        shift_sum_slot = shift_scheduler.sch_df.sum(axis=0)
        st.bar_chart(shift_sum_slot)

        st.markdown("## Confirmation of the total number of shifts satisfied by the chief")
        chief_set = set(staff_data.query("責任者フラグ == 1")["スタッフID"])
        shift_chief_only = shift_scheduler.sch_df[shift_scheduler.sch_df.index.isin(chief_set)]
        shift_chief_sum = shift_chief_only.sum(axis=0)
        st.bar_chart(shift_chief_sum)

        st.download_button(
            "Download Shift Table",
            shift_scheduler.sch_df.to_csv().encode("utf-8"),
            file_name="shift_table.csv",
            mime="text/csv"
        )
