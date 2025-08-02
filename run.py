import os
import subprocess
import sys

def run_command(command, interactive=False):
    """Run a command and print its output
    
    Args:
        command: Command to execute as a list of strings
        interactive: If True, run in interactive mode (for commands that require user input)
    """
    print(f"Executing: {' '.join(command)}")
    
    if interactive:
        # Run interactively - allows user input
        result = subprocess.run(command)
        return result.returncode
    else:
        # Capture output - for non-interactive commands
        result = subprocess.run(command, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print(result.stderr, file=sys.stderr)
        return result.returncode

def main():
    # Check if Python virtual environment is active
    if not os.environ.get('VIRTUAL_ENV'):
        print("Warning: It's recommended to run this script in a virtual environment.")
        response = input("Continue without virtual environment? (y/n): ")
        if response.lower() != 'y':
            print("Exiting. Please activate a virtual environment and try again.")
            return 1

    # Install requirements
    print("\n=== Installing requirements ===")
    if run_command([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"]) != 0:
        print("Failed to install requirements. Exiting.")
        return 1

    # Run migrations
    print("\n=== Running migrations ===")
    if run_command([sys.executable, "manage.py", "makemigrations"]) != 0:
        print("Failed to make migrations. Exiting.")
        return 1

    if run_command([sys.executable, "manage.py", "migrate"]) != 0:
        print("Failed to apply migrations. Exiting.")
        return 1

    # Initialize data
    print("\n=== Initializing data ===")
    if run_command([sys.executable, "manage.py", "initialize_data"]) != 0:
        print("Failed to initialize data. Exiting.")
        return 1

    # Create superuser if needed
    print("\n=== Checking for superuser ===")
    result = subprocess.run(
        [sys.executable, "manage.py", "shell", "-c", 
         "from django.contrib.auth import get_user_model; print(get_user_model().objects.filter(is_superuser=True).exists())"],
        capture_output=True, text=True
    )
    
    if "True" not in result.stdout:
        print("No superuser found. Creating one...")
        print("Please provide credentials for the admin user:")
        run_command([sys.executable, "manage.py", "createsuperuser"], interactive=True)
    else:
        print("Superuser already exists.")

    # Run the server
    print("\n=== Starting server ===")
    print("The application is now running at http://127.0.0.1:8000/")
    print("Press Ctrl+C to stop the server.")
    return run_command([sys.executable, "manage.py", "runserver"], interactive=True)

if __name__ == "__main__":
    sys.exit(main())