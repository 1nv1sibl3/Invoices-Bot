# Invoices Bot

Invoices Bot is a Discord bot designed to help manage and track invoices for your server. It allows administrators to send invoice reminders to users, track their payment status, and much more!

## Features
- Send invoice reminders to users.
- Track user payments and invoice statuses.
- Dump members by roles, joined date, or custom format.
- AFK system with status tracking and auto-restore.
- Dynamically control which users/roles can access specific commands.
- Easy-to-use commands for managing invoices.

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/Invoices-Bot.git
   cd Invoices-Bot
   ```

2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the bot:
   ```bash
   python main.py
   ```

## Configuration

Make sure to configure any necessary settings in your `main.py` or any configuration files (e.g., `config.py`). The bot expects specific environment variables and configuration options to run properly.

### Environment Variables
- `DISCORD_TOKEN`: Your bot's Discord token (get it from the [Discord Developer Portal](https://discord.com/developers/applications)).

---

## Commands

### `/setperms`
- **Description:** Allows server admins to define which users or roles can access specific commands or cogs.
- **Subcommands:**
  - `add`: Grants access to a cog or feature.
  - `remove`: Revokes access from a user or role.
- **Usage Examples:**
  ```
  /setperms add cog:afk allowed_roles:@Staff @Mod
  -setperms remove cog:dump allowed_users:@User1
  ```

### `/afk` and `-afk`
- **Description:** Sets your AFK status. Automatically removes it when you send a message.
- **Arguments:**
  - `user (optional)`: Set AFK on behalf of another user (if allowed).
  - `reason (optional)`: Reason for going AFK (default is "AFK").
- **Usage Examples:**
  ```
  /afk reason:"eating lunch"
  -afk @User homework time
  ```

### `/afkconfig` and `-afkconfig`
- **Description:** Configure AFK behavior for the server.
- **Subcommands:**
  - `add`: Add channels or categories to ignore AFK resets.
  - `remove`: Remove them from being ignored.
- **Usage Examples:**
  ```
  /afkconfig add ignore_channels:#spam ignore_categories:1234567890
  -afkconfig remove ignore_channels:#bot-stuff
  ```

### `/dump` and `-dump`
- **Description:** Dumps members into a list or text file with filtering and formatting options.
- **Supports Flags:**
  - `-r`, `--has-roles`: Filter by role(s)
  - `--order`: Sort by name, id, created_at, joined_at
  - `-l`, `--limit`: Limit the number of results
  - `-f`, `--format`: Custom format using `%n`, `%i`, `%u`, `%c`, `%j`
  - `-e`, `--enumerate`: Number the results
  - `--no-roles`: Filter users with no roles
- **Usage Examples:**
  ```
  /dump role:@Staff limit:10 order:joined_at format:"%n (%j)"
  -dump -r @Mod -e -f %u
  -dump -r @Role1 @Role2 --order id --desc
  ```

### /invoice
- **Description:** Generates a payment invoice for a user.
- **Arguments:**
  - **buyer:** The buyer (user mention).
  - **in_game_name:** The buyer’s in-game name.
  - **service:** The service/rank to purchase (choose from *Celestia, Eldrin, Phantom, Titan*).
  - **duration:** Duration until the invoice expires (e.g. 28d, 2h, or 30m).
  - **reminder_time:** Time before expiration to send a reminder (e.g. 1d, 12h, or 30m).
  - **attachment:** Proof of payment (required).
- **Usage Example:**
  
text
  /invoice buyer:@User in_game_name:"Test_User" service:Celestia duration:28d reminder_time:1d attachment:<file>


### /coininvoice
- **Description:** Creates a coin invoice for a user.
- **Arguments:**
  - **player:** The user receiving coins (user mention).
  - **ingame_name:** The user’s in-game name.
  - **coin_amount:** The number of coins.
  - **discount:** Discount percentage (0–100).
- **Usage Example:**
  
text
  /coininvoice player:@User ingame_name:"Test_User" coin_amount:100 discount:10


### /reminder
- **Description:** Manually sends a payment reminder to a user.
- **Arguments:**
  - **buyer:** The user who needs a reminder (user mention).
  - **ingame_name:** The buyer’s in-game name.
  - **staff:** The staff member sending the reminder (user mention).
  - **service:** The service name.
  - **amount:** Amount in Rs.
  - **expiration:** Expiration time in shorthand (e.g. 1d, 2h, 30m).
- **Usage Example:**
  
text
  /reminder buyer:@User ingame_name:"Test_User" staff:@Staff service:Celestia amount:199 expiration:1d


### /reload or -reload
- **Description:** Reloads a specified cog (module).
- **Arguments:**
  - **cog:** Name of the cog to reload (filename without .py).
- **Usage Example:**
  
text
  /reload cog:coininvoice
  -reload coininvoice


### /move and -move (or -mv)
- **Description:** Moves a player to another user's voice channel or to a specified voice channel.
- **Arguments:**
  - **player:** The user to be moved.
  - **target_user (optional):** The target user (must be in a voice channel).
  - **target_channel (optional):** The target voice channel.
- **Usage Examples:**
  
text
  /move player:@User target_user:@TargetUser
  -move @User @TargetUser    (if target is a user in a voice channel)
  -mv @User #VoiceChannel    (if target is a voice channel)


### /message and -msg (or -message)
- **Description:** Sends a message to a channel.
- **Arguments:**
  - **message:** The message content.
  - **channel (optional):** The target text channel (defaults to the current channel if omitted).
- **Usage Examples:**
  
text
  /message message:"Hello, world!" channel:#general
  -msg Hello, world!
  -message #announcements Important update!


### /rolemap and -rolemap
- **Description:** Displays all server roles along with their IDs.
- **Requirements:** Must have the **Manage Server** permission.
- **Usage Example:**
  
text
  /rolemap
  -rolemap

*Note: If the role list exceeds 2000 characters, a text file is uploaded instead.*

### /setstatus and -setstatus
- **Description:** Sets the bot's status and activity.
- **Arguments:**
  - **status:** Bot status (*online, idle, dnd, invisible*).
  - **activity_type:** Type of activity (*playing, watching, listening, competing*).
  - **message:** Custom status message.
- **Usage Examples:**
  
text
  /setstatus status:online activity_type:playing message:"Minecraft"
  -setstatus online playing Minecraft


### /whichvc and -wv (or -whichvc)
- **Description:** Checks which voice channel a user is in.
- **Arguments:**
  - **user (optional):** The target user. If omitted, defaults to the command invoker.
- **Usage Examples:**
  
text
  /whichvc user:@User
  -wv @User
  -wv   (when replying to a user's message, checks that user)


### /sale
**Description:**  
Shows sales statistics based on a query, aggregating data from active service invoices, logged service invoices, and coin invoices.  
Displays total revenue, total invoices, service revenue, coins profit, and invoice counts for services and coins.

**Usage Examples:**  
- /sale lifetime – Displays lifetime sales stats.  
- /sale 2025 – Displays stats for the year 2025.  
- /sale january – Displays stats for January (across all years).

### /history
**Description:**  
Retrieves the purchase history for a specified user.  
- By default, it shows full purchase history (active service, logged service, and coin invoices).  
- Optionally, using a category (e.g. "coins") filters the history to show only coin purchases, along with total coin profit.  
Paginated embeds allow navigation through multiple pages.

**Usage Examples:**  
- /history user:@User – Retrieves full purchase history for @User.  
- /history user:@User coins – Retrieves only coin purchase history for @User with total profit.

### /services
**Description:**  
Lists active service invoices from the system.  
- Use "active" to display all active invoices.  
- Or provide a specific service name (e.g., "celestia") to filter the active invoices.

**Usage Examples:**  
- /services active – Displays all active service invoices.  
- /services celestia – Displays active invoices for the service "Celestia".


## Running the Bot

Make sure your bot is added to a Discord server with the appropriate permissions to send messages and manage roles. After configuring and running the bot, it will automatically start interacting with users as per the defined tasks.

## Contributing

We welcome contributions! To contribute:

1. Fork the repository.
2. Create a new branch (`git checkout -b feature-name`).
3. Make your changes and commit them (`git commit -am 'Add feature'`).
4. Push to the branch (`git push origin feature-name`).
5. Create a new pull request.

Let me know if you’d like me to sort commands alphabetically, collapse advanced ones under a heading, or generate a table of contents too 📘