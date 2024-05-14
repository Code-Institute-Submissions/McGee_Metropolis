import gspread
from google.oauth2.service_account import Credentials
import random #imports the random module
import os
import platform

#Constants

GRID_SIZE = 10
ZONE_SYMBOLS = {
    'Residential': '🟢',  # Residential
    'Commercial': '🟣',  # Commercial
    'Industrial': '🟤',  # Industrial
    'School': '🟡',  # School
    'Hospital': '🔴',  # Hospital
    '-': '⚪'    # Empty space
}

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

def clear_screen():
    """Clear the console screen."""
    system_name = platform.system()
    if system_name == "Windows":
        os.system("cls")
    else:
        os.system("clear")

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

#Initialise an empty game grid
def initialize_grid(size):
    """Initialise an empty game grid with the specified size."""
    return [['-' for _ in range(size)] for _ in range(size)]

def initialize_random_grid(size, zone_counts):
    """Initialise the game grid with random zones based on fetched counts."""
    grid = [['-' for _ in range(size)] for _ in range(size)]
    positions = [(x, y) for x in range(size) for y in range(size)]
    random.shuffle(positions)  # Shuffle positions for random placement

    for zone_type, count in zone_counts.items():
        for _ in range(min(count, len(positions))):
            x, y = positions.pop()
            grid[x][y] = zone_type

    return grid

def print_grid(grid):
    """Print the grid to the console with boxed borders and consistent alignment."""
    cell_width = 4
    num_columns = len(grid[0])

    header_padding = " " * 5 # Add padding for the row letters
    print("      0     1     2     3     4     5     6     7     8     9")
                                           
    for index, row in enumerate(grid):
        # Print each row with a numerical label
        row_str = f"{index:2} |" + "|".join(f"{ZONE_SYMBOLS.get(cell, '⚪'):^{cell_width}}" for cell in row) + "|"
        print(row_str)

    print()  # Ensure there's a new line after the grid for better spacing

def place_zone(grid, zone_type, x, y, player_resources):
    """Place a zone on the grid at the specified coordinates if enough resources available."""
    zone_costs = {'Residential': 1250, 'Commercial': 450, 'Industrial': 450, 'School': 100, 'Hospital': 100}  # Costs of resources
    if player_resources['Money'] >= zone_costs[zone_type]:
        if grid[x][y] == '-':
            grid[x][y] = ZONE_SYMBOLS[zone_type] 
            player_resources['Money'] -= zone_costs[zone_type]  # Deduct the cost of zone from resources
            print(f"Congratulations, you built a {zone_type} and placed in the city at {x}, {y}.")
            print(f"Remaining Money: {player_resources['Money']}")
        else:
            print("This plot is already occupied.")
    else:
        print("Sorry, you do not enough money to build this zone right now.")


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

def fetch_player_resources():
    """Fetch player resources from the 'resources' worksheet and return as a dictionary."""
    try:
        resources_sheet = SHEET.worksheet('resources')
        data = resources_sheet.get_all_records()  # Convert list to dictionaries
        player_resources = {}
        for res in data:
            resource_type = res['Resource Type']
            current_value = res['Current Value']
            # Check if the current value is a string and contains commas, replace commas if present
            if isinstance(current_value, str) and ',' in current_value:
                current_value = current_value.replace(',', '')
            player_resources[resource_type] = int(current_value)
        return player_resources
    except gspread.exceptions.WorksheetNotFound:
        print("Error: 'resources' worksheet not found.")
        return {}
    except Exception as e:
        print(f"Error while accessing resources: {e}")
        return {}

def update_resources_in_sheet(player_resources):
    """Update the resources back to Google Sheets."""
    resources_sheet = SHEET.worksheet('resources')
    for resource_type, value in player_resources.items():
        cell = resources_sheet.find(resource_type)  # Find the cell with the resource type
        resources_sheet.update_cell(cell.row, cell.col + 1, str(value))  # Update the next column

def handle_zone_action(grid, player_resources):
    """Handle the action of placing a zon and check resources."""
    while True:
        try:
            x = int(input(f"Enter X coordinate for building a zone (0-{GRID_SIZE-1}): "))
            y = int(input(f"Enter Y coordinate for building a zone (0-{GRID_SIZE-1}): "))

            if 0 <= x < GRID_SIZE and 0 <= y < GRID_SIZE:
                zone_input = input("Enter zone type - R (Residential), C (Commercial), I (Industrial), S (School), H (Hospital): ").upper()

                # Map input to full names for internal logic
                zone_map = {
                    'R': 'Residential',
                    'C': 'Commercial',
                    'I': 'Industrial',
                    'S': 'School',
                    'H': 'Hospital'
                }

                if zone_input in zone_map:
                    zone_type = zone_map[zone_input]
                    place_zone(grid, zone_type, x, y, player_resources)
                    print_grid(grid)
                    break
                else:
                    print("Invalid zone type. Please use 'R', 'C', 'I', 'S', or 'H'.")
            else:
                print(f"Invalid coordinates. Please enter values between 0 and {GRID_SIZE - 1}.")
        except ValueError:
            print("Invalid input. Please enter numeric grid coordinates.")

def fetch_events():
    """Fetch event data from the Google Sheet."""
    events_sheet = SHEET.worksheet('events')
    events = events_sheet.get_all_records()
    # Initialise all events as inactive with specified duration
    for event in events:
        event['Active'] = False
        event['Duration'] = int(event.get('Duration', 0))
    return events

def apply_random_event(events, player_resources, day):
    """Randomly select and apply an event effect if it's not currently active, and handle event duration."""
    active_events = [event for event in events if event['Active']]
    for event in active_events:
        if event['Duration'] > 0:
            print(f"Oh no, an event is impacting the city: {event['Description']} affecting {event['Impacted Zones']} with {event['Impact Type']} of {event['Impact Value']}. Days left: {event['Duration']}")
            apply_impact(player_resources, event['Impact Type'], event['Impact Value'], event['Impacted Zones'])
            event['Duration'] -= 1
        if event['Duration'] <= 0:
            event['Active'] = False # Deactive event once duration is complete

    # Start a new event if there are no active events
    if not any(event['Active'] for event in events):
        new_event = random.choice(events)
        if not new_event['Active']:
            new_event['Active'] = True
            new_event['Duration'] = int(new_event.get('Duration', 0))  # Set duration
            print(f"Oh no a new event has started:  {new_event['Description']} affecting {new_event['Impacted Zones']} with {new_event['Impact Type']} of {new_event['Impact Value']}. Duration: {new_event['Duration']} days.")
            apply_impact(player_resources, new_event['Impact Type'], new_event['Impact Value'], new_event['Impacted Zones'])
            apply_impact(player_resources, new_event['Impact Type'], new_event['Impact Value'], new_event['Impacted Zones'])

def apply_impact(player_resources, impact_type, impact_value, impacted_zones):
    # Mapping from event impact types to player resource keys
    impact_type_map = {
        'electricity supply reduction': 'Electricity',
        'money reduction': 'Money',
        'water supply reduction': 'Water',
    }
    """Apply the calculated impact to the player's resources based on the impacted zone."""
    if impacted_zones.lower() == 'all':
        for key in player_resources:
            if key in impact_type_map.values():  
                adjusted_impact_type = impact_type_map.get(impact_type, impact_type)
                update_resource(player_resources, adjusted_impact_type, impact_value)
    else:
        adjusted_impact_type = impact_type_map.get(impact_type, impact_type)
        update_resource(player_resources, adjusted_impact_type, impact_value)

def update_resource(player_resources, resource_type, impact_value):
    """Update a specific resource based on an impact value."""
    if '%' in impact_value:
        modifier = float(impact_value.strip('%')) / 100
        player_resources[resource_type] *= (1 + modifier)
    else:
        player_resources[resource_type] += float(impact_value)

def confirm_exit():
    """Confirm before exiting the game."""
    confirm = input("Are you sure you want to exit the game? (yes/no): ").lower()
    return confirm == 'yes'


def main():
    while True:
        zone_counts = fetch_zone_counts()
        events = fetch_events()
        player_resources = fetch_player_resources()
        current_day = 1  # Start the day counter

        if zone_counts:
            # If counts are successfully fetched, initialise the grid with these counts
            grid = initialize_random_grid(GRID_SIZE, zone_counts)
        else:
            # If fetching fails, fallback to an empty grid
            grid = initialize_grid(GRID_SIZE)
        while current_day <=30:
            clear_screen()
            print("McGee Metropolis City Map:")
            print_grid(grid)

            print(f"Day {current_day}: Good Morning! A New day has started...")
            apply_random_event(events, player_resources, current_day)

            action = input("\nChoose the action you would like to take, build a zone, check resources or exit the game: (zone/resources/exit): ").lower()
            if action == 'zone':
                handle_zone_action(grid, player_resources)
            elif action == 'resources':
                print("Current Resources:")
                for key, value in player_resources.items():
                    print(f"{key}: {value}")
            elif action == 'exit':
                if confirm_exit():
                    print("Exiting the game.")
                    return
            elif action == 'help':
                print("Commands available:")
                print("  zone - Place a new zone.")
                print("  resources - Display current resources.")
                print("  exit - Exit the game.")
                print("  help - Show this help message.")
            else:
                print("Invalid action. Please choose 'zone', 'resources', or 'exit'.")

            update_resources_in_sheet(player_resources)
            current_day += 1  # Increment the day counter

            
        print("Unfortunately, you have reached the end of 30 days and haven't reached the goal. The game is over, better luck next time!")
        restart = input("Would you like to start again at day 1? (yes/no): ").lower()
        if restart != 'yes':
            print("Exiting the game.")
            break  # Exit the entire game loop


if __name__ == "__main__":
    main()