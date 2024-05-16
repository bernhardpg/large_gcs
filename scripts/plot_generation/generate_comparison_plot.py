import argparse
from pathlib import Path

from large_gcs.visualize.plot_sampling_comparison import SamplingRunData, SingleRunData


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Load data and configuration from a specified directory."
    )
    parser.add_argument(
        "--dir",
        type=str,
        help="Path to the directory containing data and config file",
        required=True,
    )
    parser.add_argument(
        "--ah_dir",
        type=str,
        help="Path to the directory containing data and config file for the AH-containment comparison",
        default=None,
    )

    # Parse the arguments
    args = parser.parse_args()

    data_dir = Path(args.dir)

    # Validate the directory
    if not data_dir.is_dir():
        print(f"The directory {data_dir} does not exist.")
        return

    run_data = SamplingRunData.load_from_folder(data_dir)

    if args.ah_dir is not None:
        ah_comparison_data_dir = Path(args.ah_dir)
        ah_run_data = SamplingRunData.load_from_folder(ah_comparison_data_dir)
        ah_run_data.save(ah_comparison_data_dir / "aggregated_run_data.json")

        assert len(ah_run_data.data) == 1
        assert type(ah_run_data.data[0]) is SingleRunData
        ah_data = ah_run_data.data[0]

        run_data.make_plot(ah_data)
    else:
        run_data.make_plot()


if __name__ == "__main__":
    main()