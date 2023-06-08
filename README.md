# AntiInsult
A Discord Bot which automatically deletes words which you want to have deleted. And more.

## Functions:

- Depends on a mysql database
- Each Discord Server has its own anti insult list
- Automatically deletes words in the list
- Only Admins or allowed users can change the list
- You can run the docker-compose.yml to create a mysql database or use your own

## Bot Commands:

- $createInsult(creates the list)
- $addAllowedUser @discordname(Adds a user which is allowed to change the list)
- $removeAllowedUser @discordname(Removes the allowed user)
- $addInsult insultword(Adds a word to the auto delete list)
- $removeInsult(Removes a word from the auto delete list)
- $removeAll(Removes all word entrys from the list)
