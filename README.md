# Puns

![License](https://img.shields.io/github/license/BigBangData/Puns)
![File Count](https://img.shields.io/github/directory-file-count/BigBangData/Puns)
![Last Commit](https://img.shields.io/github/last-commit/BigBangData/Puns?color=blueviolet)
![Stars](https://img.shields.io/github/stars/BigBangData/Puns?style=social)
![Forks](https://img.shields.io/github/forks/BigBangData/Puns?style=social)
![Watchers](https://img.shields.io/github/watchers/BigBangData/Puns?style=social)

## Story

I created a little puns website on a whim but also because I wanted to learn how to deploy a website using Python and Flask. The website evolved backwards in that my first instinct was to create an experience using data science techniques and statistical models (recently remarketed as "AI") but that turned out to be not as user-friendly as simply offering up the content and let the content shine.

The former data-sciency version of the site served questions and answers that contained a pun of sorts, but to see the answers the user had to input text into a form in an attempt to guess the answer, then various statistical models would compete to calculate the similarity of the actual answer to the user guess and the ensemble would output a prediction that the user got it right, or close enough. After that decision, the user would see a message of success or failure, accompanied by confetti (the failure confetti was very sad-looking). The user then would have to rate whether the success/failure was correct or not, and based on those inputs the ensemble would "re-train" itself (more like update weights of the models) so it'd "learn" over time (more like update the weights...). This was all super fine with one "small" exception that __it is really hard to guess the answer!__ So the UX was that users would constantly experience sad-looking confetti failures and feel bad about themselves, or I could lower the threshold of success and the entire experience would be a bit odd, getting success messages for failures, and so on. The data science bit, the so-called "online ensemble model weight updates" was fun, but the actual implementation did not add, it in fact subtracted from the UX.

So I decided to, ahem, "rollback the site" (fine, I didn't practice agile I deployed a more complex experience first) into its current form, where users just get the answer by "pressing any key" - this little delay to at least tempt the user to think up an answer, just a wee bit of suspense before being served up the answer, else I could've just served up all the puns in html or even simpler, emailed the list.

As for the conffeti, they became a bit more... interesting. They went from two animals (a happy unicorn and a sad lobster) that initially were evenly spaced (every 10 answers, etc.) to a whole confetti zoo that pops up randomly. And by randomly I mean exactly the opposite of the mathematical definition of randomness, but I do mean the popular notion that if you attempt to guess which animal will be confettied next or when, you will probably be surprised.

## Deployment

The site is deployed at an invite-only ip address for a select group of beta users since it costs to host the server and I'm near capacity for that small server. The code here can serve as a bootstrap to deploying your own website with Python and Flask.

## Site Behavior

Below are some behaviors of the frontend:

- __signup__:
  + only possible when logged out
    - flashes msg otherwise and redirects to `play`
  + fails if username exists
  + redirects to login on success
- __login__:
  + only possible when logged out
    - - flashes msg otherwise and redirects to `play`
  + fails when password is wrong
  + fails when username doesn't exist and redirects to `signup`
  + session inactivity will `logout` user
- __logout__:
  + not a route but a `base` template footer button
  + displayed when logged in only on all pages
- __play__:
  + goal of `signup` and `login`
  + when logged in, `signup` or `login` will redirect to `play`
  + goes through puns in order for every user
  + shows only question and word count so user can try to guess
  + any key redirects to `view_answer`
  + persist puns asked beyond single session so user can come back where she left off
  + starts over when all puns have been shown
- __view answer__:
  + reveals answer and pun
  + user must click on one of six "emoji buttons" to rate the pun
  + feedback get recorded in the backend table `ratings`, and triggers new `play`
- __stats__:
  + display user stats in a simple column graph with counts for each rating + avg rating line
  + displayed separately from `view_answer` so as not to influence user ratings too much

## Credits

- many of the puns were originally sourced from Will Styler's collection at: https://wstyler.ucsd.edu/puns/
  + many of them were changed substantially to fit the question-and-answer format and in an attempt to make them more humorous
- the point of origin for some of the app's code was Tim Ruscica's tutorials below, and Arpan Neupane's turotial for authentication
- I also made regular use of chatGPT (free tier of https://chat.openai.com/) to help speed up and troubleshoot code and deployment

## Tutorials Consulted

Tutorials from Tim Ruscica: 
- [Flask Series on YouTube](https://www.youtube.com/@TechWithTim)
- [Website](https://www.techwithtim.net)
- [Github](https://github.com/techwithtim)

Tutorial from Arpan Neupane:
- [Authentication Video on YouTube](https://www.youtube.com/watch?v=71EU8gnZqZQ)
- [GitHub](https://github.com/arpanneupane19/Python-Flask-Authentication-Tutorial/blob/main/app.py)

More Links:
- [Bootstrap Intro](https://getbootstrap.com/docs/5.3/getting-started/introduction/)

## Local Dev

To test locally before deployment, reproduce virtual env (see `requirements.txt`) and issue:

```{bash}
source ~/usr/local/venv/py3/Scripts/activate
source local.env
python -u run.py
```

The `local.env` contains export commands (for unix-style shell like Git Bash) used to set environment variables that will be available to any subprocesses or scripts executed from the shell, for example:

```{bash}
export BETA_USERS='<usernam_one>,<username_two>'
```

## Remote Dev

Deploying a sever is complex and varies depending on the infrastructure, but this is a typical test and deploy flow that I adhered to when making small changes to ensure they deployed correctly:

1. commit changes
2. copy changes into `server/` to see diff
3. revert changes that aren't needed in the server
4. scp changes into server
5. ssh in; modify user and permissions; restart server

---