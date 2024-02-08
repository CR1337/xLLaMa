from _util import (
    GREEN, MODELS, dash_local_suffix, print_color, run_program, post_request,
    install_model_request, get_request
)


def main():
    run_program(
        ["sh", f"./bin/stop{dash_local_suffix}"],
        "Stopping docker services...",
        "Successfully stopped docker services",
        "Failed to stop docker services"
    )
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
    get_request(
        5001,
        "/models",
        "Checking models...",
        "Successfully checked models",
        "Failed to check models"
    )
    run_program(
        ["sh", f"./bin/stop{dash_local_suffix}"],
        "Stopping docker services...",
        "Successfully stopped docker services",
        "Failed to stop docker services"
    )
    run_program(
        ["sh", f"./bin/run{dash_local_suffix}"],
        "Starting docker services...",
        "Successfully started docker services",
        "Failed to started docker services"
    )
    print_color("Setup complete!", GREEN)


if __name__ == "__main__":
    main()
