# SSH Setup for CERN GitLab + TDAQ OKS on LXPLUS

This guide explains how to configure SSH access to **CERN GitLab** for working with the **TDAQ OKS repository on LXPLUS**.

---

## Step 0: Generate an SSH Key

First, check whether you already have an SSH key:

```bash
ls -la ~/.ssh/
```

Look for:

```text
id_ed25519
id_ed25519.pub
```

If you **do not** have these files, generate a new Ed25519 key:

```bash
ssh-keygen -t ed25519 -C "your_username@lxplus.cern.ch"
```

When prompted:

* **File to save the key:** Press `Enter` to accept the default:

  ```text
  ~/.ssh/id_ed25519
  ```
* **Passphrase:** Optional. You can press `Enter` to use no passphrase, or set a passphrase for additional security.

Verify that the key was created:

```bash
ls -la ~/.ssh/
```

You should see something similar to:

```text
id_ed25519
id_ed25519.pub
known_hosts
```

> **Important:**
> `id_ed25519` is your **private key**. Never share or upload it.
> `id_ed25519.pub` is your **public key** and is the one you add to CERN GitLab.

---

# Step 1: Add Your Public Key to CERN GitLab

Display your public key:

```bash
cat ~/.ssh/id_ed25519.pub
```

The output should be a single line beginning with:

```text
ssh-ed25519
```

Copy the entire line.

Then:

1. Log in to [CERN GitLab](https://gitlab.cern.ch).(https://gitlab.cern.ch/)
2. Click on you profile icon → Go to **Preferences → SSH Keys**.
3. Paste your public key.
4. Usage type : Authentication and Signing, set expiry date to future
5. Save/add the key.

> **Security warning:**
> Only add:
>
> ```text
> id_ed25519.pub
> ```
>
> Never upload:
>
> ```text
> id_ed25519
> ```
>
> The latter is your private key.

---

# Step 2: Configure SSH for Port 7999

Create or edit your SSH configuration file:

```bash
nano ~/.ssh/config
```

Add:

```text
Host gitlab.cern.ch
    HostName gitlab.cern.ch
    User git
    Port 7999
    IdentityFile ~/.ssh/id_ed25519
    IdentitiesOnly yes
```

Save the file.

Then set the appropriate permissions:

```bash
chmod 600 ~/.ssh/config
chmod 600 ~/.ssh/id_ed25519
chmod 644 ~/.ssh/id_ed25519.pub
```

### Why configure port 7999?

The TDAQ OKS Git repository uses the CERN GitLab SSH endpoint on **port 7999**.

With the configuration above, SSH automatically uses:

```text
gitlab.cern.ch:7999
```

when you connect to:

```bash
gitlab.cern.ch
```

Therefore, you don't need to specify `-p 7999` every time.

---

# Step 3: Test SSH Authentication

Run:

```bash
ssh -T git@gitlab.cern.ch
```

Because `~/.ssh/config` specifies port `7999`, SSH should automatically use that port.

A successful authentication should produce a message similar to:

```text
Welcome to GitLab, @<your-username>!
```

If you want to explicitly specify the port, you can also test:

```bash
ssh -T -p 7999 git@gitlab.cern.ch
```

---

# Step 4: Test Repository Access

Once SSH authentication works, test access to the actual TDAQ OKS repository:

```bash
git ls-remote 'ssh://git@gitlab.cern.ch:7999/atlas-tdaq-oks/p1/tdaq-11-02-01.git'
```

If successful, Git should print a list of references such as:

```text
<commit-hash>    HEAD
<commit-hash>    refs/heads/master
<commit-hash>    refs/heads/...
```

This confirms that:

1. SSH authentication works.
2. GitLab access works.
3. You have access to the repository.
4. The repository URL is valid.

---

# Step 5: Set TDAQ Environment Variables

Set the TDAQ repository URL:

```bash
export TDAQ_DB_REPOSITORY='ssh://git@gitlab.cern.ch:7999/atlas-tdaq-oks/p1/tdaq-11-02-01.git'
```

Set the Git protocol:

```bash
export OKS_GIT_PROTOCOL='ssh'
```

Clear potentially conflicting variables:

```bash
unset TDAQ_DB_USER_REPOSITORY
unset TDAQ_DB_PATH
```

Verify the configuration:

```bash
echo "$TDAQ_DB_REPOSITORY"
echo "$OKS_GIT_PROTOCOL"
```

You should see:

```text
ssh://git@gitlab.cern.ch:7999/atlas-tdaq-oks/p1/tdaq-11-02-01.git
ssh
```

---

# Step 6: Manage the SSH Agent

Check whether your SSH key is currently loaded:

```bash
ssh-add -l
```

If you see something similar to:

```text
The agent has no identities.
```

add your key:

```bash
ssh-add ~/.ssh/id_ed25519
```

Then check again:

```bash
ssh-add -l
```

You should now see your Ed25519 key listed.

> **LXPLUS note:**
> When connecting to a new LXPLUS node, it is useful to first run:
>
> ```bash
> ssh-add -l
> ```
>
> If your key is not loaded, add it with:
>
> ```bash
> ssh-add ~/.ssh/id_ed25519
> ```

---

# Quick Troubleshooting

| Symptom                                      | Meaning / Possible Cause                                                        |
| -------------------------------------------- | ------------------------------------------------------------------------------- |
| `Permission denied (publickey)` on port 22   | SSH is using the wrong endpoint/port for the TDAQ repository                    |
| `Welcome to GitLab, @username!` on `:7999`   | SSH authentication is working                                                   |
| `git ls-remote` succeeds                     | Repository access is working                                                    |
| `git ls-remote` says `project not found`     | Repository URL may be wrong or you may not have permission                      |
| Application removes `:7999` from the URL     | The application may be rewriting the repository URL; check `TDAQ_DB_REPOSITORY` |
| `ssh-add -l` shows no identities             | Your SSH key is not loaded into the SSH agent                                   |
| SSH works manually but the application fails | The application may be constructing or modifying the repository URL incorrectly |

---

# The Two Critical Tests

Before running your application, verify these two commands.

## Test 1 — SSH Authentication

```bash
ssh -T -p 7999 git@gitlab.cern.ch
```

Expected result:

```text
Welcome to GitLab, @<your-username>!
```

If this works, your SSH authentication is working.

---

## Test 2 — Repository Access

```bash
git ls-remote 'ssh://git@gitlab.cern.ch:7999/atlas-tdaq-oks/p1/tdaq-11-02-01.git'
```

Expected result:

A list of Git references, for example:

```text
<commit-hash>    HEAD
<commit-hash>    refs/heads/master
```

If this works, your Git repository access is working.

---

# Troubleshooting Flow

The recommended order for debugging is:

```text
SSH Key
   │
   ▼
CERN GitLab SSH Authentication
   │
   │  ssh -T -p 7999 git@gitlab.cern.ch
   ▼
Repository Access
   │
   │  git ls-remote ...
   ▼
TDAQ Environment Variables
   │
   │  TDAQ_DB_REPOSITORY
   │  OKS_GIT_PROTOCOL
   ▼
Application
```

If the first two tests work but the application fails, the problem is likely **not the SSH key itself**. Investigate how the application constructs or modifies the repository URL.

---

# Important Reminders

### 1. Use CERN GitLab

Use:

```text
gitlab.cern.ch
```

Do **not** use:

```text
gitlab.com
```

---

### 2. TDAQ Repository Uses Port 7999

The repository URL should contain:

```text
:7999
```

For example:

```text
ssh://git@gitlab.cern.ch:7999/atlas-tdaq-oks/p1/tdaq-11-02-01.git
```

---

### 3. SSH Config Can Hide the Port

If your `~/.ssh/config` contains:

```text
Host gitlab.cern.ch
    HostName gitlab.cern.ch
    User git
    Port 7999
```

then:

```bash
ssh git@gitlab.cern.ch
```

will automatically connect using port `7999`.

You therefore don't need:

```bash
-p 7999
```

for normal SSH commands.

---

### 4. One SSH Key Is Enough

You do **not** need to create a separate SSH key for every CERN GitLab repository.

One key can be associated with your CERN GitLab account and used to access repositories for which your account has permission.

---

### 5. LXPLUS Home Directory

Your home directory is shared across LXPLUS nodes, so your:

```text
~/.ssh/
```

configuration should normally be available when you log in to another LXPLUS node.

---

# Final Verification Checklist

Before running the TDAQ application, verify:

* [ ] `~/.ssh/id_ed25519` exists.
* [ ] `~/.ssh/id_ed25519.pub` exists.
* [ ] The public key has been added to CERN GitLab.
* [ ] `~/.ssh/config` contains the GitLab port `7999`.
* [ ] SSH key permissions are correct.
* [ ] `ssh-add -l` shows your key.
* [ ] `ssh -T -p 7999 git@gitlab.cern.ch` succeeds.
* [ ] `git ls-remote` succeeds.
* [ ] `TDAQ_DB_REPOSITORY` contains `:7999`.
* [ ] `OKS_GIT_PROTOCOL` is set to `ssh`.
* [ ] Conflicting TDAQ repository variables have been unset.

If all of these checks pass, the **SSH and GitLab side of the TDAQ OKS setup is correctly configured**.
