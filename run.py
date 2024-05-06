import gspread
from google.oauth2.service_account import Credentials

#Constants

GRID_SIZE = 10 

#Google Sheets setup
SCOPE = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/drive"
    ]

CREDS = Credentials.from_service_account_file('creds.json')
SCOPED_CREDS = CREDS.with_scopes(SCOPE)
GSPREAD_CLIENT = gspread.authorize(SCOPED_CREDS)
SHEET = GSPREAD_CLIENT.open('McGee_Metropolis')

resources = SHEET.worksheet('resources')
data = resources.get_all_values()

#Initialise the game grid
def initialize_grid(size):
    """Initialise the game grid with the specified size."""
    return [['-' for _ in range(size)] for _ in range(size)]

def print_grid(grid):
    """Print the grid to the console."""
    for row in grid:
        print(' '.join(row))
    print()  # Print on a new line for improved visibility

def main():
    # Initialize the grid and print it to the console
    grid = initialize_grid(GRID_SIZE)
    print("Initial Game Grid:")
    print_grid(grid)


if __name__ == "__main__":
    main()