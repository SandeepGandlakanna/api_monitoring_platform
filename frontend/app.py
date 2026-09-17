import requests
import streamlit as st
import pandas as pd
import plotly.express as px


API_BASE_URL = "http://127.0.0.1:8000"


st.set_page_config(
    page_title="API Monitoring Platform",
    page_icon="📊",
    layout="wide",
)


st.sidebar.title("API Monitoring Platform")

st.sidebar.write(
    "Monitor your APIs and track their health, "
    "uptime, and response times."
)

st.sidebar.title("Navigation")

page = st.sidebar.radio(
    "Go to",
    [
        "Dashboard",
        "Monitors",
        "Login",
        "Register",
    ],
)



if "access_token" not in st.session_state:
    st.session_state["access_token"] = None

if "username" not in st.session_state:
    st.session_state["username"] = None



if st.session_state["access_token"]:

    st.sidebar.success(
        f"Logged in as "
        f"{st.session_state['username']}"
    )

    if st.sidebar.button("Logout"):

        st.session_state["access_token"] = None
        st.session_state["username"] = None

        st.rerun()



if page == "Register":

    st.header("Create an Account")

    st.write(
        "Register a new account to start monitoring APIs."
    )

    register_username = st.text_input(
        "Username",
        key="register_username",
    )

    register_email = st.text_input(
        "Email",
        key="register_email",
    )

    register_password = st.text_input(
        "Password",
        type="password",
        key="register_password",
    )

    register_confirm_password = st.text_input(
        "Confirm Password",
        type="password",
        key="register_confirm_password",
    )

    if st.button("Register"):

        if (
            not register_username
            or not register_email
            or not register_password
            or not register_confirm_password
        ):

            st.warning(
                "Please fill in all fields."
            )

        elif register_password != register_confirm_password:

            st.error(
                "Passwords do not match."
            )

        else:

            register_response = requests.post(
                f"{API_BASE_URL}/auth/register",
                json={
                    "username": register_username,
                    "email": register_email,
                    "password": register_password,
                },
            )

            if register_response.status_code in [200, 201]:

                st.success(
                    "Registration successful!"
                )

                st.info(
                    "You can now go to Login and "
                    "sign in with your account."
                )

            else:

                try:

                    error_detail = (
                        register_response.json()
                        .get(
                            "detail",
                            "Registration failed.",
                        )
                    )

                except Exception:

                    error_detail = (
                        "Registration failed."
                    )

                st.error(error_detail)


elif page == "Login":

    st.header("Login")

    username = st.text_input(
        "Username",
        key="login_username",
    )

    password = st.text_input(
        "Password",
        type="password",
        key="login_password",
    )

    if st.button("Login"):

        if not username or not password:

            st.warning(
                "Please enter username and password."
            )

        else:

            response = requests.post(
                f"{API_BASE_URL}/auth/login",
                json={
                    "username": username,
                    "password": password,
                },
            )

            if response.status_code == 200:

                data = response.json()

                st.session_state["access_token"] = (
                    data["access_token"]
                )

                st.session_state["username"] = (
                    data["username"]
                )

                st.success(
                    "Login successful!"
                )

                st.rerun()

            else:

                try:

                    error_detail = (
                        response.json()
                        .get(
                            "detail",
                            "Invalid username or password.",
                        )
                    )

                except Exception:

                    error_detail = (
                        "Invalid username or password."
                    )

                st.error(error_detail)



if page == "Dashboard":

    if not st.session_state["access_token"]:

        st.warning("Please login first.")

        st.stop()

    st.title("📊 Dashboard")

    headers = {
        "Authorization": (
            f"Bearer "
            f"{st.session_state['access_token']}"
        )
    }

    # --------------------------------------------------------
    # Dashboard Summary
    # --------------------------------------------------------

    summary_response = requests.get(
        f"{API_BASE_URL}/monitors/dashboard/summary",
        headers=headers,
    )

    if summary_response.status_code != 200:

        st.error(
            summary_response.json().get(
                "detail",
                "Unable to load dashboard.",
            )
        )

        st.stop()

    summary = summary_response.json()

    st.subheader("System Overview")

    col1, col2, col3, col4 = st.columns(4)

    with col1:

        st.metric(
            "Total Monitors",
            summary["total_monitors"],
        )

    with col2:

        st.metric(
            "Active Monitors",
            summary["active_monitors"],
        )

    with col3:

        st.metric(
            "Healthy Monitors",
            summary["healthy_monitors"],
        )

    with col4:

        st.metric(
            "Failing Monitors",
            summary["failing_monitors"],
        )

    # --------------------------------------------------------
    # Monitor Overview
    # --------------------------------------------------------

    st.subheader("Monitor Overview")

    monitors_response = requests.get(
        f"{API_BASE_URL}/monitors/",
        headers=headers,
    )

    if monitors_response.status_code != 200:

        st.error("Unable to load monitors.")

        st.stop()

    monitors = monitors_response.json()

    if not monitors:

        st.info(
            "No monitors found. "
            "Create a monitor first."
        )

        st.stop()

    overview_data = []

    for monitor in monitors:

        if monitor["last_is_success"] is True:

            status = "🟢 Healthy"

        elif monitor["last_is_success"] is False:

            status = "🔴 Failing"

        else:

            status = "⚪ Not Checked"

        overview_data.append(
            {
                "Name": monitor["name"],
                "URL": monitor["url"],
                "Status": status,
                "Status Code": (
                    monitor["last_status_code"]
                ),
                "Response Time (ms)": (
                    monitor[
                        "last_response_time_ms"
                    ]
                ),
                "Interval (sec)": (
                    monitor[
                        "check_interval_seconds"
                    ]
                ),
                "Active": monitor["is_active"],
            }
        )

    overview_df = pd.DataFrame(
        overview_data
    )

    st.dataframe(
        overview_df,
        use_container_width=True,
    )

    st.subheader("🚨 Alerts")

    alerts_response = requests.get(
        f"{API_BASE_URL}/monitors/alerts?unresolved_only=true",
        headers=headers,
    )

    if alerts_response.status_code == 200:

        alerts = alerts_response.json()

        if alerts:

            alert_data = []

            for alert in alerts:
                alert_data.append(
                    {
                        "Monitor ID": alert["monitor_id"],
                        "Message": alert["message"],
                        "Type": alert["alert_type"],
                        "Created At": alert["created_at"],
                    }
                )

            alerts_df = pd.DataFrame(alert_data)

            st.dataframe(
                alerts_df,
                use_container_width=True,
            )

        else:
            st.success("No active alerts 🎉")

    else:
        st.error("Unable to load alerts.")
# ============================================================
# MONITORS
# ============================================================

elif page == "Monitors":

    st.header("Monitors")

    if not st.session_state["access_token"]:

        st.warning(
            "Please login to view your monitors."
        )

    else:

        headers = {
            "Authorization": (
                "Bearer "
                + st.session_state["access_token"]
            )
        }

        # ----------------------------------------------------
        # Add New Monitor
        # ----------------------------------------------------

        with st.expander(
            "+ Add New Monitor"
        ):

            monitor_name = st.text_input(
                "Monitor Name"
            )

            monitor_url = st.text_input(
                "URL"
            )

            monitor_method = st.selectbox(
                "HTTP Method",
                [
                    "GET",
                    "POST",
                    "PUT",
                    "DELETE",
                ],
            )

            check_interval = st.number_input(
                "Check Interval (seconds)",
                min_value=10,
                value=60,
                step=10,
            )

            if st.button(
                "Create Monitor"
            ):

                if (
                    not monitor_name
                    or not monitor_url
                ):

                    st.warning(
                        "Please enter monitor name and URL."
                    )

                else:

                    create_response = requests.post(
                        f"{API_BASE_URL}/monitors/",
                        headers=headers,
                        json={
                            "name": monitor_name,
                            "url": monitor_url,
                            "method": monitor_method,
                            "check_interval_seconds": int(
                                check_interval
                            ),
                        },
                    )

                    if create_response.status_code in [
                        200,
                        201,
                    ]:

                        st.success(
                            "Monitor created successfully!"
                        )

                        st.rerun()

                    else:

                        try:

                            error_detail = (
                                create_response.json()
                                .get(
                                    "detail",
                                    "Failed to create monitor.",
                                )
                            )

                        except Exception:

                            error_detail = (
                                "Failed to create monitor."
                            )

                        st.error(
                            error_detail
                        )

        st.divider()

        # ----------------------------------------------------
        # Load Monitors
        # ----------------------------------------------------

        response = requests.get(
            f"{API_BASE_URL}/monitors/",
            headers=headers,
        )

        if response.status_code == 200:

            monitors = response.json()

            if not monitors:

                st.info(
                    "You don't have any monitors yet."
                )

            else:

                for monitor in monitors:

                    # ----------------------------------------
                    # Determine Status
                    # ----------------------------------------

                    if (
                        monitor["last_is_success"]
                        is True
                    ):

                        status = "🟢 Healthy"

                    elif (
                        monitor["last_is_success"]
                        is False
                    ):

                        status = "🔴 Failing"

                    else:

                        status = "⚪ Not checked yet"

                    if not monitor["is_active"]:

                        status = (
                            "⚫ Disabled"
                        )

                    st.subheader(
                        f"{status}  "
                        f"{monitor['name']}"
                    )

                    st.write(
                        f"**URL:** "
                        f"{monitor['url']}"
                    )

                    st.write(
                        f"**Method:** "
                        f"{monitor['method']}"
                    )

                    # ----------------------------------------
                    # Edit Monitor
                    # ----------------------------------------

                    with st.expander(
                        "Edit Monitor"
                    ):

                        edit_name = st.text_input(
                            "Monitor Name",
                            value=monitor["name"],
                            key=(
                                f"edit_name_"
                                f"{monitor['id']}"
                            ),
                        )

                        edit_url = st.text_input(
                            "URL",
                            value=monitor["url"],
                            key=(
                                f"edit_url_"
                                f"{monitor['id']}"
                            ),
                        )

                        edit_method = st.selectbox(
                            "HTTP Method",
                            [
                                "GET",
                                "POST",
                                "PUT",
                                "DELETE",
                            ],
                            index=[
                                "GET",
                                "POST",
                                "PUT",
                                "DELETE",
                            ].index(
                                monitor["method"]
                            ),
                            key=(
                                f"edit_method_"
                                f"{monitor['id']}"
                            ),
                        )

                        edit_interval = st.number_input(
                            "Check Interval (seconds)",
                            min_value=10,
                            value=monitor[
                                "check_interval_seconds"
                            ],
                            step=10,
                            key=(
                                f"edit_interval_"
                                f"{monitor['id']}"
                            ),
                        )

                        if st.button(
                            "Save Changes",
                            key=(
                                f"save_"
                                f"{monitor['id']}"
                            ),
                        ):

                            update_response = (
                                requests.put(
                                    f"{API_BASE_URL}/monitors/"
                                    f"{monitor['id']}",
                                    headers=headers,
                                    json={
                                        "name": edit_name,
                                        "url": edit_url,
                                        "method": edit_method,
                                        "check_interval_seconds": int(
                                            edit_interval
                                        ),
                                    },
                                )
                            )

                            if (
                                update_response.status_code
                                == 200
                            ):

                                st.success(
                                    "Monitor updated successfully!"
                                )

                                st.rerun()

                            else:

                                st.error(
                                    "Failed to update monitor."
                                )

                    # ----------------------------------------
                    # Metrics
                    # ----------------------------------------

                    col1, col2, col3 = st.columns(3)

                    with col1:

                        st.metric(
                            "Status Code",
                            (
                                monitor[
                                    "last_status_code"
                                ]
                                if monitor[
                                    "last_status_code"
                                ] is not None
                                else "N/A"
                            ),
                        )

                    with col2:

                        response_time = (
                            monitor[
                                "last_response_time_ms"
                            ]
                            if monitor[
                                "last_response_time_ms"
                            ]
                            is not None
                            else 0
                        )

                        st.metric(
                            "Response Time",
                            f"{response_time:.2f} ms",
                        )

                    with col3:

                        st.metric(
                            "Check Interval",
                            (
                                f"{monitor['check_interval_seconds']}"
                                " sec"
                            ),
                        )

                    # ----------------------------------------
                    # Enable / Disable Monitoring
                    # ----------------------------------------

                    st.write(
                        "### Monitoring Control"
                    )

                    if monitor["is_active"]:

                        if st.button(
                            "Disable Monitoring",
                            key=(
                                f"disable_"
                                f"{monitor['id']}"
                            ),
                        ):

                            update_response = (
                                requests.put(
                                    f"{API_BASE_URL}/monitors/"
                                    f"{monitor['id']}",
                                    headers=headers,
                                    json={
                                        "is_active": False
                                    },
                                )
                            )

                            if (
                                update_response.status_code
                                == 200
                            ):

                                st.success(
                                    "Monitoring disabled."
                                )

                                st.rerun()

                            else:

                                st.error(
                                    "Failed to disable monitoring."
                                )

                    else:

                        if st.button(
                            "Enable Monitoring",
                            key=(
                                f"enable_"
                                f"{monitor['id']}"
                            ),
                        ):

                            update_response = (
                                requests.put(
                                    f"{API_BASE_URL}/monitors/"
                                    f"{monitor['id']}",
                                    headers=headers,
                                    json={
                                        "is_active": True
                                    },
                                )
                            )

                            if (
                                update_response.status_code
                                == 200
                            ):

                                st.success(
                                    "Monitoring enabled."
                                )

                                st.rerun()

                            else:

                                st.error(
                                    "Failed to enable monitoring."
                                )

                    # ----------------------------------------
                    # Delete Monitor
                    # ----------------------------------------

                    if st.button(
                        "Delete Monitor",
                        key=(
                            f"delete_"
                            f"{monitor['id']}"
                        ),
                    ):

                        delete_response = (
                            requests.delete(
                                f"{API_BASE_URL}/monitors/"
                                f"{monitor['id']}",
                                headers=headers,
                            )
                        )

                        if (
                            delete_response.status_code
                            == 200
                        ):

                            st.success(
                                "Monitor deleted successfully!"
                            )

                            st.rerun()

                        else:

                            st.error(
                                "Failed to delete monitor."
                            )

                    # ----------------------------------------
                    # Monitoring History
                    # ----------------------------------------

                    history_response = requests.get(
                        f"{API_BASE_URL}/monitors/"
                        f"{monitor['id']}/history",
                        headers=headers,
                    )

                    if history_response.status_code == 200:

                        history = (
                            history_response.json()
                        )

                        if history:

                            successful_checks = sum(
                                1
                                for result in history
                                if result[
                                    "is_success"
                                ] is True
                            )

                            total_checks = len(
                                history
                            )

                            if total_checks > 0:

                                uptime_percentage = (
                                    successful_checks
                                    / total_checks
                                ) * 100

                            else:

                                uptime_percentage = 0

                            st.metric(
                                "Historical Uptime",
                                (
                                    f"{uptime_percentage:.2f}%"
                                ),
                            )

                            history_data = (
                                pd.DataFrame(
                                    history
                                )
                            )

                            history_data[
                                "checked_at"
                            ] = pd.to_datetime(
                                history_data[
                                    "checked_at"
                                ]
                            )

                            st.subheader(
                                "Response Time History"
                            )

                            chart = px.line(
                                history_data,
                                x="checked_at",
                                y="response_time_ms",
                                markers=True,
                                labels={
                                    "checked_at": "Time",
                                    "response_time_ms": (
                                        "Response Time (ms)"
                                    ),
                                },
                            )

                            st.plotly_chart(
                                chart,
                                use_container_width=True,
                            )

                        else:

                            st.info(
                                "No monitoring history "
                                "available yet."
                            )

                    else:

                        st.error(
                            "Failed to load monitoring history."
                        )

                    st.divider()

        else:

            st.error(
                "Failed to load monitors."
            )