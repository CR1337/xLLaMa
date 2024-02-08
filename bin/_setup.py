from _util import (
    GREEN, MODELS, dash_local_suffix, dot_local_suffix, print_color,
    run_program, ask_for_integer, set_environment, copy_file
)
from _requests import post_request, install_model_request


def main():
    gpu_amount = ask_for_integer(
        "How many GPUs do you want to use? ([0..2] default: 0)>",
        0, 2, 1
    )
    print()
    gpu_indices = [
        ask_for_integer(
            f"Which GPU do you want to use for instance {i}? ([0..256])>",
            0, 256
        )
        for i in range(gpu_amount)
    ]
    print()
    copy_file(
        f".env.template{dot_local_suffix}",
        ".env",
        f"Copying .env.template{dot_local_suffix} to .env...",
        f"Successfully copied .env.template{dot_local_suffix} to .env",
        f"Failed to copy .env.template{dot_local_suffix} to .env"
    )
    set_environment(gpu_indices)
    run_program(
        ["sh", f"./bin/build{dash_local_suffix}"],
        "Building docker services...",
        "Successfully built docker services",
        "Failed to build docker services"
    )
    run_program(
        ["sh", f"./bin/run{dash_local_suffix}"],
        "Starting docker services...",
        "Successfully started docker services",
        "Failed to started docker services"
    )
    post_request(
        5003,
        "/db/reset",
        "Resetting database...",
        "Successfully reset database",
        "Failed to reset database"
    )
    post_request(
        5003,
        "/db/populate",
        "Populating database...",
        "Successfully populated database",
        "Failed to populate database"
    )
    for model in MODELS:
        install_model_request(
            model,
            f"Installing model {model}...",
            f"Successfully installed model {model}",
            f"Failed to install model {model}"
        )
    run_program(
        ["sh", f"./bin/stop{dash_local_suffix}"],
        "Stopping docker services...",
        "Successfully stopped docker services",
        "Failed to stop docker services"
    )
    print_color("Setup complete!", GREEN)


if __name__ == "__main__":
    main()
