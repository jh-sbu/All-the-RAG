from pathlib import Path

pairs = []

for line in Path(".env.deploy").read_text().splitlines():
    line = line.strip()
    if not line or line.startswith("#"):
        continue

    param_name, param_value, _ = line.split('"')
    param_name, _ = param_name.split("=")

    # print(f"param_name: {param_name}")
    # print(f"param_value: {param_value}")

    pairs.append((param_name, param_value))

strings = [f'{param_name}=\\"{param_value}\\"' for param_name, param_value in pairs]

# for string in strings:
#     print(f"String: {string}")

final_string = " ".join(strings)

with open("samconfig.toml", "r") as f:
    lines = f.readlines()

lines = [
    f'parameter_overrides = "{final_string}"\n'
    if line.startswith("parameter_overrides = ")
    else line
    for line in lines
]

with open("samconfig.toml", "w") as f:
    f.writelines(lines)
