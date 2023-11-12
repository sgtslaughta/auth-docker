import streamlit as st
import plotly.express as px
import pandas as pd


class Info:
    def __init__(self):
        self.status = st.status(label="Waiting for connection..",
                                state="running")
        try:
            self.svr = st.session_state["svr"]
            if not self.svr:
                return
            self.status.update(label="Connected", state="complete")
            self.data = self.svr.ops.get_svr_data()
            self.show_data()
        except KeyError:
            pass

    def show_data(self):
        if self.data:
            st.write("Server Info")
            col1, col2 = st.columns(2)
            with col1:
                logins = self.data["logins"]
                if logins:
                    data = []
                    for metric, values in logins.items():
                        for entry in values:
                            data.append(
                                {"Metric": metric, "X_Coord": entry["x_cord"],
                                 "Y_Coord": entry["y_cord"]})
                    df = pd.DataFrame(data)
                    login_fig = px.scatter(df, x='X_Coord', y='Y_Coord',
                                           color='Metric',
                                           title='Hourly Login Metrics')
                    st.plotly_chart(login_fig,
                                    use_container_width=True,
                                    sharing="streamlit")
            with col2:
                version = self.data["version"]
                st.metric(label="Current Server Version",
                          value=version["version_current"],
                          delta=version["version_latest"],
                          help="The current version of the Authentik server "
                               "compared to the latest available version")
                if version["version_current"] != version["version_latest"]:
                    st.warning("Update Available", icon="⚠️")

                # print(self.data["tasks"])
                # Convert task data to a Pandas DataFrame
                df = pd.DataFrame(self.data["tasks"])

                # Convert the timestamp strings to datetime objects
                df['task_finish_timestamp'] = pd.to_datetime(
                    df['task_finish_timestamp'])

                # Extract hour from the timestamp
                df['hour'] = df['task_finish_timestamp'].dt.hour

                # Filter tasks with status "SUCCESSFUL"
                successful_tasks = df[df['status'] == 'SUCCESSFUL']
                tasks = df

                # Count the number of successful tasks per hour
                tasks_per_hour = successful_tasks.groupby(
                    'hour').size().reset_index(name='count')

                # Create a bar chart using Plotly Express
                fig = px.density_heatmap(df, x='hour',
                                         y='task_finish_timestamp',
                                         title='Tasks per Hour',
                                         labels={
                                             'task_finish_timestamp': 'Task '
                                                                      'Finish Timestamp'},
                                         facet_col='status')

                # Display the Plotly figure in the Streamlit app
                st.plotly_chart(fig, use_container_width=True,
                                sharing="streamlit")

            with st.expander("Sessions"):
                os_col, uagent_col, geo_col = st.columns(3)
                session_df = pd.DataFrame(self.data['sessions']['results'])

                with os_col:
                    # Extract user agent details
                    user_agent_df = pd.json_normalize(session_df['user_agent'])

                    # Create a pivot table for counting occurrences
                    heatmap_data = user_agent_df.groupby(
                        ['os.family', 'user_agent.family']).size().reset_index(
                        name='count')
                    heatmap_data = heatmap_data.pivot(index='os.family',
                                                      columns='user_agent.family',
                                                      values='count').fillna(0)

                    # Create a heatmap using plotly.express.imshow
                    fig = px.imshow(heatmap_data,
                                    labels=dict(x="User Agent", y="OS",
                                                color="Count"),
                                    x=list(heatmap_data.columns),
                                    y=list(heatmap_data.index),
                                    title='User Agent vs OS')
                    st.plotly_chart(fig, use_container_width=True,
                                    sharing="streamlit")
                with uagent_col:
                    # Convert 'last_used' to datetime format
                    session_df['last_used'] = pd.to_datetime(
                        session_df['last_used'])

                    # Create a scatter plot using Plotly Express
                    lu_fig = px.scatter(session_df, x='last_used',
                                        y='last_used',
                                        title='Sessions Last Used')
                    st.plotly_chart(lu_fig, use_container_width=True,
                                    sharing="streamlit",
                                    theme="streamlit")
                # with geo_col:
                #     # Access latitude and longitude from the nested "geo_ip"
                #     # field
                #     session_df['latitude'] = session_df['geo_ip'].apply(
                #         lambda x: x[
                #             'lat'] if x is not None else None)
                #     session_df['longitude'] = session_df['geo_ip'].apply(
                #         lambda x:
                #         x['long'] if x is not None else None)
                #     st.map(df[['latitude', 'longitude']])
                st.dataframe(session_df)

            st.subheader("System Info")
            system = self.data["system"]
            sys_data = pd.DataFrame(system)
            st.dataframe(sys_data)


info = Info()
