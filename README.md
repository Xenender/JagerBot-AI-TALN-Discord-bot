# JagerBot-AI-TALN-Discord-bot

JägerBot is a discord chatbot. It was developed in collaboration with the LIRMM (Computer Science, Robotics and Microelectronics Laboratory of Montpellier)
This is a bot whose purpose is to answer simple questions asked in **FRENCH**

"Can a penguin fly?"
"Can a dog eat meat?"

you can also ask for an explanation of the answer that was given:
"why can a penguin fly?"

## How does it work ?

JägerBot works thanks to the knowledge base <a href="https://www.jeuxdemots.org/jdm-accueil.php">JeuxDeMots</a>.
To sum up very simply, JägerBot will try to understand the relationship between the words of the question.
After finding the relationship(s) sought, JägerBot will find the keywords of the phrase and make an express query to jeuxDeMots for each keyword,
a processing will then be carried out to gather all the existing relationships between the keywords, if the relationship sought exists then the question is considered true.
JägerBot will work with a depth of 4, i.e. for each keyword it will look for the "generic" and "hypo" relations (and so on for the new words 4 times) and carry out the work again to find or not the desired relationship.

## How to use it ?

     -Create a discord bot.
    
     -Invite him to your server.
    
     -Download the project zip file.
    
     -Open the jagerbot.py file and modify the "TOKEN" variable by putting the token of your bot.
    
     -Also modify the "PATH" variable by putting the absolute path to the folder containing the jagerbot.py program.
    
     -Download if necessary the python libraries necessary for the operation of the program.

     -Run the python file "jagerbot.py".
    
     -The bot will connect to the server, you can start chatting, do !help to know the basic commands.

## Screenshots

<img src="/images/jagerbot1.png">
<img src="/images/jagerbot2.png">
<img src="/images/jagerbot3.png">

