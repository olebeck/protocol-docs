import os
import subprocess
import glob
import re
import shutil

PROTOCOL_JAR = "./ProtocolParser/build/libs/ProtocolParser.jar"
INPUT_DIR = "./bedrock-protocol-docs/"
OUTPUT_DIR = "protocol-docs"


def build_protocol_parser():
    if os.path.exists(PROTOCOL_JAR):
        return
    subprocess.run(["gradle", "shadowJar"], cwd="./ProtocolParser", shell=True)


# returns list[(branch, git_hash)]
def get_converted_heads():
    converted_heads = []
    if os.path.exists(OUTPUT_DIR):
        for git_hash_file in glob.glob("**/.git_hash", root_dir=OUTPUT_DIR, recursive=True):
            git_hash_file = git_hash_file.replace("\\", "/")
            branch_dir = os.path.dirname(git_hash_file)
            with open(os.path.join(OUTPUT_DIR, git_hash_file), "r") as f:
                git_hash = f.read().strip()
            converted_heads.append((branch_dir, git_hash))
                    
    return converted_heads


def fetch_mojang_repo():
    if not os.path.exists("bedrock-protocol-docs"):
        subprocess.run(["git", "clone", "https://github.com/Mojang/bedrock-protocol-docs/"])
    subprocess.run(["git", "-C", "bedrock-protocol-docs", "fetch", "--all"])


# returns list[(branch, git_hash)]
def get_mojang_repo_heads():
    heads = []
    subprocess.run(
        ["git", "-C", "bedrock-protocol-docs", "fetch", "--all"],
        check=True,
    )
    result = subprocess.run(
        ["git", "-C", "bedrock-protocol-docs", "branch", "-r"],
        capture_output=True,
        text=True,
        check=True,
    )
    branches = result.stdout.strip().split("\n")
    for branch in branches:
        branch = branch.strip().replace("origin/", "").split(" ")[0]
        if branch in ("HEAD"):
            continue
        result = subprocess.run(
            ["git", "-C", "bedrock-protocol-docs", "rev-parse", f"origin/{branch}"],
            capture_output=True,
            text=True,
            check=True,
        )
        git_hash = result.stdout.strip()
        heads.append((branch, git_hash))
    return heads


def get_need_update(converted, mojang_heads):
    need_update = []
    converted_dict = dict(converted)
    mojang_dict = dict(mojang_heads)
    
    for branch, mojang_hash in mojang_dict.items():
        if branch not in converted_dict or converted_dict[branch] != mojang_hash:
            need_update.append((branch, mojang_hash))
    return need_update


def checkout_branch(repo, branch_name):
    subprocess.run(["git", "-C", repo, "checkout", branch_name], check=True)

with open("layout.html", "r") as f:
    layout = f.read()

def with_layout(title, base, content):
    output = layout
    output = output.replace("{TITLE}", title)
    output = output.replace("{BASE}", base)
    output = output.replace("{CONTENT}", content)
    return output

def main():
    build_protocol_parser()
    fetch_mojang_repo()
    converted = get_converted_heads()
    mojang_heads = get_mojang_repo_heads()
    need_update = get_need_update(converted, mojang_heads)
    for (branch_name, git_hash) in need_update:
        output_dir = os.path.join(OUTPUT_DIR, branch_name)
        checkout_branch("bedrock-protocol-docs", branch_name)
        try:
            subprocess.run(["java", "-jar", PROTOCOL_JAR, "-i", INPUT_DIR, "-o", output_dir], check=True)
        except Exception as e:
            print(e)
            continue
        md_files = glob.glob(os.path.join(output_dir, "**/*.md"), recursive=True)
        for md_file in md_files:
            md_file = md_file.replace("\\", "/")
            html_file = os.path.splitext(md_file)[0] + ".html"
            subprocess.run(["showdown", "-q", "makehtml", "-p", "github", "-i", md_file, "-o", html_file], check=True, shell=True)
            with open(html_file, "r") as f:
                content = f.read()
            
            content = re.sub(r'href="([^"]+?)\.md"', r'href="\1.html"', content)
            base = "../" * (md_file.count("/")-1)

            if title := re.match(r"<h1 [^>]*>([^<]*)</h1>", content):
                title = title.group(1)
            else:
                title = ""

            output = with_layout(title, base, content)
            with open(html_file, "w") as f:
                f.write(output)

        # folder indexes
        folders = ["enums", "packets", "types"]
        for folder in folders:
            base = "../" * (folder.count("/") + branch_name.count("/"))
            filenames = [a for a in os.listdir(os.path.join(output_dir, folder)) if a.endswith(".html")]
            with open(os.path.join(output_dir, folder, "index.html"), "w") as f:
                title = f"{branch_name} {folder}"
                content = f"<h1>{branch_name} {folder}</h1>\n<ul>"
                for filename in filenames:
                    name = filename.split(".")[0]
                    content += f"<li><a href=\"{filename}\">{name}</a></li>\n"
                content += "</ul>"
                f.write(with_layout(title, "../../", content))

        # branch index
        with open(os.path.join(output_dir, "index.html"), "w") as f:
            base = "../" * (branch_name.count("/")+1)
            title = f"{branch_name} Protocol Docs"
            content = f"<h1>{branch_name}</h1>\n<ul>"
            content += f"<li><a href=\"packets.html\">packets</a></li>\n"
            folders = ["enums", "types"]
            for folder in folders:
                content += f"<li><a href=\"{folder}/\">{folder}</a></li>\n"
            content += "</ul>"
            f.write(with_layout(title, base, content))

        # git_hash
        with open(os.path.join(output_dir, ".git_hash"), "w") as f:
            f.write(git_hash)

    # branches index
    branch_names = [b[0] for b in mojang_heads]
    with open(os.path.join(OUTPUT_DIR, "index.html"), "w") as f:
        title = "Protocol Docs"
        content = "<h1>Versions</h1>\n<ul>"
        for name in branch_names:
            content += f"<li><a href=\"{name}/\">{name}</a></li>\n"
        content += "</ul>"
        f.write(with_layout(title, "", content))

    shutil.copyfile("main.css", os.path.join(OUTPUT_DIR, "main.css"))

main()