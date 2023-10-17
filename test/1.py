print("111.555".isdigit())

def is_numeric_and_convert(input_str):
    try:
        numeric_value = float(input_str)
        return numeric_value
    except ValueError:
        return None