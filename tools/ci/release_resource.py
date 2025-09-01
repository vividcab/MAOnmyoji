from install import install_resource, install_chores, install_agent, install_path


if __name__ == "__main__":
    install_resource()
    install_chores()
    install_agent()

    print(f"Install to {install_path} successfully.")
