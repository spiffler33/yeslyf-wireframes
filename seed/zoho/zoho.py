#!/usr/bin/env python3
"""Shared Zoho client for the phase F provisioning (seed/zoho/): the India datacentre endpoints, the OAuth
self-client flow, HTTP with backoff, and the run log. Python 3 standard library only.

Credentials: seed/zoho/.env (gitignored) holds ZOHO_CLIENT_ID and ZOHO_CLIENT_SECRET, copied by hand from the
Self Client at api-console.zoho.in. The refresh token never goes in the repo: `auth` writes it, with the cached
access token, to seed/zoho/.local/token.json (gitignored). Tokens are never printed.

Usage:
    python3 seed/zoho/zoho.py auth <grant code>   exchange a Self Client grant code (Generate Code tab) once
    python3 seed/zoho/zoho.py check                refresh the access token; print the CRM org, Desk portal and
                                                   Bookings workspaces it reaches
"""
import datetime
import http.client
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import uuid

HERE = os.path.dirname(os.path.abspath(__file__))
ENV_FILE = os.path.join(HERE, ".env")
LOCAL = os.path.join(HERE, ".local")
TOKEN_FILE = os.path.join(LOCAL, "token.json")

# India datacentre. The upload host is the IN one from the bulk write upload-file page (upload-accl.zoho.in); the
# Bookings API sits under www.zohoapis.in (Bookings domain-specific API URLs page).
ACCOUNTS = "https://accounts.zoho.in"
API = "https://www.zohoapis.in"
UPLOAD = "https://upload-accl.zoho.in"
DESK = "https://desk.zoho.in/api/v1"
CAMPAIGNS = "https://campaigns.zoho.in/api/v1.1"
BOOKINGS = API + "/bookings/v1/json"

# 429 is the documented throttle answer (CRM TOO_MANY_REQUESTS, Desk TOO_MANY_REQUESTS / THRESHOLD_EXCEEDED); 5xx
# are retried the same way. Retry-After is honoured when a service sends it (Desk documents it).
RETRY_STATUS = {429, 500, 502, 503, 504}
BACKOFF = [2, 4, 8, 16, 32, 64, 120]
RETRY_AFTER_CAP = 300

IST = datetime.timezone(datetime.timedelta(hours=5, minutes=30))


class ApiError(Exception):
    def __init__(self, status, body, method, url):
        self.status, self.body, self.method, self.url = status, body, method, url
        super().__init__("%s %s -> HTTP %s: %s" % (method, url, status, short(body)))

    def code(self):
        # CRM: {"code": ...} or {"data": [{"code": ...}]}; Desk: {"errorCode": ...}; token errors: {"error": ...}
        b = self.body
        if isinstance(b, dict):
            if isinstance(b.get("data"), list) and b["data"] and isinstance(b["data"][0], dict):
                return b["data"][0].get("code") or ""
            return b.get("code") or b.get("errorCode") or b.get("error") or ""
        return ""


def short(body, n=400):
    text = body if isinstance(body, str) else json.dumps(body, sort_keys=True)
    return text if len(text) <= n else text[:n] + "..."


def now_ist():
    return datetime.datetime.now(IST)


def stamp():
    # the operator page's "done by script" timestamp, e.g. "24 Sep 2026, 16:05 IST"
    t = now_ist()
    return "%d %s, %s IST" % (t.day, t.strftime("%b %Y"), t.strftime("%H:%M"))


_log_path = None


def log(msg):
    global _log_path
    line = "%s %s" % (now_ist().strftime("%H:%M:%S"), msg)
    print(line, flush=True)
    os.makedirs(LOCAL, exist_ok=True)
    if _log_path is None:
        _log_path = os.path.join(LOCAL, "run-%s.log" % now_ist().strftime("%Y%m%d-%H%M%S"))
    with open(_log_path, "a") as fh:
        fh.write(line + "\n")


def load_env():
    # KEY=VALUE lines; blank lines and "#" comments skipped. Closed format we write the instructions for.
    if not os.path.exists(ENV_FILE):
        raise SystemExit("missing %s: put ZOHO_CLIENT_ID=... and ZOHO_CLIENT_SECRET=... in it (Self Client, "
                         "api-console.zoho.in)" % ENV_FILE)
    env = {}
    with open(ENV_FILE) as fh:
        for raw in fh:
            line = raw.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, value = line.partition("=")
            env[key.strip()] = value.strip().strip('"').strip("'")
    for key in ("ZOHO_CLIENT_ID", "ZOHO_CLIENT_SECRET"):
        if not env.get(key):
            raise SystemExit("%s has no %s" % (ENV_FILE, key))
    return env


def _save_token(tok):
    os.makedirs(LOCAL, exist_ok=True)
    tmp = TOKEN_FILE + ".tmp"
    with open(tmp, "w") as fh:
        json.dump(tok, fh, indent=1, sort_keys=True)
    os.chmod(tmp, 0o600)
    os.replace(tmp, TOKEN_FILE)


def _token_call(params):
    data = urllib.parse.urlencode(params).encode()
    for attempt, wait in enumerate(BACKOFF[:4] + [None]):
        req = urllib.request.Request(ACCOUNTS + "/oauth/v2/token", data=data, method="POST",
                                     headers={"Content-Type": "application/x-www-form-urlencoded"})
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                body = json.loads(resp.read().decode() or "{}")
            break
        except urllib.error.HTTPError as e:
            raise SystemExit("token request refused: HTTP %s %s" % (e.code, e.read().decode(errors="replace")[:300]))
        except (OSError, http.client.HTTPException) as e:
            if wait is None:
                raise SystemExit("token request failed: %s" % e)
            log("  backoff %ss after a network error on the token request" % wait)
            time.sleep(wait)
    if "error" in body:
        # never echo the request; the body carries no secret
        raise SystemExit("token request refused: %s" % body.get("error"))
    return body


def auth(code):
    env = load_env()
    body = _token_call({"grant_type": "authorization_code", "client_id": env["ZOHO_CLIENT_ID"],
                        "client_secret": env["ZOHO_CLIENT_SECRET"], "code": code})
    if not body.get("refresh_token"):
        raise SystemExit("no refresh token in the answer; generate a fresh code and run auth again")
    if body.get("api_domain") and body["api_domain"] != API:
        raise SystemExit("this grant is for %s, not the India datacentre %s" % (body["api_domain"], API))
    _save_token({"refresh_token": body["refresh_token"], "access_token": body.get("access_token", ""),
                 "expires_at": time.time() + int(body.get("expires_in", 3600)), "api_domain": body.get("api_domain", ""),
                 "scope": body.get("scope", "")})
    print("refresh token stored in %s (gitignored, mode 600)" % os.path.relpath(TOKEN_FILE))


class Client:
    """One access token per run, refreshed from the stored refresh token only when it is within two minutes of
    expiry (Zoho allows ten access tokens per refresh token per ten minutes)."""

    def __init__(self):
        if not os.path.exists(TOKEN_FILE):
            raise SystemExit("no token yet: run python3 seed/zoho/zoho.py auth <grant code>")
        with open(TOKEN_FILE) as fh:
            self.tok = json.load(fh)
        self.env = load_env()
        self.desk_org = None
        self.forced_at = 0.0

    def token(self, force=False):
        if force or not self.tok.get("access_token") or self.tok.get("expires_at", 0) - time.time() < 120:
            body = _token_call({"grant_type": "refresh_token", "refresh_token": self.tok["refresh_token"],
                                "client_id": self.env["ZOHO_CLIENT_ID"], "client_secret": self.env["ZOHO_CLIENT_SECRET"]})
            self.tok["access_token"] = body["access_token"]
            self.tok["expires_at"] = time.time() + int(body.get("expires_in", 3600))
            _save_token(self.tok)
        return self.tok["access_token"]

    def request(self, method, url, params=None, body=None, form=None, files=None, headers=None, timeout=90, safe=None):
        """body: JSON-encoded; form: urlencoded; files: multipart {name: (filename, bytes, type) or str}.
        Returns the parsed JSON (None for an empty answer). Raises ApiError on a 4xx, or once retries run out.
        A 429 is always retried (nothing was done); a 5xx or a lost answer only when repeating the call cannot create
        a second copy (safe: GETs by default, and the callers that say so)."""
        if params:
            url = url + ("&" if "?" in url else "?") + urllib.parse.urlencode(params)
        if safe is None:
            safe = method == "GET"
        refreshed = False
        attempt = 0
        while True:
            h = {"Authorization": "Zoho-oauthtoken " + self.token()}
            h.update(headers or {})
            data = None
            if body is not None:
                data = json.dumps(body).encode()
                h["Content-Type"] = "application/json"
            elif form is not None:
                data = urllib.parse.urlencode(form).encode()
                h["Content-Type"] = "application/x-www-form-urlencoded"
            elif files is not None:
                data, ctype = multipart(files)
                h["Content-Type"] = ctype
            req = urllib.request.Request(url, data=data, method=method, headers=h)
            status, raw, retry_after = None, b"", None
            try:
                with urllib.request.urlopen(req, timeout=timeout) as resp:
                    status, raw = resp.status, resp.read()
            except urllib.error.HTTPError as e:
                status, raw = e.code, e.read()
                retry_after = e.headers.get("Retry-After") if e.headers else None
            except (OSError, http.client.HTTPException) as e:  # 3.9: socket.timeout, SSL errors, cut connections
                status, raw = None, str(e).encode()
            parsed = _parse(raw)
            if status is not None and status < 400:
                return parsed
            code = parsed.get("code") if isinstance(parsed, dict) else None
            if status == 401 and not refreshed and code != "OAUTH_SCOPE_MISMATCH" and time.time() - self.forced_at > 300:
                # an expired or revoked access token: one fresh token, at most every five minutes (Zoho allows ten
                # per ten minutes); a second 401, or a scope the grant lacks, is a real refusal
                self.forced_at = time.time()
                self.token(force=True)
                refreshed = True
                continue
            retryable = status == 429 or (safe and (status is None or status in RETRY_STATUS))
            if retryable and attempt < len(BACKOFF):
                wait = BACKOFF[attempt]
                if retry_after and retry_after.isdigit():
                    wait = min(int(retry_after), RETRY_AFTER_CAP)
                log("  backoff %ss after %s on %s %s" % (wait, status or "network error", method, url.split("?")[0]))
                time.sleep(wait)
                attempt += 1
                continue
            raise ApiError(status, parsed, method, url.split("?")[0])

    def download(self, url, timeout=120):
        req = urllib.request.Request(url, headers={"Authorization": "Zoho-oauthtoken " + self.token()})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.read()

    # ---- per service -----------------------------------------------------------------------------------------
    def crm(self, method, path, **kw):
        return self.request(method, API + "/crm/v8" + path, **kw)

    def desk(self, method, path, **kw):
        if self.desk_org is None:
            self.desk_org = desk_org_id(self)
        headers = dict(kw.pop("headers", None) or {})
        headers["orgId"] = self.desk_org
        return self.request(method, DESK + path, headers=headers, **kw)

    def bookings(self, method, path, **kw):
        return self.request(method, BOOKINGS + path, **kw)

    def campaigns(self, method, path, **kw):
        return self.request(method, CAMPAIGNS + path, **kw)


def _parse(raw):
    if not raw:
        return None
    text = raw.decode("utf-8", errors="replace")
    try:
        return json.loads(text)
    except ValueError:
        return text


def multipart(files):
    boundary = "zoho" + uuid.uuid4().hex
    out = []
    for name, value in files.items():
        out.append(("--" + boundary).encode())
        if isinstance(value, tuple):
            filename, content, ctype = value
            out.append(('Content-Disposition: form-data; name="%s"; filename="%s"' % (name, filename)).encode())
            out.append(("Content-Type: " + ctype).encode())
            out.append(b"")
            out.append(content)
        else:
            out.append(('Content-Disposition: form-data; name="%s"' % name).encode())
            out.append(b"")
            out.append(str(value).encode())
    out.append(("--" + boundary + "--").encode())
    out.append(b"")
    return b"\r\n".join(out), "multipart/form-data; boundary=" + boundary


def desk_org_id(client):
    env_org = client.env.get("ZOHO_DESK_ORG_ID")
    if env_org:
        return env_org
    resp = client.request("GET", DESK + "/organizations")
    orgs = resp.get("data", []) if isinstance(resp, dict) and "data" in resp else ([resp] if isinstance(resp, dict) else [])
    if len(orgs) != 1:
        names = ", ".join("%s (%s)" % (o.get("companyName"), o.get("id")) for o in orgs)
        raise SystemExit("expected one Desk portal, found %d: %s. Put ZOHO_DESK_ORG_ID=<id> in seed/zoho/.env"
                         % (len(orgs), names or "none; open Desk once in the trial to create it"))
    return str(orgs[0]["id"])


def check():
    c = Client()
    org = c.crm("GET", "/org")["org"][0]
    lic = org.get("license_details") or {}
    print("CRM org: %s, type %s, edition %s, trial %s" % (org.get("company_name"), org.get("type"),
                                                          lic.get("paid_type"), lic.get("trial_type")))
    print("Desk portal id: %s" % desk_org_id(c))
    ws = c.bookings("GET", "/workspaces")
    names = [w.get("name") for w in ((ws or {}).get("response", {}).get("returnvalue", {}).get("data") or [])]
    print("Bookings workspaces: %s" % (", ".join(names) or "none"))


def main():
    if len(sys.argv) >= 2 and sys.argv[1] == "auth":
        code = sys.argv[2] if len(sys.argv) > 2 else load_env().get("ZOHO_GRANT_CODE", "")
        if not code:
            raise SystemExit("usage: python3 seed/zoho/zoho.py auth <grant code>")
        auth(code)
    elif len(sys.argv) == 2 and sys.argv[1] == "check":
        check()
    else:
        raise SystemExit(__doc__)


if __name__ == "__main__":
    main()
