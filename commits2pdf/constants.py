DATE = r"^\d{4}\-(0?[1-9]|1[012])\-(0?[1-9]|[12][0-9]|3[01])$" # YYYY/mm/dd or YYYY/m/d
EMAILS = r"^([\w+-.%]+@[\w.-]+\.[A-Za-z]{2,4})(,[\w+-.%]+@[\w.-]+\.[A-Za-z]{2,4})*$" # usr@email.com or usr@email.com,user2@email.com, etc
QUERY = r"^(?:[^,\s]+(?:,[^,\s]+)*)$" # value1,value2 etc or value1

WIDTH = 612
HEIGHT = 792
MARGIN = 50

LIGHT = {
    "background": (1, 1, 1),
    "text": (0, 0, 0),
    "diff_link": (0, 0, 1)
}

DARK = {
    "background": (0.2, 0.2, 0.2),
    "text": (0.9, 0.9, 0.9),
    "diff_link": (0.6, 0.6, 1)
}