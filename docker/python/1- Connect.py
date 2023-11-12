from lib.auth_svr import AuthServer
import streamlit as st


class App:
    def __init__(self):
        self.api = "64ZD6fQlOmudCB1z6jP5IrIdUTknLJC3uym7XFPqc6f71xhb5DiSL36rxZDW"
        self.addr = "http://localhost"
        self.port = 80
        st.set_page_config(layout="wide", page_icon=":lock:",
                           page_title="Home")

        self.main()

    def main(self):
        def is_valid(addr, port, api):
            valid = True
            if not addr or not port or not api:
                return False
            # if "http://" not in addr or "https://" not in addr:
            #     print("Invalid Address")
            #     valid = False
            if port and port.isdigit():
                if not 0 < int(port) < 65535:
                    print("Invalid Port")
                    valid = False
            else:
                print("Invalid Port")
                valid = False
            if len(api) != 60:
                valid = False
            return valid

        st.write("Connection Details")
        main_win = st.container()
        with main_win:
            common_addrs = "http://localhost"
            addr = st.text_input("Address", value=self.addr,
                                 autocomplete=common_addrs,
                                 help="The address of the Authentik server",
                                 placeholder="Ex: http://localhost")
            common_ports = "80"
            port = st.text_input("Port", value=self.port,
                                 autocomplete=common_ports,
                                 help="The port of the Authentik server",
                                 placeholder="Ex: 80",
                                 max_chars=5)
            api = st.text_input("API Key", placeholder="Your Authentik API Key",
                                max_chars=60, type="password")
            if is_valid(addr, port, api):
                st.button("Connect", key="connect",
                          on_click=lambda: self.connect(addr, port, api))
            else:
                st.button("Connect", key="connect", disabled=True)

    def connect(self, addr, port, api):
        self.api = api
        self.addr = addr
        self.port = port
        st.session_state["svr"] = AuthServer(api, addr, port)
        if not st.session_state["svr"]:
            st.error("Connection Error", icon="⚠️")
        else:
            st.success("Connected", icon="👍")


if __name__ == "__main__":
    app = App()
