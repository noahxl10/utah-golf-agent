# import signal
# import sys

# _exit_hooks = []

# def register_exit(func):
#     """Register a function to run on process exit"""
#     _exit_hooks.append(func)

# def run_exit_hooks(*args):
#     """Run all registered exit hooks"""
#     for func in _exit_hooks:
#         try:
#             func()
#         except Exception as e:
#             print("Error in exit hook:", e)
#     sys.exit(0)

# # Hook into SIGINT (Ctrl+C) and SIGTERM
# signal.signal(signal.SIGINT, run_exit_hooks)
# signal.signal(signal.SIGTERM, run_exit_hooks)
