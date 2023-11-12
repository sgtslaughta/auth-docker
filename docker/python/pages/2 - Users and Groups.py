import pandas as pd
import streamlit as st
import plotly.express as px
from datetime import datetime
from pandas import DataFrame


class UsersGroups:
    def __init__(self):
        try:
            self.svr = st.session_state["svr"]
        except KeyError:
            self.svr = None
        self.u_df = None
        self.g_df = None
        self.users_data = None
        self.groups_data = None

        st.set_page_config(layout="wide", page_icon=":lock:",
                           page_title="Auth Server")
        self.status = st.status(label="Waiting for connection...",
                                state='running',
                                expanded=False)

        #self.sidebar()
        if self.svr:
            self.users_data = self.svr.ops.get_users()
            self.groups_data = self.svr.ops.get_groups()
            self.u_df = DataFrame(self.users_data).transpose()
            self.g_df = DataFrame(self.groups_data).transpose()
            self.refresh()
            self.show_users_groups()

    def sidebar(self):
        with st.sidebar.container():
            st.write("Auth Server")

        with st.sidebar.container():
            with st.sidebar.expander("User Options", expanded=False):
                test_container = st.container()
                with test_container:
                    st.header("Add User")
                    add_options = st.radio("Add", ["User", "Group"])

    def show_users_groups(self):
        def create_user(uname, name, email, pw):
            if self.svr and uname and name and email and pw:
                rtn = self.svr.ops.add_user(username=uname,
                                            display_name=name,
                                            email=email,
                                            password=pw)
                st.session_state["add_user"] = ""
                st.session_state["add_name"] = ""
                st.session_state["add_email"] = ""
                st.session_state["add_pw"] = ""
                if rtn:
                    self.status.success("User Added", icon="👍")

        def remove_user(uname):
            if self.svr and uname:
                rtn = self.svr.ops.delete_user(username=uname)
                st.session_state["del_user"] = ""
                if rtn is None:
                    self.status.success("User Removed", icon="👍")

        def add_user_to_group(users, group):
            if self.svr and users and group:
                for user in users:
                    rtn = self.svr.ops.add_user_to_group(user_name=user,
                                                         group_name=group)
                    st.session_state["add_guser"] = ""
                    if 'error' not in rtn.keys():
                        self.status.success("User Added to Group", icon="👍")

        def rem_users_from_group(users, group):
            if self.svr and users and group:
                for user in users:
                    rtn = self.svr.ops.remove_user_from_group(user_name=user,
                                                              group_name=group)
                    st.session_state["rem_guser"] = ""
                    if 'error' not in rtn.keys():
                        self.status.success("User Removed from Group", icon="👍")

        self.refresh_button = st.button("Refresh",
                                        on_click=self.refresh)
        self.users_container = st.container()
        with self.users_container:
            self.users_container.header("Users")
            self.users_container.write("Users Table")
            st.dataframe(self.u_df)
            with st.expander("Add/Remove User", expanded=False):
                add_user_col, remove_user_col = st.columns(2)
                with add_user_col:
                    st.write("Add User")
                    add_user = st.text_input("Username", key="add_user")
                    add_name = st.text_input("Name", key="add_name")
                    add_email = st.text_input("Email", key="add_email")
                    add_pw = st.text_input("Password", key="add_pw",
                                           type="password")
                    add_user_button = st.button("Add User",
                                                on_click=
                                                lambda: create_user(add_user,
                                                                 add_name,
                                                                 add_email,
                                                                 add_pw))
                with remove_user_col:
                    st.write("Remove User")
                    del_user = st.text_input("Username", key="del_user")
                    del_user_button = st.button("Remove User",
                                                on_click=
                                                lambda: remove_user(
                                                    del_user))

            charts_container = st.container()
            with charts_container:
                col11, col21 = st.columns(2)
                with col11:
                    st.header("Admins to Regular Users")
                    admin_pie_chart = px.pie(self.u_df, names="is_superuser",
                                                title="Admins to Regular Users")
                    admin_pie_chart.update_traces(textposition='inside',
                                                  textinfo='percent+label+value')
                    st.plotly_chart(admin_pie_chart,
                                    use_container_width=True,
                                    sharing="streamlit",
                                    theme="streamlit")
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

            explode = self.g_df.explode("users")
            grouped = explode.groupby("name").count()
            groups_by_user_count = px.scatter(grouped,
                                              x=grouped.index,
                                              y=[1] * len(grouped),
                                              title="Groups by User Count",
                                              size='users',
                                              labels={
                                                  'Users': 'Number of Users'})
            st.plotly_chart(groups_by_user_count,
                            use_container_width=True,
                            sharing="streamlit")

            self.group_drilldown = st.container()
            with self.group_drilldown:
                self.group_drilldown.header("Group Drilldown")
                self.g_dd_entry = st.selectbox("Select Group",
                                               self.groups_data.keys())

                with st.expander("Group Details", expanded=True):
                    try:
                        if self.groups_data[self.g_dd_entry]["is_superuser"]:
                            st.warning("Admin Group", icon="⚠️")
                    except KeyError:
                        pass
                    self.g_dd_details = st.dataframe(
                        self.g_df[self.g_df["name"] == self.g_dd_entry])
                    users_not_in_group = []
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

                        for user in self.users_data:
                            if user not in users.keys():
                                users_not_in_group.append(user)

                    else:
                        st.write(f"'{self.g_dd_entry}' has no users")
                        for i in self.users_data.keys():
                            users_not_in_group.append(i)
                    add_col, rem_col = st.columns(2)
                    with add_col:
                        st.write(f"Add user to: '{self.g_dd_entry}'")
                        g_add_user = st.multiselect("Select Users to Add",
                                                    users_not_in_group)
                        add_guser_button = st.button("Add User to group",
                                                     key="add_guser_button",
                                                     on_click=
                                                     lambda: add_user_to_group(
                                                         g_add_user,
                                                         self.g_dd_entry))
                    with rem_col:
                        st.write(f"Remove user from: '{self.g_dd_entry}'")
                        g_rem_user = st.multiselect("Select Users to Remove",
                                                    users.keys())
                        rem_guser_button = st.button("Remove User from group",
                                                     key="rem_guser_button",
                                                     on_click=
                                                     lambda:
                                                     rem_users_from_group(
                                                         g_rem_user,
                                                         self.g_dd_entry))

    def refresh(self):
        self.status.update(label="Refreshing", state="running")
        with self.status:
            self.users_data = self.svr.ops.get_users()
            time = datetime.now().strftime("%d%b%Y - %H:%M:%S:%f %z")
            st.write(f"Users pulled - [{time}]")
            self.u_df = DataFrame(self.users_data)
            # self.u_df.drop("groups_obj", inplace=True)
            self.u_df = self.u_df.transpose()
            col_names = self.u_df.columns.tolist()
            col_names.remove("groups_obj")
            self.u_df = self.u_df[col_names]
            self.u_df["groups"] = self.u_df["groups"].apply(
                self.swap_guid_for_name)

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
        self.status.update(label="Done", state="complete")

    def swap_guid_for_name(self, groups):
        if groups:
            for idx, guid in enumerate(groups):
                groups[idx] = self.svr.ops.get_group(guid)["name"]
        return groups

    @staticmethod
    def expand_groups_obj(groups_obj):
        if groups_obj:
            return [name for name in groups_obj.keys()]


ug = UsersGroups()
