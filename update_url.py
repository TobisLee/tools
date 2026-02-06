import sys


def update_file(file_path):
    print(f"Processing {file_path}...")

    with open(file_path, "r") as f:
        lines = f.readlines()

    new_lines = []
    changes_count = 0

    for line in lines:
        # We look for the specific old pattern in the file: ${GITLAB_IP}\:28443\/
        if "${GITLAB_IP}\\:28443\\/" in line:
            # Split by the old string to isolate the "replacement" part of the sed command
            parts = line.split("${GITLAB_IP}\\:28443\\/")

            if len(parts) > 1:
                # Reconstruct the line:
                # 1. Everything before the match (parts[0])
                # 2. The NEW Host string
                # 3. The rest of the line (parts[1:]), with protocol=https -> protocol=ssh

                new_line = parts[0] + "${GITLAB_HOST}:"

                for part in parts[1:]:
                    if "protocol=https" in part:
                        part = part.replace("protocol=https", "protocol=ssh")
                    new_line += part

                new_lines.append(new_line)
                changes_count += 1
            else:
                new_lines.append(line)
        else:
            new_lines.append(line)

    with open(file_path, "w") as f:
        f.writelines(new_lines)

    print(f"Done. Modified {changes_count} lines in {file_path}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 update_gitlab_urls.py <path_to_your_shell_script>")
        sys.exit(1)

    update_file(sys.argv[1])