from dash import no_update
from datetime import date, timedelta


def update_date(callbackid,date_picker,callback_context):
    ctx = callback_context
    # Default case
    data = {}
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    print(f"{button_id}****")
    if button_id == 'date-picker' + callbackid:
        selected_date = date.fromisoformat(date_picker)
        data = {
            "workstart": selected_date.isoformat(),
            "workend": (selected_date + timedelta(days=1)).isoformat(),
            "interval": "day"
        }
    elif button_id == 'btn-day' + callbackid:
        data = {
            "workstart": (date.today() - timedelta(days=1)).isoformat(),
            "workend": date.today().isoformat(),
            "interval": "day"

        }
    elif button_id == 'btn-week' + callbackid:
        selected_date = date.fromisoformat(date_picker)
        year, week, _ = selected_date.isocalendar()  # Get ISO year and week number
        start = date.fromisocalendar(year, week, 1)  # Week starts on Monday, which is denoted by 1 in ISO calendar
        end = date.fromisocalendar(year, week, 7)  # Week ends on Sunday, which is denoted by 7 in ISO calendar
        data = {
            "workstart": start.isoformat(),
            "workend": end.isoformat(),
            "interval": "week"
        }

    elif button_id == 'btn-month' + callbackid:
        selected_date = date.fromisoformat(date_picker)
        start = date(selected_date.year, selected_date.month, 1)  # Start of the month
        if selected_date.month == 12:
            end = date(selected_date.year + 1, 1, 1) - timedelta(days=1)
        else:
            end = date(selected_date.year, selected_date.month + 1, 1) - timedelta(days=1)
        data = {
            "workstart": start.isoformat(),
            "workend": end.isoformat(),
            "interval": "month"
        }
    elif button_id == 'btn-year' + callbackid:
        selected_date = date.fromisoformat(date_picker)
        start = date(selected_date.year, 1, 1)  # Start of the year
        end = date(selected_date.year, 12, 31)  # End of the year
        data = {
            "workstart": start.isoformat(),
            "workend": end.isoformat(),
            "interval": "year"
        }
    print(data)
    return data


def update_date_output(n1, date_picker, n2, n3, n4, data):
    if n1:
        result = str(n1)
    elif date_picker:
        result = str(date_picker)
    elif n2:
        result = str(n2)
    elif n3:
        result = str(n3)
    elif n4:
        result = str(n4)
    else:
        data = {}
        result = no_update

    return data, result
