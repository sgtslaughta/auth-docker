import time

import pandas as pd
import re
import streamlit as st
import plotly.express as px
from datetime import datetime
from time import sleep
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

        # self.sidebar()
        if self.svr:
            self.users_data = self.svr.ops.get_users()
            self.groups_data = self.svr.ops.get_groups()
            self.u_df = DataFrame(self.users_data).transpose()
            self.g_df = DataFrame(self.groups_data).transpose()

            if self.u_df.empty or self.g_df.empty:
                self.status.error("Unable to retrieve data", icon="👎")
                st.write("Unable to retrieve data")
            else:
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
        def is_valid_email(email):
            pattern = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
            return re.match(pattern, email) is not None
        def create_user(uname, name, email, pw):
            if self.svr and uname and name:
                # validate email
                if not email:
                    email = None
                else:
                    if is_valid_email(email):
                        pass
                    else:
                        st.error("Invalid Email")
                        return
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
                        self.status.success("User Removed from Group",
                                            icon="👍")

        def add_group(group, parent, admin):
            if self.svr and group:
                if parent:
                    p_gid = self.svr.ops.get_group(group_name=parent)["pk"]
                else:
                    p_gid = None
                rtn = self.svr.ops.add_group(group_name=group,
                                             parent_group=p_gid,
                                             is_superuser=admin)
                if rtn:
                    self.status.success("Group Added", icon="👍")
                    self.refresh()

        def remove_group(group):
            if self.svr and group:
                rtn = self.svr.ops.delete_group(group_name=group)
                if rtn is None:
                    self.status.success("Group Removed", icon="👍")

        def edit_user_func(uname, name, email, active):
            if self.svr and uname:
                rtn = self.svr.ops.edit_user(user_name=uname,
                                             display_name=name,
                                             email=email,
                                             is_active=active)
                if rtn:
                    self.status.success("User Edited", icon="👍")
                    self.refresh()

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

            with st.expander("Edit User", expanded=False):
                edit_u_col1, edit_u_col2 = st.columns(2)
                with edit_u_col1:
                    st.write("Edit User")
                    edit_user_sel = st.selectbox("Select User",
                                             self.u_df["username"].tolist(),
                                             key="edit_user")
                    edit_name = st.text_input("Name",
                                              key="edit_name",
                                              value=self.u_df.loc[
                                                  edit_user_sel, 'name'])
                    edit_email = st.text_input("Email",
                                               key="edit_email",
                                               value=self.u_df.loc[
                                                   edit_user_sel, "email"])
                    edit_active = st.checkbox("Active",
                                              key="edit_active",
                                              value=self.users_data[
                                                  edit_user_sel]["is_active"])
                    edit_user_button = st.button("Edit User",
                                                 on_click=
                                                 lambda: edit_user_func(
                                                     edit_user_sel,
                                                     edit_name,
                                                     edit_email,
                                                     edit_active))

                with edit_u_col2:
                    st.write("Change Password")
                    with st.form(key="edit_user_form2", clear_on_submit=True):
                        edit_user = st.selectbox("Select User",
                                                 self.u_df[
                                                     "username"].tolist(),
                                                 key="edit_user2")
                        chg_pw = st.text_input("Change Password",
                                               key="chg_pw",
                                               type="password")
                        chg_pw_2 = st.text_input("Confirm Password",
                                                 key="chg_pw_2",
                                                 type="password")
                        chg_pw_button = st.form_submit_button("Set Password")
                        if chg_pw_button:
                            if not chg_pw or not chg_pw_2:
                                st.error("Passwords cannot be blank")
                            else:
                                if chg_pw != chg_pw_2:
                                    st.error("Passwords do not match")
                                else:
                                    rtn = self.svr.ops.set_password(
                                        user_name=edit_user,
                                        password=chg_pw)
                                    st.success("Password Changed",
                                               icon="👍")

            ### User Charts ###
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

            with st.expander("Add/Remove Group", expanded=False):
                add_g_col, rm_g_col = st.columns(2)
                with add_g_col:
                    st.write("Add Group")
                    with st.form(key="add_group_form", clear_on_submit=True):
                        add_group_entry = st.text_input("Group Name",
                                                        key="add_group_entry")
                        add_group_parent = st.multiselect("Parent Group",
                                                        self.g_df[
                                                            "name"].tolist(),
                                                        key="add_group_parent",
                                                          max_selections=1)
                        add_group_admin = st.checkbox("Admin Group",
                                                      key="add_group_admin")
                        add_group_button = st.form_submit_button("Add Group")
                        if add_group_button:
                            if not add_group_parent:
                                add_group_parent = ""
                            else:
                                add_group_parent = add_group_parent[0]
                            add_group(add_group_entry, add_group_parent,
                                      add_group_admin)
                            time.sleep(1)
                            self.refresh()

                with rm_g_col:
                    st.write("Remove Group")
                    rm_group_entry = st.selectbox("Select Group",
                                                  self.g_df["name"].tolist(),
                                                  key="rm_group_entry")
                    rm_group_button = st.button("Delete Group",
                                                key="rm_group_button",
                                                on_click=lambda: remove_group(
                                                    rm_group_entry))

            explode = self.g_df.explode("users")
            grouped = explode.groupby("name").count()
            groups_by_user_count = px.scatter(grouped,
                                              x=grouped.index,
                                              y=grouped["users"],
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

                    g_df = DataFrame(self.groups_data)
                    g_df = g_df.transpose()
                    users = g_df[self.g_df["name"] ==
                                 self.g_dd_entry]["users_obj"]
                    users = users.values[0]
                    users = {user["username"]: user for user in users}
                    if self.groups_data[self.g_dd_entry]["users_obj"]:
                        st.write(f"'{self.g_dd_entry}' Users:")

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
            if "groups_obj" in col_names:
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
            if "users_obj" in col_names:
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
