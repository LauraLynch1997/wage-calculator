import gspread
from google.oauth2.service_account import Credentials

SCOPE = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/drive"
    ]

CREDS = Credentials.from_service_account_file('creds.json')
SCOPED_CREDS = CREDS.with_scopes(SCOPE)
GSPREAD_CLIENT = gspread.authorize(SCOPED_CREDS)
SHEET = GSPREAD_CLIENT.open('employee-wage')


def get_sales_data():
    """
    Get employees hours input from the user.
    Run a while loop to collect a valid string of data from the user
    via the terminal, which must be a string of 2 numbers separated
    by commas. The loop will repeatedly request data, until it is valid.
    """
    while True:
        print("Please enter number of hours employee has worked")
        print("Data should be two numbers, separated by commas. ID, Hours")
        print("Example: 123,40\n")

        data_str = input("Enter your data here:\n")

        sales_data = data_str.split(",")

        if validate_data(sales_data):
            print("Data is valid!")
            break

    return sales_data


def validate_data(values):
    """
    Inside the try, converts all string values into floats.
    Raises ValueError if strings cannot be converted into float,
    or if there aren't exactly 2 values.
    """
    try:
        [float(value) for value in values]
        if len(values) != 2:
            raise ValueError(
                f"Exactly 6 values required, you provided {len(values)}"
            )
    except ValueError as e:
        print(f"Invalid data: {e}, please try again.\n")
        return False

    return True


def update_worksheet(data, worksheet):
    """
    Receives a list of integers to be inserted into a worksheet
    Update the relevant worksheet with the data provided
    """
    print(f"Updating {worksheet} worksheet...\n")
    worksheet_to_update = SHEET.worksheet(worksheet)
    worksheet_to_update.append_row(data)
    print(f"{worksheet} worksheet updated successfully\n")

def get_pay_rate(rota):
    pay_rates = SHEET.worksheet("Pay-Rates")
    cell = pay_rates.find(str(int(rota[0])))
    rate = pay_rates.cell(cell.row, 2).value
    return rate

def calculate_gross(hours, pay_rate):
    return float(pay_rate) * hours

def calculate_taxes(id, gross):
    tax_data = [id, gross]
    weekly_tax_cut_off = 40000 / 52
    low_band_full_tax = weekly_tax_cut_off * 0.2
    total_income_tax = 0
    if gross > weekly_tax_cut_off:
        cut_off_tax = gross - weekly_tax_cut_off
        high_band_tax = cut_off_tax * 0.4
        total_income_tax = high_band_tax + low_band_full_tax
        tax_data.append(round(total_income_tax, 2))
    else:
        total_income_tax = gross * 0.2
        tax_data.append(round(total_income_tax, 2))
    prsi = gross * 0.04
    tax_data.append(round(prsi, 2))
    usc = gross * 0.05
    tax_data.append(round(usc, 2))
    net_tax = total_income_tax + prsi + usc
    tax_data.append(round(gross - net_tax, 2))
    return tax_data


def main():
    """
    Run all program functions
    """
    data = get_sales_data()
    rota_data = [float(num) for num in data]
    update_worksheet(rota_data, "Rota")
    pay_rate = get_pay_rate(rota_data)
    gross_pay = calculate_gross(rota_data[1], pay_rate)
    tax_data = calculate_taxes(rota_data[0], gross_pay)
    update_worksheet(tax_data, "Wages")


print("Welcome to HR Wages Automation")

main()