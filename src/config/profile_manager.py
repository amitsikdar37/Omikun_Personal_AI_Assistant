import yaml

def load_profile(path="user_profile.yaml"):
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def profile_to_text(profile):
    lines = []
    for k, v in profile.items():
        if isinstance(v, list):
            lines.append(f"{k.capitalize()}: {', '.join(str(x) for x in v)}")
        else:
            lines.append(f"{k.capitalize()}: {v}")
    return "\n".join(lines)
