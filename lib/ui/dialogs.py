# lib/ui/dialogs.py
# Dialogs (confirm, error, info)

class Dialog:
    pass

def show_error(ctx, message):
    """Display a user-facing error message. For now, print to console; later, show on device display."""
    print(f"ERROR: {message}")
    # TODO: Implement on-device error dialog using ctx['display'] 