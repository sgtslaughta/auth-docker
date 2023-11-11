from lib.auth_svr import AuthServer
import streamlit as st
import plotly.express as px
from datetime import datetime
from pandas import DataFrame


class App:
    def __init__(self):

        self.api = \
            "64ZD6fQlOmudCB1z6jP5IrIdUTknLJC3uym7XFPqc6f71xhb5DiSL36rxZDW"
        self.addr = "http://localhost"
        self.port = 80
        self.svr = None
        self.u_df = None
        self.g_df = None
        self.users_data = None
        self.groups_data = None


        st.set_page_config(layout="wide", page_icon=":lock:",
                           page_title="Auth Server")
        self.status_bar = st.container()
        #self.status_header()
        self.main_win = st.container()
        self.sidebar()

    def sidebar(self):
        def is_valid():
            if self.addr and self.port and self.api:
                return True

        with st.sidebar.container():
            st.write("Auth Server")
            with st.sidebar.expander(label=":red[Server Connection]",
                                                   expanded=False):
                st.write("Server Address")
                self.addr = st.text_input("Address", value=self.addr)
                self.port = st.text_input("Port", value=self.port)
                self.api = st.text_input("API", value=self.api)
                if is_valid():
                    self.connect_button = st.button("Connect", key="connect",
                                                    on_click=self.connect)
                else:
                    self.connect_button = st.button("Connect", key="connect",
                                                    on_click=self.connect,
                                                    disabled=True)

        with st.sidebar.container():
            with st.sidebar.expander("User Options", expanded=False):
                test_container = st.container()
                with test_container:
                    st.header("Add User")
                    add_options = st.radio("Add", ["User", "Group"])

    def connect(self):
        self.svr = AuthServer(self.api, self.addr, self.port)
        if not self.svr:
            # self.conn_status.error("Connection Error", icon="⚠️")
            # self.conn_status.update(state="error")
            print("Connection Error")
        else:
            # self.conn_status.success("Connected", icon="👍")
            # self.conn_status.update(state="complete")
            self.users_data = self.svr.ops.get_users()
            self.groups_data = self.svr.ops.get_groups()
            self.u_df = DataFrame(self.users_data).transpose()
            self.g_df = DataFrame(self.groups_data).transpose()
            self.refresh()

    def show_users_groups(self):
            self.refresh_button = st.button("Refresh", key="refresh",
                                            on_click=self.refresh)
            self.users_container = st.container()
            with self.users_container:
                self.users_container.header("Users")
                self.users_container.write("Users Table")
                st.dataframe(self.u_df)

                charts_container = st.container()
                with charts_container:
                    col11, col21 = st.columns(2)
                    with col11:
                        st.header("Admins")
                        st.bar_chart(self.u_df["is_superuser"].value_counts(),
                                     use_container_width=True, y="count")
                    with col21:
                        st.header("Active")
                        active_pie_chart = px.pie(self.u_df, names="is_active",
                                                    title="Active Users")
                        st.plotly_chart(active_pie_chart,
                                        use_container_width=True,
                                                  sharing="streamlit",
                                                  theme="streamlit")

            self.groups_conatiner = st.container()
            with self.groups_conatiner:
                self.groups_conatiner.header("Groups")
                self.groups_conatiner.write("Groups Table")
                user_dframe = st.dataframe(self.g_df)

                self.group_drilldown = st.container()
                with self.group_drilldown:
                    self.group_drilldown.header("Group Drilldown")
                    self.g_dd_entry = st.selectbox("Select Group",
                                                   self.groups_data.keys())

                    with st.expander("Group Details", expanded=False):
                        try:
                            if self.groups_data[self.g_dd_entry]["is_superuser"]:
                                st.warning("Admin Group", icon="⚠️")
                        except KeyError:
                            pass
                        self.g_dd_details = st.dataframe(
                            self.g_df[self.g_df["name"] == self.g_dd_entry])
                        if self.groups_data[self.g_dd_entry]["users_obj"]:
                            st.write(f"'{self.g_dd_entry}' Users:")
                            g_df = DataFrame(self.groups_data)
                            g_df = g_df.transpose()
                            users = g_df[self.g_df["name"] ==
                                                   self.g_dd_entry]["users_obj"]
                            users = users.values[0]
                            users = {user["username"]: user for user in users}
                            users_df = DataFrame(users)
                            st.dataframe(users_df.transpose())
                        else:
                            st.write(f"'{self.g_dd_entry}' has no users")

    def refresh(self):
        self.refresh_status = st.status("Refreshing")
        with self.refresh_status:
            self.users_data = self.svr.ops.get_users()
            time = datetime.now().strftime("%d%b%Y - %H:%M:%S:%f %z")
            st.write(f"Users pulled - [{time}]")
            self.u_df = DataFrame(self.users_data)
            #self.u_df.drop("groups_obj", inplace=True)
            self.u_df = self.u_df.transpose()
            col_names = self.u_df.columns.tolist()
            col_names.remove("groups_obj")
            self.u_df = self.u_df[col_names]
            self.u_df["groups"] = self.u_df["groups"].apply(self.swap_guid_for_name)

            time = datetime.now().strftime("%d%b%Y - %H:%M:%S:%f %z")
            st.write(f"Users Dataframe updated - [{time}]")

            self.groups_data = self.svr.ops.get_groups()
            self.g_df = DataFrame(self.groups_data)
            self.g_df = self.g_df.transpose()
            col_names = self.g_df.columns.tolist()
            col_names.remove("users_obj")
            self.g_df = self.g_df[col_names]

            time = datetime.now().strftime("%d%b%Y - %H:%M:%S:%f %z")
            st.write(f"Groups pulled - [{time}]")
            st.write(f"Groups Dataframe updated - [{time}]")
        self.show_users_groups()

    def swap_guid_for_name(self, groups):
        if groups:
            for idx, guid in enumerate(groups):
                groups[idx] = self.svr.ops.get_group(guid)["name"]
        return groups

    @staticmethod
    def expand_groups_obj(groups_obj):
        if groups_obj:
            return [name for name in groups_obj.keys()]


if __name__ == "__main__":
    app = App()
