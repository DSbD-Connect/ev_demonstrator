import subprocess


def fetch_card_provider(card_number, expire_date, cvv, amount, cheri_comp_on):

    if cheri_comp_on:
        executable = "./payment_comp"
    else:
        executable = "./payment_nocomp"

    command_str = executable + " " + \
        card_number + " " + expire_date + " " + \
        cvv + " " + amount

    result = subprocess.run(command_str, shell=True,
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output = result.stdout.decode(errors='replace')  # Replace invalid bytes
    # error_output = result.stderr.decode(errors='replace')
    return output
