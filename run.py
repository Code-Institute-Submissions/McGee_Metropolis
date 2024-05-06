import gspread
from google.oauth2.service_account import Credentials

#Constants

GRID_SIZE = 15 

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


#Initialise the game grid
def initialize_grid(size):
    """Initialise the game grid with the specified size."""
    return [['-' for _ in range(size)] for _ in range(size)]

def print_grid(grid):
    """Print the grid to the console."""
    for row in grid:
        print(' '.join(row))
    print()  # Print on a new line for improved visibility

def place_zone(grid, zone_type, x, y):
    """Place a zone on the grid at the specified coordinates."""
    if grid[x][y] == '-':
        grid[x][y] = zone_type
        print(f"Zone placed at {x}, {y}.")
    else:
        print("This plot is already occupied.")

def fetch_zone_counts():
    """Fetch the counts of each zone type from Google Sheets."""
    try:
        zone_sheet = SHEET.worksheet('zones')
        data = zone_sheet.get_all_values()
         # Create a dictionary where the key is the zone type and the value is the count
        zone_counts = {row[0]: int(row[1]) for row in data[1:]}  # Skip header row
        return zone_counts
    except Exception as e:
        print(f"Error fetching zone counts: {e}")
        return {}

def get_resources():
    """Source and display resources from the 'resources' worksheet."""
    try:
        resources = SHEET.worksheet('resources')
        data = resources.get_all_values()
        print("\nCurrent Resources:")
        for row in data:
            print(row)
    except gspread.exceptions.WorksheetNotFound:
        print("Error: 'resources' worksheet not found.")
    except Exception as e:
        print(f"Error while accessing resources: {e}")

def main():
    zone_counts = fetch_zone_counts()
    if zone_counts:
        # If counts are successfully fetched, initialise the grid with these counts
        grid = initialize_random_grid(GRID_SIZE, zone_counts)
    else:
        # If fetching fails, fallback to an empty grid
        grid = initialize_grid(GRID_SIZE)
    print("Initial Game Grid:")
    print_grid(grid)

    while True:
        action = input("\nChoose the action you would like to take, build a zone, check resources or exit the game: (zone/resources/exit): ").lower()
        if action == 'zone':
            try:
                # Get coordinates from the player
                x = int(input(f"Enter X coordinate for building zone (0-{GRID_SIZE-1}): "))
                y = int(input(f"Enter Y coordinate for building zone (0-{GRID_SIZE-1}): "))
            
                # Ensure coordinates are within grid boundary
                if 0 <= x < GRID_SIZE and 0 <= y < GRID_SIZE:
                # Get the zone type (R for Residential, C for Commercial, I for Industrial)
                    zone_type = input("Enter zone type - Residential = R, Commercial = C, Industrial = I (R/C/I): ").upper()
                    if zone_type in ['R', 'C', 'I']:
                        place_zone(grid, zone_type, x, y)
                    else:
                        print("Invalid zone type. Please use 'R', 'C', or 'I'.")
                else:
                    print(f"Invalid coordinates. Please enter values between 0 and {GRID_SIZE - 1}.")
            except ValueError:
                print("Invalid input. Please enter numeric grid coordinates.")
            print_grid(grid)
        elif action == 'resources':
            get_resources()
        elif action == 'exit':
            print("Exiting the game.")
            break
        else:
            print("Invalid action. Please choose 'zone', 'resources', or 'exit'.")

if __name__ == "__main__":
    main()