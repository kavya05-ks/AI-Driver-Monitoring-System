import os
import re
import sqlite3
from datetime import datetime

try:
    from twilio.rest import Client
except ImportError:
    Client = None


BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

DATABASE_PATH = os.path.join(
    BASE_DIR,
    "database",
    "users.db"
)


TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")


def get_driver_numbers(username):

    if not username:
        print("SMS FAILED")
        print("Reason: Driver username is missing")
        return []

    try:
        conn = sqlite3.connect(DATABASE_PATH)

        try:
            driver = conn.execute(
                """
                SELECT phone_number, emergency_number
                FROM drivers
                WHERE username = ?
                """,
                (username,)
            ).fetchone()
        finally:
            conn.close()

        if not driver:
            print("DRIVER DETAILS NOT FOUND")
            print("Username:", username)
            return []

        contact = driver[0]
        emergency_contact = driver[1]

        numbers = []

        if contact:
            contact = str(contact).strip()

            if contact:
                numbers.append(contact)

        if emergency_contact:
            emergency_contact = str(
                emergency_contact
            ).strip()

            if (
                emergency_contact
                and emergency_contact not in numbers
            ):
                numbers.append(emergency_contact)

        return numbers

    except Exception as e:
        print("DATABASE ERROR:")
        print(e)
        return []


def format_phone_number(number):

    number = str(number).strip()

    number = number.replace(" ", "")
    number = number.replace("-", "")
    number = number.replace("(", "")
    number = number.replace(")", "")

    if number.startswith("+"):
        return number

    if number.startswith("91") and len(number) == 12:
        return "+" + number

    if len(number) == 10:
        return "+91" + number

    if re.fullmatch(r"\+?[1-9]\d{7,14}", number):
        return number

    return None


def mask_phone_number(number):

    return "*" * max(0, len(number) - 3) + number[-3:]


def get_alert_message(username, alert_type):

    normalized_alert = str(alert_type or "").strip().upper()

    if "DROWS" in normalized_alert:
        return (
            "AI Driver Alert: Drowsiness detected for driver "
            + username
            + ". Please check the driver immediately."
        )

    if "PHONE" in normalized_alert or "MOBILE" in normalized_alert:
        return (
            "AI Driver Alert: Phone usage detected for driver "
            + username
            + ". Please check the driver."
        )

    if "DISTRACT" in normalized_alert or "HEAD" in normalized_alert:
        return (
            "AI Driver Alert: Driver "
            + username
            + " is distracted. Please check the driver immediately."
        )

    if "YAWN" in normalized_alert:
        return (
            "AI Driver Alert: Excessive yawning detected for driver "
            + username
            + ". Please check the driver."
        )

    return (
        "AI Driver Alert: "
        + str(alert_type)
        + " detected for driver "
        + username
        + ". Please check the driver."
    )


def send_alert(username, alert_type):

    print("SMS ALERT PROCESS STARTED")
    print("Driver:", username)
    print("Alert:", alert_type)

    def failed(reason):
        print("SMS FAILED")
        print("Driver:", username)
        print("Alert:", alert_type)
        print("Reason:", reason)
        return False

    if not username:
        return failed("Driver username is missing")

    if not TWILIO_ACCOUNT_SID:
        return failed("TWILIO_ACCOUNT_SID is missing")

    if not TWILIO_AUTH_TOKEN:
        return failed("TWILIO_AUTH_TOKEN is missing")

    if not TWILIO_PHONE_NUMBER:
        return failed("TWILIO_PHONE_NUMBER is missing")

    if Client is None:
        return failed("Twilio package is not installed")

    numbers = get_driver_numbers(username)

    if not numbers:
        return failed("No registered phone or emergency number found")

    try:
        client = Client(
            TWILIO_ACCOUNT_SID,
            TWILIO_AUTH_TOKEN
        )

    except Exception as e:
        return failed("Unable to create Twilio client: " + str(e))

    message_body = get_alert_message(username, alert_type)

    success_count = 0

    for number in numbers:

        formatted_number = format_phone_number(number)

        if not formatted_number:
            print("SMS FAILED")
            print("Driver:", username)
            print("Alert:", alert_type)
            print("Reason: Invalid phone number")
            continue

        try:

            message = client.messages.create(
                body=message_body,
                from_=TWILIO_PHONE_NUMBER,
                to=formatted_number
            )

            print("SMS SENT")
            print("Driver:", username)
            print("Alert:", alert_type)
            print("Mobile:", mask_phone_number(formatted_number))

            success_count += 1

        except Exception as e:

            print("SMS FAILED")
            print("Driver:", username)
            print("Alert:", alert_type)
            print("Mobile:", mask_phone_number(formatted_number))
            print("Reason:", e)

    print()
    print(
        "SMS sent successfully to "
        + str(success_count)
        + " of "
        + str(len(numbers))
        + " numbers."
    )

    print("============================================")
    print("SMS ALERT PROCESS FINISHED")
    print("============================================")

    return success_count > 0