import requests
import re
import json
import base64


JS_URL = "https://lchdxfootball.pages.dev/cricxfootball.js"

KEY = "gf676rc7gr4grg76r6ag56gg8f76713f"

OUTPUT = "decoded_channels.json"


def decrypt_base64(data, key):
    decoded = base64.b64decode(data)

    result = bytearray()

    for i, b in enumerate(decoded):
        result.append(
            b ^ ord(key[i % len(key)])
        )

    text = result.decode("utf-8")

    return json.loads(text)


# JS file download
js = requests.get(JS_URL).text


# encodedChannelData block nikalo
match = re.search(
    r"const\s+encodedChannelData\s*=\s*{(.*?)};",
    js,
    re.S
)

if not match:
    raise Exception("encodedChannelData not found")


block = match.group(1)


# Saare entries extract karo
channels = dict(
    re.findall(
        r'(\w+)\s*:\s*"([^"]+)"',
        block
    )
)


print("Found channels:", len(channels))


decoded = {}


for name, encrypted in channels.items():

    try:
        data = decrypt_base64(
            encrypted,
            KEY
        )

        decoded[name] = data

        print("Decoded:", name)

    except Exception as e:
        print(
            "Failed:",
            name,
            e
        )


# JSON save
with open(
    OUTPUT,
    "w",
    encoding="utf-8"
) as f:

    json.dump(
        decoded,
        f,
        indent=4,
        ensure_ascii=False
    )


print("\nSaved:", OUTPUT)
