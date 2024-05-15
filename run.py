import gspread
from google.oauth2.service_account import Credentials
import random #imports the random module
import os
import platform

#Constants

GRID_SIZE = 10
ZONE_SYMBOLS = {
'Residential': '🟢', # Residential
'Commercial': '🟣', # Commercial
'Industrial': '🟤', # Industrial
'School': '🟡', # School
'Hospital': '🔴', # Hospital
'-': '⚪' # Empty space
}

# ANSI colour Codes for console colour
class Colour:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

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

def place_zone(grid, zone_type, x, y, player_resources):
    """Place a zone on the grid at the specified coordinates if enough resources available."""
    zone_costs = {'Residential': 1250, 'Commercial': 450, 'Industrial': 450, 'School': 100, 'Hospital': 100}  # Costs of resources
    if player_resources['Money'] >= zone_costs[zone_type]:
        if grid[x][y] == '-':
            grid[x][y] = zone_type
            player_resources['Money'] -= zone_costs[zone_type]  # Deduct the cost of zone from resources
            print(f"Congratulations, you built a {zone_type} and placed in the city at {x}, {y}.")
            print(f"Remaining Money: {player_resources['Money']}")
        else:
            print("This plot is already occupied")
    else:
        print("Sorry, you do not enough money to build this zone right now.")

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
            regeneration_rate = res.get('Regeneration Rate', 0)
            # Check if the current value is a string and contains commas, replace commas if present
            if isinstance(current_value, str) and ',' in current_value:
                current_value = current_value.replace(',', '')
            player_resources[resource_type] = {
                'current': int(current_value),
                'regeneration': float(regeneration_rate)
            }
        return player_resources
    except Exception as e:
        print(f"Error while accessing resources: {e}")
        return {}

def update_resources_in_sheet(player_resources):
    """Update the resources back to Google Sheets."""
    resources_sheet = SHEET.worksheet('resources')
    for resource_type, value in player_resources.items():
        cell = resources_sheet.find(resource_type)  # Find the cell with the resource type
        resources_sheet.update_cell(cell.row, cell.col + 1, str(value))  # Update the next column

def reset_resources_to_default():
    """Reset the resource values in the Google Sheet to their default amounts."""
    try:
        resources_sheet = SHEET.worksheet('resources')
        default_resources = {
            'Money': 10000, 
            'Population': 200,  
            'Electricity': 500,  
            'Water': 500 
        }
        # Iterate over the default_resources dictionary and update the sheet
        for resource, value in default_resources.items():
            cell = resources_sheet.find(resource)  # Find the cell with the resource type
            resources_sheet.update_cell(cell.row, cell.col + 1, value)  # Update the resource value to default
        print("Resources have been reset to default values.")
    except Exception as e:
        print(f"Failed to reset resources: {e}")

def regenerate_resources(player_resources):
    """Regenerate resources daily"""
    for resource, values in player_resources.items():
        # Apply the regeneration rate directly to the current value
        values['current'] += values['regeneration']
        print(f"Updated {resource}: {values['current']}")

def print_resources(resources):
    print(Colour.BLUE + "Resources:" + Colour.ENDC)
    print(f"{Colour.HEADER}Type{Color.ENDC}         {Colour.HEADER}Current{Colour.ENDC}     {Color.HEADER}Regeneration{Color.ENDC}")
    for key, value in resources.items():
        print(f"{key}: {value}")

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
                    clear_screen()  
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
            print(f"Oh no, an event is impacting the city: {event['Description']} resulting in {event['Impact Type']} of {event['Impact Value']}. Days left: {event['Duration']}")
            apply_impact(player_resources, event['Impact Type'], event['Impact Value'])
            event['Duration'] -= 1
        if event['Duration'] <= 0:
            event['Active'] = False

    if not any(event['Active'] for event in events):
        new_event = random.choice(events)
        if not new_event['Active']:
            new_event['Active'] = True
            new_event['Duration'] = int(new_event.get('Duration', 1))
            print(f"Oh no, a new event has started: {new_event['Description']} resulting in {new_event['Impact Type']} by {new_event['Impact Value']} for {new_event['Duration']} days.")
            apply_impact(player_resources, new_event['Impact Type'], new_event['Impact Value'])

def apply_impact(player_resources, impact_type, impact_value):
    """Apply the calculated impact to the player's resources."""
    # Mapping from event impact types to player resource keys
    impact_type_map = {
        'electricity supply reduction': 'Electricity',
        'money reduction': 'Money',
        'water supply reduction': 'Water',
    }

    adjusted_impact_type = impact_type_map.get(impact_type, None)

    # Check if the mapping was successful
    if not adjusted_impact_type:
        return  # Exit if no valid mapping exists


    """Apply the calculated impact to the player's resources."""
    update_resource(player_resources, adjusted_impact_type, impact_value)
    print(f"{adjusted_impact_type} after impact: {player_resources.get(adjusted_impact_type)}")


def update_resource(player_resources, resource_type, impact_value):
    """Update a specific resource based on an impact value."""
    if '%' in impact_value:
        modifier = float(impact_value.strip('%')) / 100
        player_resources[resource_type] *= (1 + modifier)
    else:
        player_resources[resource_type] += float(impact_value)

def fetch_metrics():
    return {
        'Employment Rate': 70,
        'Crime Rate': 5,
        'Happiness Index': 75,
        'Health': 80
    }

def check_metrics(metrics):
    min_values = {
        'Employment Rate': 50,
        'Crime Rate': 30,  # Represents a max value
        'Happiness Index': 50,
        'Health': 50
    }
    for metric, value in metrics.items():
        if metric == 'Crime Rate':
            if value > min_values[metric]:
                print("Game Over: Crime Rate is too high!")
                return False
        else:
            if value < min_values[metric]:
                print(f"Game Over: {metric} is too low!")
                return False
    return True

def update_metrics(metrics, zone_type, amount):
    if zone_type == 'Commercial' or zone_type == 'Industrial':
        metrics['Employment Rate'] += amount * 0.5
    elif zone_type == 'Residential':
        metrics['Employment Rate'] -= amount * 0.3
        metrics['Crime Rate'] += amount * 0.2
    elif zone_type == 'School':
        metrics['Happiness Index'] += amount * 1
    elif zone_type == 'Hospital':
        metrics['Health'] += amount * 1.5

    # Ensure metrics don't go out of bounds
    metrics['Employment Rate'] = min(max(metrics['Employment Rate'], 0), 100)
    metrics['Crime Rate'] = min(max(metrics['Crime Rate'], 0), 100)
    metrics['Happiness Index'] = min(max(metrics['Happiness Index'], 0), 100)
    metrics['Health'] = min(max(metrics['Health'], 0), 100)

def print_metrics(metrics):
    print(Colour.GREEN + "Metrics:" + Colour.ENDC)
    print(f"{Colour.HEADER}Metric{Colour.ENDC}               {Colour.HEADER}Value (%){Colour.ENDC}")
    for key, value in metrics.items():
        print(f"{key}: {value}")

def print_help():
    print("Commands available:")
    print("  build - Place a new zone.")
    print("  next - Move to the next day.")
    print("  restart - Restart the game.")
    print("  help - Show this help message.")

def confirm_restart():
    response = input("Are you sure you want to restart the game? (yes/no): ")
    return response.lower() == 'yes'

def confirm_exit():
    """Confirm before exiting the game."""
    confirm = input("Are you sure you want to exit the game? (yes/no): ").lower()
    return confirm == 'yes'


def main():
    monetary_goal = 20000
    min_metrics = {'Employment Rate': 50, 'Crime Rate': 50, 'Happiness Index': 50, 'Health': 50}  # Minimum / maximum acceptable metric values
    while True:
        zone_counts = fetch_zone_counts()
        events = fetch_events()
        player_resources = fetch_player_resources()
        metrics = fetch_metrics()
        current_day = 1  # Start the day counter
        
        if zone_counts:
            # If counts are successfully fetched, initialise the grid with these counts
            grid = initialize_random_grid(GRID_SIZE, zone_counts)
        else:
            # If fetching fails, fallback to an empty grid
            grid = initialize_grid(GRID_SIZE)
        game_over = False
        while current_day <=30 and not game_over:
            clear_screen()
            print("McGee Metropolis City Map:")
            print_grid(grid)
            print("\nCurrent Resources and Metrics:")
            print_resources(player_resources)  # Function to print resources in a formatted table
            print_metrics(metrics)  # Function to print metrics in a formatted table

            regenerate_resources(player_resources)
            print(f"Day {current_day}: Good Morning! A New day has started...")
            apply_random_event(events, player_resources, current_day)
            if not check_metrics(metrics):
                print("One or more metrics have fallen below or above critical levels. The game is over, better luck next time!")
                game_over = True
                continue

            action = input("\nChoose the action you would like to take, build a zone, check resources, access help or exit the game: (zone/resources/help/exit): ").lower()
            if action == 'zone':
                handle_zone_action(grid, player_resources)
                print_grid(grid)
            elif action == 'next':
                current_day += 1  # Increment the day counter
            elif action == 'restart':
                if confirm_restart():  # Confirm restart decision
                    print("Restarting the game.")
                    reset_resources_to_default()
                    metrics = fetch_metrics() 
                    fetch_player_resources()
                    print("Resources and metrics have been reset.")
                    break
            elif action == 'help':
               print_help()
            elif action == 'exit':
                if confirm_exit():
                    print("Exiting the game.")
                    reset_resources_to_default()  # Reset resources on exit
                    return
            else:
                print("Invalid action. Please choose 'zone', 'resources', 'help', or 'exit'.")

            update_resources_in_sheet(player_resources)
            
        if not game_over and current_day > 30:
            if player_resources['Money'] >= monetary_goal and all(metrics[m] >= min_metrics[m] for m in metrics):
                print("Congratulations! You have reached your goals and won the game.")
            else:
                print("Unfortunately, you did not meet the goals. Game over.")
        if not confirm_restart():
            print("Exiting the game.")
            break

if __name__ == "__main__":
    main()