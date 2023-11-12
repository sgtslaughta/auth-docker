from lib.auth_api import api_get, api_post, api_delete
import json
import secrets
import string


class AuthServer:
    def __init__(self, api_key: str, svr_addr: str, svr_port: int = None):
        self.api_key = None
        self.svr_addr = None
        self.svr_port = None
        self.curr_rqst_path = None
        self.verify_ssl = True
        self.users = {}
        self.groups = {}
        self.ops = AuthOperations(self)
        self.set_api_key(api_key)
        self.set_svr_addr(svr_addr)
        self.set_svr_port(svr_port)

    def set_api_key(self, api_key: str):
        if len(api_key) != 60:
            print("The API key must be 60 characters long.")
            return
        self.api_key = api_key

    def set_svr_addr(self, svr_addr: str):
        if 'http://' in svr_addr or 'https://' in svr_addr:
            self.svr_addr = svr_addr.rstrip('/')
        else:
            print("The server address must start with http:// or https://")
            return

    def set_svr_port(self, svr_port):
        if svr_port is None:
            self.svr_port = ''
        else:
            try:
                self.svr_port = int(svr_port)
            except ValueError:
                print("The server port must be an integer.")
                return

    def make_get_call(self, api_rqst: str):
        self.curr_rqst_path = api_rqst
        return api_get(self.api_key, self.svr_addr, api_rqst,
                       self.svr_port, self.verify_ssl)


class AuthOperations:
    def __init__(self, svr: AuthServer):
        self.svr = svr

    @staticmethod
    def generate_password(length=18, punctuation='!@#$%_-') -> str:
        """
        This function will generate a random password
        :param length: Int containing the length of the password
        :param punctuation: String containing the punctuation to use
        :return: String containing the password
        """
        alphabet = string.ascii_letters + string.digits + punctuation
        password = ''.join(secrets.choice(alphabet) for _ in range(length))
        return password

    def get_metrics(self) -> dict:
        """
        This function will get the metrics from the server
        :return: Dict containing the metrics
        """
        return self.svr.make_get_call('/admin/metrics/')

    def get_users(self) -> dict:
        """
        This function will get all users from the server
        :return: Dict containing all users
        """
        self.svr.users = self.svr.make_get_call('/core/users/')
        users = {}
        try:
            for item in self.svr.users['results']:
                users[item['username']] = item
        except KeyError:
            return {'error': 'No users found'}
        return users

    def get_user(self, user_id: int = None, username: str = None):
        """
        This function will get a user from the server using either the user ID
        or username
        :param user_id:
        :param username:
        :return:
        """
        if user_id is None and username is None:
            print("You must specify either a user ID or name.")
            return
        if user_id is None:
            users = self.get_users()
            if username in users:
                user_id = users[username]['pk']
            if user_id is None:
                print(f"The user '{username}' does not exist.")
                return
        return self.svr.make_get_call(f'/core/users/{user_id}/')

    def get_user_groups(self, user_id: int = None, username: str = None):
        """
        This function will get all groups for a user
        :param user_id:
        :param username:
        :return:
        """
        if user_id is None and username is None:
            print("You must specify either a user ID or name.")
            return
        users_groups = {}
        if user_id is None:
            users = self.get_users()
            if username in users:
                user_id = users[username]['pk']
            if user_id is None:
                print(f"The user '{username}' does not exist.")
                return
        groups = self.get_groups()
        for group in groups:
            if user_id in groups[group]['users']:
                users_groups[group] = groups[group]
        return users_groups

    def get_groups(self):
        self.svr.groups = self.svr.make_get_call('/core/groups/')
        groups = {}
        for item in self.svr.groups['results']:
            groups[item['name']] = item
        return groups

    def get_roles(self):
        roles = self.svr.make_get_call('/rbac/roles/')
        role_dict = {}
        for item in roles['results']:
            try:
                role_dict[item['name']] = dict(item)
            except [KeyError, TypeError]:
                pass
        return role_dict

    def get_role(self, role_id: int = None, role_name: str = None):
        if role_id is None and role_name is None:
            print("You must specify either a role ID or name.")
            return
        if role_id is not None:
            return self.svr.make_get_call(f'/rbac/roles/{role_id}/')
        else:
            roles = self.get_roles()
            if role_name in roles:
                return roles[role_name]
            print(f"The role '{role_name}' does not exist.")
            return

    def get_group(self, group_id: int = None, group_name: str = None):
        if group_id is None and group_name is None:
            print("You must specify either a group ID or name.")
            return
        if group_id is not None:
            return self.svr.make_get_call(f'/core/groups/{group_id}/')
        else:
            groups = self.get_groups()
            if group_name in groups:
                return groups[group_name]
            print(f"The group '{group_name}' does not exist.")
            return

    def get_group_users(self, group_id: int = None, group_name: str = None):
        if group_id is None and group_name is None:
            print("You must specify either a group ID or name.")
            return
        if group_id is None:
            group = self.get_group(group_name=group_name)
        else:
            group = self.get_group(group_id=group_id)
        if group is None:
            print(f"The group '{group_name}' does not exist.")
            return
        users = {}
        for item in group['users']:
            user = self.get_user(user_id=item)
            users[user['username']] = user
        return users

    def add_user_to_group(self, user_id: int = None, group_id: int = None,
                          group_name: str = None, user_name: str = None):
        if user_id is None and user_name is None or group_id is None and \
                group_name is None:
            print("You must specify either a user ID or name and a group ID "
                  "or name.")
            return {'error': 'You must specify either a user ID or name and a '
                             'group ID or name.'}
        if user_id is None:
            user = self.get_user(username=user_name)
            user_id = user['pk']
        if group_id is None:
            group = self.get_group(group_name=group_name)
            group_id = group['pk']
        data = {
            "pk": user_id
        }
        data = json.dumps(data)
        rtn = api_post(self.svr.api_key, data, self.svr.svr_addr,
                          f'/core/groups/{group_id}/add_user/',
                          self.svr.svr_port,
                          self.svr.verify_ssl)
        return rtn

    def remove_user_from_group(self, user_id: int = None, group_id: int = None,
                               group_name: str = None, user_name: str = None):
        if user_id is None and user_name is None or group_id is None and group_name is None:
            print(
                "You must specify either a user ID or name and a group ID or name.")
            return
        if user_id is None:
            user = self.get_user(username=user_name)
            user_id = user['pk']
        if group_id is None:
            group = self.get_group(group_name=group_name)
            group_id = group['pk']
        data = {
            "pk": user_id
        }
        data = json.dumps(data)
        rtn = api_post(self.svr.api_key, data, self.svr.svr_addr,
                       f'/core/groups/{group_id}/remove_user/',
                       self.svr.svr_port,
                       self.svr.verify_ssl)
        return rtn

    def add_group(self, group_name: str, is_superuser: bool = False,
                  parent_group: int = None,
                  users: list = None,
                  attributes: dict = None,
                  roles: list = None) -> dict:
        groups = self.get_groups()
        if group_name in groups:
            print(f"The group '{group_name}' already exists.")
            return {}
        data = {
            "name": group_name,
            "is_superuser": is_superuser,
        }
        if parent_group is not None:
            parent = self.get_group(group_id=parent_group)
            if parent is None:
                print(f"The parent group '{parent_group}' does not exist.")
                return {}
            data['parent'] = parent_group
        if users is not None:
            grp_users = self.get_users()
            for item in users:
                if item not in grp_users:
                    print(f"The user '{item}' does not exist.")
                    return {}
            data['users'] = users
        if attributes is not None:
            data['attributes'] = attributes
        if roles is not None:
            grp_roles = self.get_roles()
            for item in roles:
                if item not in grp_roles:
                    print(f"The role '{item}' does not exist.")
                    return {}
            data['roles'] = roles
        data = json.dumps(data)
        data = api_post(self.svr.api_key, data, self.svr.svr_addr,
                        '/core/groups/', self.svr.svr_port,
                        self.svr.verify_ssl)
        return data

    def set_password(self, user_id: int, password: str):
        data = {
            "password": password
        }
        data = json.dumps(data)
        api_post(self.svr.api_key, data, self.svr.svr_addr,
                 f'/core/users/{user_id}/set_password/',
                 self.svr.svr_port, self.svr.verify_ssl)

    def add_user(self, username: str, display_name: str,
                 email: str, is_active: bool = True,
                 password: str = None, groups: list = None,
                 attributes: dict = None, path: str = None,
                 type: str = 'internal') -> dict:
        """
        A function to create a new user
        :param username: A unique username (1-150 char). If not unique,
        an empty dictionary will be returned.
        :param display_name: A display name for the user
        :param email: A unique email address. If not unique, an empty
        dictionary will be returned.
        :param is_active: Whether the user is active or not
        :param password: Can be none, in which case a random password will be
        generated and returned in the response under key 'password'
        :param groups: A list of the group ID in which the user should be
        added. If the group does not exist, an empty dictionary will be
        returned.
        :param attributes: { [any-key]: any }
        :param path: Must be at least 1 character long
        :param type: Allowed: internal┃external┃service_account┃
        internal_service_account
        :return:
        """
        users = self.get_users()
        svr_groups = self.get_groups()
        # Validate the provided information
        if username in users:
            return {'error': 'The user already exists.'}
        if any(email == item['email'] for item in users.values()):
            return {'error': 'The email is already in use.'}
        # if groups is not None:
        #     for group in groups:
        #         if not any(group == item['pk'] for item in
        #                    svr_groups['results']):
        #             return {}
        if 1 < len(username) > 150:
            return {'error': 'The username must be between 1 and 150 '}
        data = {
            "username": username,
            "name": display_name,
            "email": email,
            "is_active": is_active,
            "type": type
        }
        if groups is not None:
            data['groups'] = groups
        if attributes is not None:
            data['attributes'] = attributes
        if path is not None:
            data['path'] = path

        data = json.dumps(data)
        data = api_post(self.svr.api_key, data, self.svr.svr_addr,
                        '/core/users/', self.svr.svr_port,
                        self.svr.verify_ssl)
        if data:
            if password is None:
                password = self.generate_password()
            self.set_password(user_id=data['pk'], password=password)
            data['password'] = password
        return data

    def delete_user(self, user_id: int = None, username: str = None):
        if user_id is None and username is None:
            print("You must specify either a user ID or name.")
            return
        if user_id is None:
            user = self.get_user(username=username)
            user_id = user['pk']
        return api_delete(self.svr.api_key, self.svr.svr_addr,
                          f'/core/users/{user_id}/', self.svr.svr_port,
                          self.svr.verify_ssl)

    def delete_group(self, group_id: int, group_name: str = None):
        if group_id is None and group_name is None:
            print("You must specify either a group ID or name.")
            return
        if group_id is None:
            group = self.get_group(group_name=group_name)
            group_id = group['pk']
        return api_delete(self.svr.api_key, self.svr.svr_addr,
                          f'/core/groups/{group_id}/', self.svr.svr_port,
                          self.svr.verify_ssl)

    def get_svr_data(self):
        data = {}
        data['logins'] = self.svr.make_get_call('/admin/metrics/')
        data['system'] = self.svr.make_get_call('/admin/system/')
        data['version'] = self.svr.make_get_call('/admin/version/')
        data['apps'] = self.svr.make_get_call('/core/applications/')
        data['tasks'] = self.svr.make_get_call('/admin/system_tasks/')
        data['sessions'] = self.svr.make_get_call('/core/authenticated_sessions/')
        return data
