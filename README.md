
# Experiment: Claude for e-Comm + Flask website
**Primary Objective:** Use Anthropic's Claude as an aid to build an e-Comm website in Flask. 

**Secondary Objective:** Learn more about Flask as I use Claude to build the code, I test the code, and give Claude feedback about what did and did not work.
## Short Background
I have used Python for going on 10 years but I was only familiar with Flask. I'd built a few very simple pages of a website years ago.

The background, provided below, was provided so that you could understand that what my level of understanding was before starting the experiment. I was not a blank slate with regards to understanding the pieces of an e-Comm site. Nor was a blank slate with regards to Python or Flask. However, my understanding of Flask specifically for the task was still quite basic.

# Final Outcome
Claude was building the e-Comm site well. The conversation were going well. However, as the tasks became more complex, I was having to learn a lot about how to explain the coding task to Claude. (Note: I think this will always be the fundamental difficulty in getting AI to code things for us. English just isn't a very good engineering language for hardware or software. Human language in general is not precise enough.)

The intent was to get to a complete site. However, this wasn't just an experiment but rather a means of acquiring customers. I've since received advice to stop making this so complex and just get something simple out there. Discover is there is really a market for these tools. People will forgive you for a crude UI if the tool is useful.

So I've decided to leave this incomplete and go another route. Assuming I make money from these tools, I'll probably hire someone to build the UI for me.
### Primary Objective
The site that is presented in the code is functional but lacks styling. I was focused on functionality not style at this stage. It is also incomplete. The site is also crudely organized. Claude dumps everything into a single folder and all routes into the app.py file unless you instruct it otherwise. The code comes without adequate commenting as well.

I wouldn't want to code in this style myself. However, the code Claude provided, both Python and HTML, was fully functional and correct roughly 90% of the time. If you read the conversation with Claude you will see a significant amount of time is spent debugging with Claude but that is mostly around 1 feature which I needed to Google to figure out the fix. In other instances, Claude was quite good at fixing its own code so long as I adequately explained the error I was getting.
### Secondary Objective
The secondary objective was as successful as it could be without finishing the site but was heavily aided by the fact that I'd already done a lot of research into the structure of an e-Comm site. As well as having spent some time learning the code for the db models that SQLAlchemy uses prior to using Claude.

This meant that when I did something like asking Claude to "build a login and registration form for an e-Comm site" I was able to look at the resulting code and refine my question "to (1) build a Users table with fields ..., (2) build a login form with a Forgot password link, (3) build a registration form, ..." This dramatically speeds up the building of quality code and by extension the speed at which you reach the deeper levels of the design and the code.

Additionally, using Claude for this learning is like learning at warp speed. I'm asking for an e-Comm site and Claude can provide a lot of the code for that without precise prompting. But the code results in a site with bare minimum functionality lacking things like a "Forgot Password" button. Or a cart/checkout functionality that doesn't allow a customer to more than 1 thing at a time or won't allow a customer to designate that they want to buy 3 of the same item. This forces you to step back, consider the design and features you want, and explicitly ask for revisions. Those revisions expose more features of Flask, leading to more design questions, leading to new features, leading to more code experiments.

Finally, learning to code in this manner is extremely fast. If I have a specific question about the fastest way to sort a list in Python then StackOverflow is still the best choice. But if I'm new to something like Flask, there are lots of getting started questions. StackOverflow is great for this but it's even better to have Claude produce code in seconds that works and is specific to the question I asked. The amount of code I'm consuming in each iteration is smaller and more targeted to my current frame of mind. As a result, my follow questions can be much more targeted.
# Background
I have built AI based automation tools. The number and breadth of tools has reached a level where it's time to find customers. Step one is to build a way to allow customers to purchase those tools.

The ultimate website/web app would include an e-comm style site that allows for usage of the tools within the web app. I tried a few no-code tools and while they are capable of the e-comm site side, they are extremely limited with regards to doing something like a built-in chat.

The exploration chain was Bubble (no-code) -> Softr (no-code) -> Reflex (python library) -> Flask (python library) -> Adalo (no-code). This repo represents a part of the Flask portion of this exploration.

I initially attempted to build a Flask e-Comm site based on examples online. Then I decided to try Claude for this.

## More specific background on my understanding of Flask relative to the Claude conversation
Let's start with Reflex, a low-code style Python library for creating React sites using Python code.

When I worked with Reflex, the code was incomplete. There are tutorials for things like building a login form but the tutorial doesn't tie that login to a db. Nor does the tutorial show you how to designate someone is authenticated as they explore other pages. So you have to build your own way of doing this. How secure is that if you haven't done it before? How long do you want to study that security before moving forward with the rest of the project?

Like the no-code tools, Reflex is limited in what I can do. Additionally, the repo is still buggy and the documentation is limited. Reflex is not yet ready for a production site (IMO).

So then I decided to look into Flask where I would need to build a lot more code but have far fewer limitations related to the functionality. (Hopefully)

Like many examples online, the code for a Flask e-Comm website tends to be more complete for Flask than Reflex. So I started by following a YouTube channel that had a series of 10 min videos on how to build out the pieces of the e-Comm site. It was informative and the code well organized. It came with a repo as well.

As I followed the tutorial, I was copying files from the repo to my local computer one at a time. However, two problems occurred. First, the code in the early tutorials is not what is in the repo. This is because the repo is the final product and the code in the tutorials is built to allow testing at each stage. Second, as I got deeper into the videos the e-Comm site that was being built for the videos began deviating from my desired site. So I was making small tweaks to the repo's code. Eventually I stopped being able to test that the code was still working.

So I faced a choice of start over, build up the code in the same way the tutorial did (piecemeal) allowing for staged testing. Or try something else.

I had used ChatGPT (3.5) to build out simple pieces of physics simulations in Python for me. The code that resulted was decent. It had some small syntax errors but it wasn't bloated or completely incorrect. However, the context window was a major issue in designing anything even modestly complex.

Claude has a context window of 100k tokens. My prior experiments with Claude building code had not gone nearly as well as my early experiments with ChatGPT but it had been a few months. So I tried again.

