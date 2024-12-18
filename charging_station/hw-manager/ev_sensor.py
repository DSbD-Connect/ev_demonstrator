import subprocess


def get_random_value():
    try:
        # Call the compiled C program
        result = subprocess.run(['./ev_sensor'], capture_output=True, text=True, check=True)

        # Print the output from the C program
        print("Output from C program:")
        print(result.stdout.strip())

    except subprocess.CalledProcessError as e:
        print("Error occurred while calling the C program:")
        print(e.stderr)


if __name__ == "__main__":
    get_random_value()
