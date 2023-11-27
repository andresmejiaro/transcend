import subprocess
import json

# NOT WORKING YET

def run_test(command):
    print(f"\033[94mRunning test: {command}\033[0m")
    result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, encoding="utf-8")
    
    # Check the response status
    print(f"\033[92mOutput: {result.stdout}\033[0m")
    data = result.stdout.split("\n")[1]
    status_code = data.split(" ")[2]

    # If the response status is 200, print "Test passed" in green
    if status_code == "200":
        print("\033[92mTest passed\033[0m\n")
    else:
        # If the response status is not 200, print the response status in red
        print(f"\033[91mTest failed\033[0m")
        print(f"\033[91mResponse Status: {status_code}\033[0m")
        
        # If there's an error message, print it in red
        if result.stderr:
            print(f"\033[91mError message: {result.stderr}\033[0m")
    print('==============================================================')

def test_api_endpoint(model, pk, create_data, update_data):
    create_endpoint = f"{model}/create/"

    # Create Test
    run_test(f"python3 apitester.py {create_endpoint} POST --data '{json.dumps(create_data)}'")

    list_endpoint = f"{model}/"
    update_endpoint = f"{model}/{pk}/"
    delete_endpoint = f"{model}/{pk}/"
    view_detail_endpoint = f"{model}/{pk}/"

    # List Test
    # run_test(f"python3 apitester.py {list_endpoint} GET")

    # View Details Test
    run_test(f"python3 apitester.py {view_detail_endpoint} GET")

    # Update Test
    run_test(f"python3 apitester.py {update_endpoint} PUT --data '{json.dumps(update_data)}'")

    # Delete Test
    run_test(f"python3 apitester.py {delete_endpoint} DELETE")

# Example usage for the "tournament" model
model_name = "tournament"
primary_key = "37"
create_data = {
    "name": "Awesome2 Tournament2",
    "start_date": None,
    "end_date": None,
    "round": 2,
    "players": [74, 144],
    "observers": [69]
}
update_data = {
    "name": "Awesome2 Tournament2",
    "start_date": None,
    "end_date": None,
    "round": 2,
    "players": [74, 144],
    "observers": [66]
}

test_api_endpoint(model_name, primary_key, create_data, update_data)
