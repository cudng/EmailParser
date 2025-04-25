from email_validator import validate_email, EmailNotValidError
import re
from flet import ControlEvent


DATE_REGEX = re.compile(
        r"^(0[1-9]|[12][0-9]|3[01])-(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)-\d{4}$"
    )


def on_change(e: ControlEvent):
    cleaned = re.sub(r'[^\x00-\x7F]', '', e.control.value)
    if e.control.value != cleaned:
        e.control.value = cleaned
        e.control.update()


def validate(email: str) -> dict:
    """
    Validates the email address.
    Returns a dictionary with 'valid' (bool) and 'message' (str).
    """
    try:
        # Will raise EmailNotValidError if invalid
        validate_email(email)
        return {"valid": True}
    except EmailNotValidError as e:
        return {"valid": False, "message": str(e)}


def auto_format_and_validate_date_input(e: ControlEvent):
    """
    Automatically formats and validates a date entered in a TextField as you type.

    This function:
    - Automatically inserts '-' after the day (2 digits)
      and again after the month (3 letters) when appropriate.
    - Waits until the complete input (11 characters for "DD-MMM-YYYY") is entered
      before showing an error message.
    - Uses a regex (DATE_REGEX) to validate the full date format.

    :param e: The ControlEvent from a Flet TextField (triggered on change).
    """
    text = e.control.value.strip()

    # Auto-insert hyphen after the day part:
    # If the user has entered exactly 2 characters (day) and there's no '-' yet, append it.
    if len(text) == 2 and not text.endswith("-"):
        text += "-"
        e.control.value = text  # update the value immediately

    # -------------------------------
    # Auto-insert hyphen after the month part:
    # After the day and hyphen, the user should type 3 letters for the month.
    # When the total length reaches 6 (e.g., "01Jan") and the hyphen is missing,
    # insert a hyphen at the 5th index (position 6) so that the text becomes "01-Jan".
    if len(text) == 6 and text[5] != "-":
        text = text[:6] + "-" + text[6:]
        e.control.value = text

    # -------------------------------
    # Validation Part:
    # The complete date "DD-MMM-YYYY" is 11 characters long.
    # If the text is not yet complete, do not show an error.
    if len(text) < 11:
        e.control.error_text = None
    else:
        # Once the input is complete, validate it against the regex.
        if DATE_REGEX.fullmatch(text):
            e.control.error_text = None  # Input is valid; clear any error.
        else:
            e.control.error_text = "Invalid date format, e.g., 01-Jan-2023"  # Show error message.

    # Update the control so that changes are rendered
    e.control.update()

