import os

# directory where this script is located
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

for filename in os.listdir(BASE_DIR):
    if filename.lower().endswith(".txt"):
        old_path = os.path.join(BASE_DIR, filename)

        name, ext = os.path.splitext(filename)
        new_name = f"{name}_renamed{ext}"
        new_path = os.path.join(BASE_DIR, new_name)

        # avoid overwriting
        if not os.path.exists(new_path):
            os.rename(old_path, new_path)
            print(f"Renamed: {filename} -> {new_name}")
        else:
            print(f"Skipped (already exists): {new_name}")
