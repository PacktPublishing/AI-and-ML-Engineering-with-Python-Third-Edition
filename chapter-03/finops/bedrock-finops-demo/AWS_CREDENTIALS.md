# Getting AWS credentials for this demo, step by step

This guide assumes you are starting from scratch: you have an AWS account
and can sign in to the AWS Management Console as the **root user** (the
email address you signed up with), and nothing else is set up yet.

By the end you will have:

1. An **IAM user** — an identity for day-to-day work, so you can stop using
   the root user.
2. **Permissions** attached to that user, so it's allowed to call Bedrock.
3. An **access key** on your laptop, so `boto3` can authenticate as that user.
4. **Bedrock model access** enabled, so the models will actually answer.

Work through the steps in order. Total time: about 10 minutes.

> **Why not just use the root user?** The root user can do anything,
> including deleting the whole account, and its credentials can't be
> restricted. The rule is: use root once to create your working identity,
> then sign out and don't use it again.

---

## Step 1: sign in and open IAM

1. Go to <https://console.aws.amazon.com/> and sign in as the **root user**
   (choose "Root user" on the sign-in page and use your account email).
2. In the search bar at the very top of the console, type **IAM** and click
   the **IAM** service in the results.

IAM (Identity and Access Management) is where users and permissions live.

## Step 2: create an IAM user

If you've already created a user, skip to Step 3 — but read through to check
you made the same choices.

1. In the IAM left-hand menu, click **Users**, then the orange
   **Create user** button.
2. **User name:** `bedrock-demo` (any name is fine).
3. **Provide user access to the AWS Management Console?** — leave this
   **unticked**. This user is only for running code from your terminal; it
   doesn't need to log in to the website.
4. Click **Next**. You're now on the permissions page — continue with
   Step 3 below (it's part of the same wizard).

## Step 3: give the user permissions

On the **Set permissions** page of the wizard (or, if your user already
exists: **IAM → Users → click your user → Permissions tab → Add
permissions → Add permissions**):

1. Choose **Attach policies directly**.
2. In the search box, type `AmazonBedrockFullAccess`, and **tick** the
   checkbox next to the policy with exactly that name.
3. Clear the search box, type `CloudWatchReadOnlyAccess`, and **tick** that
   one too.
4. Click **Next**, then **Create user** (or **Add permissions** if editing
   an existing user).

That's two AWS-managed policies:

| Policy | Why the demo needs it |
| --- | --- |
| `AmazonBedrockFullAccess` | Lets the user invoke Bedrock models |
| `CloudWatchReadOnlyAccess` | Lets you view the token metrics in CloudWatch |

> These managed policies are broader than the demo strictly needs, which is
> fine for a personal learning account. A least-privilege alternative is at
> the end of this guide.

## Step 4: create an access key

An access key is a two-part credential (an ID and a secret) that programs
like `boto3` use to prove they are acting as your IAM user.

1. **IAM → Users →** click **bedrock-demo**.
2. Open the **Security credentials** tab.
3. Scroll to **Access keys** and click **Create access key**.
4. For "Use case", choose **Command Line Interface (CLI)**, tick the
   confirmation box at the bottom, and click **Next**, then
   **Create access key**.
5. You now see the **Access key ID** (starts with `AKIA`) and the
   **Secret access key**. **The secret is shown only this once.** Keep this
   browser tab open until Step 5 is done, or download the `.csv`.

Treat these two values like a password:

- never paste them into code, notebooks, or `.env` files inside a git repo;
- never share them or screenshot them;
- if they ever leak, come back to this page and click
  **Actions → Deactivate**, then delete and create a new key.

## Step 5: put the key on your laptop

Install the AWS CLI if you don't have it:

```bash
# macOS
brew install awscli

# check it worked
aws --version
```

Then run:

```bash
aws configure
```

It asks four questions — answer with the values from Step 4:

```text
AWS Access Key ID [None]:     AKIA................   <- from step 4
AWS Secret Access Key [None]: ....................   <- from step 4
Default region name [None]:   us-east-1              <- where you'll use Bedrock
Default output format [None]: json
```

This writes the key to `~/.aws/credentials` and the region to
`~/.aws/config` — plain files in your home directory, outside any git
repository. Every AWS tool on your machine (the CLI, `boto3`, and therefore
this demo) reads them automatically. You never put credentials in the code.

Check it worked:

```bash
aws sts get-caller-identity
```

You should see JSON containing your account number and
`.../user/bedrock-demo`. If you see `Unable to locate credentials`, run
`aws configure` again.

You can now sign out of the root user in your browser.

## Step 6: enable Bedrock model access

IAM permissions say your *user* may call Bedrock. Separately, your *account*
must have each model family switched on. Without this, the demo fails with
`AccessDeniedException` even though Steps 1–5 are correct.

1. In the console search bar, type **Bedrock** and open **Amazon Bedrock**.
2. Check the **region picker** (top-right of the console) shows the same
   region you chose in Step 5, e.g. `us-east-1`.
3. In the left-hand menu, scroll to the bottom and click **Model access**.
4. Click **Modify model access** (or **Enable specific models**).
5. Tick the **Amazon Nova** models and the **Anthropic Claude** models, then
   click **Next** and **Submit**. Anthropic models may show a short
   use-case form — fill it in briefly; approval is normally instant.
6. Wait until the status column shows **Access granted** for the models you
   ticked (refresh after a minute).

## Step 7: verify, then run the demo

```bash
# 1. Credentials work?
aws sts get-caller-identity

# 2. Bedrock reachable and models visible in your region?
aws bedrock list-foundation-models --region us-east-1 \
  --query 'modelSummaries[?contains(modelId, `nova-micro`)].modelId'
```

If the second command prints a model ID, everything is in place:

```bash
cd chapter-03/finops/bedrock-finops-demo
uv sync
uv run python run_demo.py
```

## If something goes wrong

| You see | It means | Do this |
| --- | --- | --- |
| `Unable to locate credentials` | Step 5 didn't complete | Re-run `aws configure`; check with `aws sts get-caller-identity` |
| `AccessDeniedException` | Model access not enabled (most likely), or policies not attached | Step 6 first; then check the user's Permissions tab shows both policies from Step 3 |
| `ValidationException` mentioning the model ID | That model/profile isn't available in your region | Substitute the model IDs — see the README |
| Metrics missing in CloudWatch | Wrong region, or too soon | Match the console region to the one `run_demo.py` printed; wait 1–2 minutes |

---

## Optional extras (come back to these later)

**Least-privilege policy.** Instead of the two managed policies in Step 3,
you can create a custom policy (**IAM → Policies → Create policy → JSON**)
that allows only what the demo does, and attach that to the user instead:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "InvokeBedrockModels",
      "Effect": "Allow",
      "Action": ["bedrock:InvokeModel"],
      "Resource": [
        "arn:aws:bedrock:*::foundation-model/*",
        "arn:aws:bedrock:*:*:inference-profile/*"
      ]
    },
    {
      "Sid": "ViewCloudWatchMetrics",
      "Effect": "Allow",
      "Action": ["cloudwatch:ListMetrics", "cloudwatch:GetMetricData"],
      "Resource": "*"
    }
  ]
}
```

Both Bedrock resource lines are needed: the demo's default model IDs are
*cross-region inference profiles* (the `us.` / `eu.` prefix), and calling a
profile requires permission on the profile **and** the foundation models it
routes to.

**IAM Identity Center (SSO).** For an account you'll use long-term, AWS
recommends IAM Identity Center over access keys: you log in through a
browser (`aws configure sso`, then `aws sso login`) and receive short-lived
credentials, so no permanent secret sits on your laptop. It takes longer to
set up, which is why this guide uses access keys — but it's the pattern to
adopt once you're past the learning stage.

**Root account hygiene.** While signed in as root one last time: turn on
MFA for the root user (**IAM dashboard → Add MFA**), and never create
access keys for the root user.
