def progress_bar(progress, total) -> None:
  percent = 100 * (progress / float(total))
  bar = "#" * int(percent) + "-" * (100 - int(percent))
  print(f"\r|{bar}| {percent:.2f}%", end="\r")


if __name__ == "__main__":
  import platform
  import subprocess
  import sys

  total = 5
  os_name = platform.system()
  print("Setting up thinkledger for ", os_name)

  try:
    progress_bar(1, total)

    # Install npm packages
    subprocess.run(
      ["npm", "install"],
      stdout=subprocess.DEVNULL,
      stderr=subprocess.STDOUT,)
    progress_bar(2, total)

    if os_name == "Darwin" or os_name == "Linux":
      # Install uv
      subprocess.run(
        "curl -LsSf https://astral.sh/uv/install.sh | sh",
        shell=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.STDOUT,
        executable="/bin/bash")
      progress_bar(3, total)

      # Install dependencies
      subprocess.run(
        "uv sync",
        shell=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.STDOUT,
        executable="/bin/bash")
      progress_bar(4, total)

      # Install tide
      subprocess.run(
        "curl -LsSf https://raw.githubusercontent.com/builtbyjb/tide/main/install.sh | sh",
        shell=True,
        executable="/bin/bash")
      progress_bar(5, total)
      print("\nSetup complete. Quick start: DEBUG=2 python3 main.py")

    elif os_name == "Windows":
      # Install uv
      subprocess.run(
        'powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"',
        shell=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.STDOUT)
      progress_bar(3, total)

      # Install dependencies
      subprocess.run(
        "uv sync",
        shell=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.STDOUT)
      progress_bar(4, total)

      # Install tide
      subprocess.run(
        'powershell -ExecutionPolicy ByPass -c "irm https://raw.githubusercontent.com/builtbyjb/tide/main/install.ps1 | iex"', # noqa: E501
        shell=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.STDOUT)
      progress_bar(5, total)
      print("\nSetup complete. Quick start: set DEBUG=2 && python main.py")

    else:
      print("Unable to determine operating system.")
      sys.exit(1)

  except FileNotFoundError as f_err:
    print(f_err)
    sys.exit(1)

  except Exception as e:
    print(e)
    sys.exit(1)

  # Progress_bar
  sys.exit(0)
