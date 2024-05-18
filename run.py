"""
McGee Metropolis: A city-building game.

This contains the implementation of McGee Metropolis, a game where
players build and manage a city, balancing resources and metrics to achieve
goals within a set number of days. The game uses Google Sheets to store and
retrieve data for game state and resources.
"""

import random
import os
import platform
import time
import gspread
from google.oauth2.service_account import Credentials
from gspread.exceptions import GSpreadException

# Constants

GRID_SIZE = 10
ZONE_SYMBOLS = {
    'Residential': '🟢',  # Residential
    'Commercial': '🟣',  # Commercial
    'Industrial': '🟤',  # Industrial
    'School': '🟡',  # School
    'Hospital': '🔴',  # Hospital
    '-': '⚪'  # Empty space
}

"""ANSI color codes for colored console output."""


class Colour:
    """
    ANSI colour codes for coloured console output.

    This class provides constants for various ANSI colour codes that can be
    used to format text output in the console with different colurs and styles.
    """
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

# Google Sheets setup


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
    """Clear the console screen.
    Detects the operating system and clears the screen.
    """
    system_name = platform.system()
    if system_name == "Windows":
        os.system("cls")
    else:
        os.system("clear")


def show_intro():
    """
    Display the game introduction and instructions in clear sections.
    """
    logo = r"""
    __        __   _
    \ \      / /__| | ___ ___  _ __ ___   ___
     \ \ /\ / / _ \ |/ __/ _ \| '_ ` _ \ / _ \
      \ V  V /  __/ | (_| (_) | | | | | |  __/
       \_/\_/ \___|_|\___\___/|_| |_| |_|\___|
    """
    # Welcome and Aim of the Game
    welcome_message = "Welcome to McGee Metropolis!\n"
    aim = """
    Aim of the Game:
    You are being challenged to build and manage a thriving city.
    Build zones, manage your money, population, electricity and water.
    Your goal is to reach 200000 in money within 30 days whilst
    maintaining the Employment Rate, Crime Rate, Happiness Index, & Health.
    Every move has an impact on your resources & metrics, so plan carefully.
    EG. If you build a residential zone, your population will increase,
    but your employment rate will decrease.
    """

    print(Colour.GREEN + logo + Colour.ENDC)
    for char in welcome_message:
        print(Colour.BLUE + char, end='', flush=True)
        time.sleep(0.05)

    for char in aim:
        print(Colour.GREEN + char, end='', flush=True)
        time.sleep(0.02)

    while True:
        choice = input(
            Colour.BOLD +
            "\nPress Enter to read the instructions,\n" +
            "'play' to start the game, or 'exit' to exit: " +
            Colour.ENDC).strip().lower()
        if choice == '':
            clear_screen()
            show_instructions()
            break
        elif choice == 'play':
            clear_screen()
            break
        elif choice == 'exit':
            print("Exiting the game.")
            exit()
        else:
            print("Invalid input. Please press Enter, type 'play', or type 'exit'.")
    clear_screen()


def show_instructions():
    """
    Display the game instructions in clear sections.
    """
    # Game Instructions
    instructions = """
    Game Instructions:
    1. You will start with a grid representing your city.

    2. You will also be allocated resources.

    3. Every decision impacts the city just like in real life.

    4. Manage your resources wisely to reach the monetary goal
    and keep your metrics balanced.

    5. Random events will impact your city each day.

    6. Tables will update you each day with your current metrics and resources.
    """

    # Zone Details
    zone_details = """
     Zone Details:
    - Residential 🟢: Cost to build: 1250, income generated 50 per day
    - Commercial 🟣: Cost to build: 450, income generated 100 per day
    - Industrial 🟤: Cost to build: 450, income generated 75 per day
    - School 🟡: Cost to build: 100, income generated 20 per day
    - Hospital 🔴: Cost to build: 100, income generated 30 per day
    """

    for char in instructions:
        print(Colour.GREEN + char, end='', flush=True)
        time.sleep(0.02)
    for char in zone_details:
        print(Colour.GREEN + char, end='', flush=True)
        time.sleep(0.02)

    while True:
        choice = input(
            Colour.BOLD +
            "\nPress Enter to read the tips, 'play' to start the game, or 'exit' to exit: " +
            Colour.ENDC).strip().lower()
        if choice == '':
            clear_screen()
            show_tips()
            break
        elif choice == 'play':
            clear_screen()
            break
        elif choice == 'exit':
            print("Exiting the game.")
            exit()
        else:
            print("Invalid input. Please press Enter, type 'play', or type 'exit'.")
    clear_screen()


def show_tips():
    """
    Display game tips and metric stats.
    """
    metrics_tips = """
    Top Tips

    Metric Stats:
    If you hit any of these metrics, you will lose the game:
    Employment Rate: 50
    Crime Rate: 30
    Happiness Index: 50
    Health: 50

    1. Building any zone will increase your daily income.

    2. If you are building a residential zone,
    your population will increase but your employment rate will decrease.

    3. If you build a commercial zone your employment rate will increase,
    but your happiness index will decrease.

    4. If you build an industrial zone your happiness index
    and your citizens health will both decrease.

    5. Building a hospital will boost your citizens health

    6. Building a school will increase your employment rate
    and boost your happiness index.

    7. Water and electricity regenerate at a rate of 5 per day.
    """

    for char in metrics_tips:
        print(Colour.GREEN + char, end='', flush=True)
        time.sleep(0.02)

    while True:
        choice = input(
            Colour.BOLD +
            "\nPress 'play' to start the game, or 'exit' to exit: " +
            Colour.ENDC).strip().lower()
        if choice == 'play':
            clear_screen()
            break
        elif choice == 'exit':
            print("Exiting the game.")
            exit()
        else:
            print("Invalid input. Please type 'play', or type 'exit'.")
    clear_screen()


def fetch_zone_data():
    """
    Fetch the data of each zone type from Google Sheets.

    Returns:
    dict: A dictionary with zone types as keys and a dictionary of count
    and income as values.
    """
    try:
        zone_sheet = SHEET.worksheet('zones')
        data = zone_sheet.get_all_values()
        zone_data = {}
        for row in data[1:]:  # Skip header row
            zone_type = row[0]
            count = row[1].strip()
            income = row[2].strip()
            # Validate and convert count and income
            if count.isdigit():
                count = int(count)
            else:
                print(f"Invalid count for {zone_type}: {count}")
                count = 0
            try:
                income = float(income) if income else 0.0
            except ValueError:
                print(f"Invalid income for {zone_type}: {income}")
                income = 0.0
            zone_data[zone_type] = {
                'count': count,
                'income': income
            }
        return zone_data
    except GSpreadException as e:
        print(f"Google Sheets error fetching zone data: {e}")
        return {}


def initialize_grid(size):
    """
    Initialise an empty game grid with the specified size.

    Args:
        size (int): The size of the grid.

    Returns:
        list: A 2D list representing the empty game grid.
    """
    return [['-' for _ in range(size)] for _ in range(size)]


def initialize_random_grid(size, zone_data):
    """
    Initialise the game grid with random zones based on fetched counts.

    Args:
        size (int): The size of the grid.
        zone_data (dict): A dictionary containing zone types and their data.

    Returns:
        tuple: A tuple containing the initialied grid and the total daily
        income.
    """
    grid = [['-' for _ in range(size)] for _ in range(size)]
    positions = [(x, y) for x in range(size) for y in range(size)]
    random.shuffle(positions)  # Shuffle positions for random placement

    total_daily_income = 0
    for zone_type, data in zone_data.items():
        count = data['count']
        income = data['income']
        for _ in range(min(count, len(positions))):
            x, y = positions.pop()
            grid[x][y] = zone_type
            total_daily_income += income

    return grid, total_daily_income


def place_zone(grid, zone_type, x, y, player_resources):
    """
    Place a zone on the grid at the specified coordinates if enough resources
    are available.

    Args:
        grid (list): The game grid.
        zone_type (str): The type of zone to place.
        x (int): The x-coordinate.
        y (int): The y-coordinate.
        player_resources (dict): A dictionary containing the player's
        resources.
    """
    # Costs of resources
    zone_costs = {
        'Residential': 1250,
        'Commercial': 450,
        'Industrial': 450,
        'School': 100,
        'Hospital': 100}
    if player_resources['Money']['Current Value'] >= zone_costs[zone_type]:
        if grid[x][y] == '-':
            grid[x][y] = zone_type
            # Deduct the cost of zone from resources
            player_resources['Money']['Current Value'] -= zone_costs[zone_type]
            print(
                f"Congratulations, you built a {zone_type} & placed it at"
                f"{x}, {y}."
            )
            print(f"Remaining Money: {player_resources['Money']}")
        else:
            print("This plot is already occupied, please choose another plot")
    else:
        print("Sorry, you do not enough money to build this zone right now.")


def print_grid(grid):
    """
    Print the grid to the console with boxed borders and consistent alignment.
    Also prints a key to help players understand the symbols used for
    different zones.

    Args:
        grid (list): The game grid.
    """
    cell_width = 4

    print("      0   1   2   3   4   5   6   7   8   9")
    for index, row in enumerate(grid):
        # Print each row with a numerical label
        row_str = (
            f"{index:2} |" +
            "|".join(
                f"{ZONE_SYMBOLS.get(str(cell), '⚪'):^{cell_width}}"
                for cell in row
            ) +
            "|"
        )
        print(row_str)

    print()  # Ensure there's a new line after the grid for better spacing
    # Print the key
    key = """
    Key:
    🟢 - Residential
    🟣 - Commercial
    🟤 - Industrial
    🟡 - School
    🔴 - Hospital
    ⚪ - Empty space
    """
    print(Colour.BOLD + key + Colour.ENDC)


def get_resources():
    """
    Source and display resources from the 'resources' worksheet.
    """
    try:
        resources = SHEET.worksheet('resources')
        data = resources.get_all_values()
        print("\nCurrent Resources:")
        for row in data:
            print(row)
    except gspread.exceptions.WorksheetNotFound:
        print("Error: 'resources' worksheet not found.")


def fetch_player_resources():
    """
    Fetch player resources from the 'resources' worksheet
    and return as a dictionary.

    Returns:
        dict: A dictionary containing player resources.
    """
    player_resources = {}
    try:
        resources_sheet = SHEET.worksheet('resources')
        data = resources_sheet.get_all_records()  # Convert list to dictionary
        for res in data:
            resource_type = res['Resource Type']
            current_value = res['Current Value']
            regeneration_rate = res.get('Regeneration Rate', 0)
            # Comma removal and conversion of values
            if isinstance(current_value, str) and ',' in current_value:
                current_value = int(current_value.replace(',', ''))
            else:
                current_value = int(current_value)
            # Convert to float or default to 0.0 if empty
            regeneration_rate = (
                float(regeneration_rate) if regeneration_rate else 0.0
            )
            player_resources[resource_type] = {
                'Current Value': current_value,
                'Regeneration Rate': float(regeneration_rate)
            }
    except GSpreadException as e:
        print(f"Google Sheets error fetching player resources: {e}")
        return player_resources


def update_resources_in_sheet(player_resources):
    """
    Update the resources back to Google Sheets.

    Args:
        player_resources (dict):
        A dictionary containing the player's resources.
    """
    try:
        resources_sheet = SHEET.worksheet('resources')
        for resource_type, value in player_resources.items():
            # Find the cell with the resource type
            cell = resources_sheet.find(resource_type)
            # Update the next column
            resources_sheet.update_cell(cell.row, cell.col + 1, str(value))
    except GSpreadException as e:
        print(f"Google Sheets error updating resources: {e}")


def reset_resources_to_default():
    """Reset the resource values in the Google Sheet
    to their default amounts."""
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
            # Find the cell with the resource type
            cell = resources_sheet.find(resource)
            # Update the resource value to default
            resources_sheet.update_cell(cell.row, cell.col + 1, value)
        print("Resources have been reset to default values.")
    except GSpreadException as e:
        print(f"Google Sheets error resetting resources: {e}")


def regenerate_resources(player_resources, total_daily_income):
    """
    Regenerate resources daily and add daily income.

    Args:
        player_resources (dict): A dictionary containing the player resources.
        total_daily_income (float): The total daily income generated by zones.
    """
    for values in player_resources.items():
        # Apply the regeneration rate directly to the current value
        values['Current Value'] += values['Regeneration Rate']
    # Add daily income to the player's money
    player_resources['Money']['Current Value'] += total_daily_income


def print_resources(resources):
    """
    Print the player's resources in a formatted table.

    Args:
        resources (dict): A dictionary containing the player's resources.
    """
    header = (
        f"{Colour.HEADER}{'Resource Type':<20}{Colour.ENDC}"
        f"{Colour.HEADER}{'Current Value':<15}{Colour.ENDC}"
        f"{Colour.HEADER}{'Regeneration Rate':<15}{Colour.ENDC}"
    )
    print(Colour.BLUE + "Resources:" + Colour.ENDC)
    print(header)
    for key, value in resources.items():
        print(f"{key:<15} {value['Current Value']:10} "
              f"{value['Regeneration Rate']:15.2f}")
    print()


def handle_zone_action(grid, player_resources):
    """
    Handle the action of placing a zone and check resources.

    Args:
        grid (list): The game grid.
        player_resources (dict): A dictionary containing the player resources.
    """
    clear_screen()
    while True:
        try:
            x = int(input(f"Enter X coordinate to build a zone "
                          f"(0-{GRID_SIZE-1}): "))
            y = int(input(f"Enter Y coordinate to build a zone "
                          f"(0-{GRID_SIZE-1}): "))

            if 0 <= x < GRID_SIZE and 0 <= y < GRID_SIZE:
                zone_input = input(
                    "Enter zone type - R (Residential), C (Commercial),"
                    "I (Industrial), S (School), H (Hospital): "
                ).upper()

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
                    break
                else:
                    print("Invalid. Please use 'R', 'C', 'I', 'S', or 'H'")
            else:
                print(
                    f"Invalid coordinates. Please enter values between 0 "
                    f"and {GRID_SIZE - 1}."
                )
        except ValueError:
            print("Invalid input. Please enter numeric grid coordinates.")


def fetch_events():
    """
    Fetch event data from the Google Sheet.

    Returns:
        list: A list of dictionaries containing event data.
    """
    events_sheet = SHEET.worksheet('events')
    events = events_sheet.get_all_records()
    # Initialise all events as inactive with specified duration
    for event in events:
        event['Active'] = False
        event['Duration'] = int(event.get('Duration', 0))
    return events


def apply_random_event(events, player_resources):
    """
    Randomly select and apply an event effect if it's not currently active,
    and handle event duration.

    Args:
        events (list): A list of dictionaries containing event data.
        player_resources (dict): A dictionary containing the resources.
        day (int): The current day in the game.
    """
    active_events = [event for event in events if event['Active']]
    for event in active_events:
        if event['Duration'] > 0:
            print(
                f"Oh no, an event is impacting the city:"
                f"{event['Description']} "
                f"resulting in {event['Impact Type']}"
                f"of {event['Impact Value']}. "
                f"Days left: {event['Duration']}"
            )
            apply_impact(
                player_resources, event['Impact Type'], event['Impact Value']
            )
            event['Duration'] -= 1
        if event['Duration'] <= 0:
            event['Active'] = False

    if not any(event['Active'] for event in events):
        new_event = random.choice(events)
        if not new_event['Active']:
            new_event['Active'] = True
            new_event['Duration'] = int(new_event.get('Duration', 1))
            print(
                f"Oh no, a new event has started: {new_event['Description']} "
                f"resulting in {new_event['Impact Type']}"
                f" by {new_event['Impact Value']} "
                f"for {new_event['Duration']} days."
            )
            apply_impact(
                player_resources,
                new_event['Impact Type'],
                new_event['Impact Value']
            )


def apply_impact(player_resources, impact_type, impact_value):
    """
    Apply the calculated impact to the player's resources.

    Args:
        player_resources (dict): A dictionary containing the player resources.
        impact_type (str): The type of impact.
        impact_value (str): The value of the impact.
    """
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

    # Apply the calculated impact to the player's resources.
    if '%' in impact_value:
        modifier = float(impact_value.strip('%')) / 100
        player_resources[adjusted_impact_type]['Current Value'] *= (
            1 - modifier
        )
    else:
        player_resources[adjusted_impact_type]['Current Value'] += (
            float(impact_value)
        )

    print(
        f"{adjusted_impact_type} after impact: "
        f"{player_resources.get(adjusted_impact_type)}"
    )


def update_resource(player_resources, resource_type, impact_value):
    """
    Update a specific resource based on an impact value.

    Args:
        player_resources (dict): A dictionary containing the resources.
        resource_type (str): The type of resource to update.
        impact_value (str): The value of the impact.
    """
    if '%' in impact_value:
        modifier = float(impact_value.strip('%')) / 100
        player_resources[resource_type] *= (1 + modifier)
    else:
        player_resources[resource_type] += float(impact_value)


def fetch_metrics():
    """
    Fetch the initial metrics for the game.

    Returns:
        dict: A dictionary containing the initial metrics.
    """
    return {
        'Employment Rate': 70,
        'Crime Rate': 5,
        'Happiness Index': 75,
        'Health': 80
    }


def check_metrics(metrics):
    """
    Check if any metrics have fallen below or above critical levels.

    Args:
        metrics (dict): A dictionary containing the current metrics.

    Returns:
        bool: True if all metrics are within acceptable levels, False if not.
    """
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
    """
    Update the metrics based on the type and amount of zone built.

    Args:
        metrics (dict): A dictionary containing the current metrics.
        zone_type (str): The type of zone built.
        amount (int): The number of zones built.
    """
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
    """
    Print the current metrics in a formatted table.

    Args:
        metrics (dict): A dictionary containing the current metrics.
    """
    header = (
        f"{Colour.HEADER}{'Metric Type':<27}{Colour.ENDC}"
        f"{Colour.HEADER}{'Value (%)':<27}{Colour.ENDC}"
    )
    print(Colour.GREEN + "Metrics:" + Colour.ENDC)
    print(header)
    for key, value in metrics.items():
        print(f"{key:<20} {value:10}%")
    print()


def print_help():
    """
    Print the help message displaying available commands.
    """
    print("Commands available:")
    print("  build - Place a new zone.")
    print("  next - Move to the next day.")
    print("  restart - Restart the game.")
    print("  help - Show this help message.")


def confirm_restart():
    """
    Confirm the decision to restart the game.

    Returns:
        bool: True if the player confirms restart, False otherwise.
    """
    response = input("Are you sure you want to restart the game? (yes/no): ")
    return response.lower() == 'yes'


def confirm_exit():
    """
    Confirm before exiting the game.

    Returns:
        bool: True if the player confirms exit, False otherwise.
    """
    # Confirm before exiting the game
    confirm = input(
        "Are you sure you want to exit the game? (yes/no): "
    ).lower()
    return confirm == 'yes'


def main():
    """
    Main function to run the game.

    Initialises the game, handles the main game loop, and manages game state.
    """
    show_intro()  # Show introduction and instructions at the start
    monetary_goal = 200000
    # Minimum / maximum acceptable metric values
    min_metrics = {
        'Employment Rate': 50,
        'Crime Rate': 50,
        'Happiness Index': 50,
        'Health': 50
    }
    while True:
        zone_data = fetch_zone_data()
        events = fetch_events()
        player_resources = fetch_player_resources()
        metrics = fetch_metrics()
        current_day = 1  # Start the day counter
        if zone_data:
            grid, total_daily_income = initialize_random_grid(
                GRID_SIZE, zone_data
            )
        else:
            # If fetching fails, fallback to an empty grid
            grid, total_daily_income = initialize_grid(GRID_SIZE), 0
        game_over = False
        while current_day <= 30 and not game_over:
            clear_screen()
            print("McGee Metropolis City Map:")
            print_grid(grid)
            print("\nCurrent Resources and Metrics:")
            # Function to print resources in a formatted table
            print_resources(player_resources)
            # Function to print metrics in a formatted table
            print_metrics(metrics)

            print(f"Day {current_day}: Good Morning! A New day has started...")
            apply_random_event(events, player_resources)
            regenerate_resources(player_resources, total_daily_income)
            if not check_metrics(metrics):
                print(
                    "One or more metrics have reached critical levels. "
                    "The game is over, better luck next time!"
                )
                game_over = True
                continue

            action = input(
                "\nChoose the action you would like to take:"
                "1. Build a zone"
                "2. Go to the next day"
                "3. Access help"
                "4. Exit the game: (zone/next/help/exit): "
            ).lower()
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
                    player_resources = fetch_player_resources()
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
                print("Invalid. Choose 'zone', 'next', 'help', or 'exit'.")

            update_resources_in_sheet(player_resources)
        if not game_over and current_day > 30:
            if (
                player_resources['Money']['Current Value'] >= monetary_goal and
                all(
                    metrics[m] >= min_metrics[m]
                    for m, _ in min_metrics.items()
                )
            ):
                print(
                    "Congratulations! You have reached your goals and won!"
                )
            else:
                print("Unfortunately, you did not meet the goals. Game over.")
        if not confirm_restart():
            print("Exiting the game.")
            break
        print("Current Resources and Metrics:")
        print_resources(player_resources)
        print_metrics(metrics)


if __name__ == "__main__":
    main()
