import os
import sys
import time
import threading
import webbrowser
import urllib.request
import urllib.error

import uvicorn

from backend.server import app


# ============================================================
# PATHS
# ============================================================

if getattr(sys, "frozen", False):
    BASE_DIR = sys._MEIPASS
else:
    BASE_DIR = os.path.dirname(
        os.path.abspath(__file__)
    )


FRONTEND_DIST = os.path.join(
    BASE_DIR,
    "frontend",
    "dist"
)


# ============================================================
# CHECK FRONTEND
# ============================================================

def check_frontend():

    index_file = os.path.join(
        FRONTEND_DIST,
        "index.html"
    )

    if not os.path.exists(index_file):

        print()
        print("ERROR: React frontend was not found.")
        print()
        print("Expected:")
        print(index_file)
        print()

        return False

    print("✓ Frontend found")

    return True


# ============================================================
# WAIT FOR SERVER
# ============================================================

def wait_for_server():

    url = "http://127.0.0.1:8000/health"

    print()
    print("Waiting for NOVA backend...")

    for attempt in range(30):

        try:

            with urllib.request.urlopen(
                url,
                timeout=1
            ) as response:

                if response.status == 200:

                    print("✓ NOVA backend online")

                    return True

        except (
            urllib.error.URLError,
            ConnectionError,
            TimeoutError
        ):

            pass

        time.sleep(0.25)


    print()
    print("ERROR: NOVA backend did not start.")
    print()

    return False


# ============================================================
# OPEN BROWSER
# ============================================================

def open_browser():

    if wait_for_server():

        time.sleep(0.5)

        webbrowser.open(
            "http://127.0.0.1:8000"
        )


# ============================================================
# MAIN
# ============================================================

def main():

    print()
    print("========================================")
    print("             N O V A")
    print("       PERSONAL AI ASSISTANT")
    print("========================================")
    print()


    # --------------------------------------------------------
    # Check frontend
    # --------------------------------------------------------

    if not check_frontend():

        input(
            "Press Enter to exit..."
        )

        return


    # --------------------------------------------------------
    # Start browser watcher
    # --------------------------------------------------------

    browser_thread = threading.Thread(
        target=open_browser,
        daemon=True
    )

    browser_thread.start()


    # --------------------------------------------------------
    # Start FastAPI
    # --------------------------------------------------------

    print()
    print("Starting NOVA backend...")
    print()

    print(
        "Server:"
    )

    print(
        "http://127.0.0.1:8000"
    )

    print()


    try:

        uvicorn.run(

            app,

            host="127.0.0.1",

            port=8000,

            reload=False

        )


    except Exception as error:

        print()
        print("========================================")
        print("NOVA FAILED TO START")
        print("========================================")
        print()

        print("Error:")
        print(error)

        print()

        input(
            "Press Enter to exit..."
        )


# ============================================================
# START
# ============================================================

if __name__ == "__main__":

    main()