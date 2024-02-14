# mohela-balance
Pulls current principal and interest from Mohela


# What the hell is this?
I'm due for loan forgiveness and I'm sick of logging in to Mohela every day to see if they've adjusted my balance. They do forgiveness in batches roughly every two months so my options are to log in to Mohela or keep an eye on r/PSLF to see if anyone noticed a batch is being processed.

# How do I even use this pile of trash?
Copy the .env.example file and rename it .env. You need to pick a security question and answer it in the .env. The numbers listed are from the first "group" of security questions that are on your account so you should have the answer to exactly one of them. Once you've filled out the question number, the answer, your username, and password, just run `python3 balance.py`. You'll get some JSON outputted (hopefully).

Example:
```
$ python balance.py
{"principal": "$150,628.03", "interest": "$98,422.40"}

```
![erp](https://github.com/chelming/mohela-balance/assets/7746625/2ef08a65-d6ca-4ffe-8921-243172af9700)

# OK cool. Now what?
Idk, that's up to you. I'm gonna pipe it into Home Assistant and trigger an alert when the value changes.

# Troubleshooting
Don't @ me. If something isn't working, fix it and submit a PR.
