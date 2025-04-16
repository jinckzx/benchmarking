# from llm_consortium.ui.app import create_ui
# from llm_consortium.core.logging import configure_logging

# configure_logging()
# if __name__ == "__main__":
#     ui = create_ui()
#     ui.launch()





import subprocess
from llm_consortium.utils.logging import configure_logging

configure_logging()

if __name__ == "__main__":
    # Adjust the path to app.py if necessary.
    subprocess.run(["streamlit", "run", "app.py"])
