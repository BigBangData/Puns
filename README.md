# Puns

![License](https://img.shields.io/github/license/BigBangData/Puns)
![File Count](https://img.shields.io/github/directory-file-count/BigBangData/Puns)
![Last Commit](https://img.shields.io/github/last-commit/BigBangData/Puns?color=blueviolet)
![Stars](https://img.shields.io/github/stars/BigBangData/Puns?style=social)
![Forks](https://img.shields.io/github/forks/BigBangData/Puns?style=social)
![Watchers](https://img.shields.io/github/watchers/BigBangData/Puns?style=social)

## Story

I created a little puns website on a whim, but also because I wanted to learn how to deploy a site using [Python](https://www.python.org/) <img src=static/img/python.png width="20" height="20"/> and [Flask](https://flask.palletsprojects.com/en/3.0.x/). <img src=static/img/flask.png width="20" height="20"/>

The website evolved backwards <img src=static/img/pepe-sip-backwards.gif width="20" height="20"/> because my first instinct was to create an experience using data science techniques <img src=static/img/atom.gif width="20" height="20"/> and statistical models but that turned out to be not as user-friendly as simply offering up the content and letting it shine. <img src=static/img/diamond.png width="20" height="20"/>

__Data <img src=static/img/for_science.jpg width="24" height="24"/> Version__ 

The original version of the site worked like this:
1. user sees a question and a form
2. user inputs text into a form to guess the answer, which should contain a pun
3. user sees the question and both actual and guessed answer, and gets success/failure confetti
4. user then clicks on either a "correct" or "wrong" button in reaction to the success/failure confetti
5. that final user feedback reloads the next question

The success/failure was either happy unicorn confetti <img src=static/img/unicorn.gif width="20" height="20"/>, or sad lobster <img src=static/img/lobster.png width="20" height="20"/> ones. Success was determined by an ensemble of models whose weighted average score had to pass threshold. Those models would compute the similarity between the two answers in different ways, with simple text similarity measures or word embeddings, using transformers, and even phonetically, and the system of weights would adapt every time the user gave feedback about whether the success/failure confetti was correct or wrong, in a sense "training" the ensemble model to predict success better over time.

The problem with all this wasn't the data science - it was the user experience. Forget for a second that it's a bit onerous and obscure to ask users to type in answers and later rate conffeti reactions for the success of ensemble models in their weighted average evaluation of success or failure in... yeah, even explaining what is wrong hurts <img src=static/img/this-is-fine-fire.gif width="20" height="20"/>, what was really wrongheaded is that it is __way too hard to guess the answer!__, and most of the time a user would just get them sad lobsters. If we lower the threshold of success so more unicorn confetti are thrown, that just confuses the models and users who don't understand why there was success when there should've been a failure. <img src=static/img/fail.gif width="24" height="24"/>

__Let The Content Shine__

Given the bad UX, I decided to "rollback the site"... (fine, I didn't practice agile and deployed a more complex experience first, so it's more like a roll forward) to its current form:
1. user sees a question and can press any key to see the answer
2. user sees the answer and then 6 emoji buttons that user clicks to "rate the pun"
3. the pun rating reloads the next question

Not only is the flow a lot simpler and clearer, it's more fun to interact with, and makes a ton more sense. Instead of rating the performance of an ensemble of statistical models, the user is just rating the pun, interacting more with the actual content. The site is about puns, not "text similarity models"! <img src=static/img/punk.gif width="20" height="20"/>

As for the conffeti.... they went from two animals to a whole zoo.  <img src=static/img/ladybug.gif width="20" height="20"/>  <img src=static/img/jellyfish.gif width="20" height="20"/> <img src=static/img/dragon.gif width="20" height="20"/>

Initially I'd throw the confetti every fifth or tenth answer but as I added animals, I decided to make the experience seem a bit more random. And by random I don't mean the mathematical definition <img src=static/img/math.gif width="30" height="20"/>, but the popular notion that random = "unexpected"... so for example, if users attempts guess which animal will be confettied next and when, that won't be so guessable and will keep users on their toes. <img src=static/img/potaytoes.gif width="20" height="20"/>

## Deployment <img src=static/img/partydeploy.gif width="24" height="24"/>

The site is deployed at an invite-only ip address for a select group of beta users since it costs to host the server and I'm at near capacity for that small server. The code here can serve as a bootstrap to deploying your own website with Python and Flask if you so desire.

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

## Credits <img src=static/img/thankyou.gif width="24" height="24"/>

- many of the puns were originally sourced from Will Styler's collection at: https://wstyler.ucsd.edu/puns/ <img src=static/img/clapclap.gif width="20" height="20"/>
  + many of them were changed substantially to fit the question-and-answer format and in an attempt to make them more humorous
- the point of origin for some of the app's code was Tim Ruscica's tutorials below, and Arpan Neupane's turotial for authentication
- I also made regular use of chatGPT (free tier of https://chat.openai.com/) to help speed up and troubleshoot code and deployment

## Tutorials Consulted <img src=static/img/books.gif width="24" height="24"/>

Tutorials from Tim Ruscica: 
- [Flask Series on YouTube](https://www.youtube.com/@TechWithTim)
- [Website](https://www.techwithtim.net)
- [Github](https://github.com/techwithtim)

Tutorial from Arpan Neupane:
- [Authentication Video on YouTube](https://www.youtube.com/watch?v=71EU8gnZqZQ)
- [GitHub](https://github.com/arpanneupane19/Python-Flask-Authentication-Tutorial/blob/main/app.py)

More Links:
- [Bootstrap Intro](https://getbootstrap.com/docs/5.3/getting-started/introduction/)
- [Slackmoji emojis](https://slackmojis.com/emojis/)

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

Deploying to a server is complex and varies depending on the infrastructure, but this is a typical test and deploy flow that I adhered to when making small changes to ensure they deployed correctly:

1. commit changes
2. copy changes into the `server/` folder to check diffs
3. revert changes that aren't needed in the (actual) server
4. scp `server/` into (the actual) server
5. ssh into the server; modify user and permissions for files; restart server

---