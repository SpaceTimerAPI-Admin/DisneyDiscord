from discord.ext import tasks

latest_restaurants = []

@tasks.loop(minutes=60)
async def refresh_restaurants():
    global latest_restaurants
    print("🔄 Refreshing restaurant list...")
    latest_restaurants = await get_all_restaurants()
    print(f"✅ Loaded {len(latest_restaurants)} restaurants.")

async def setup_slash_commands(bot):
    # Register slash command here...
    tree = app_commands.CommandTree(bot)

    @tree.command(name="request", description="Request a Disney Dining Alert")
    async def request(interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        await interaction.followup.send("🍽️ What restaurant are you looking for?")

        def check(msg):
            return msg.author.id == interaction.user.id and msg.channel == interaction.channel

        try:
            msg = await bot.wait_for("message", check=check, timeout=60)
            query = msg.content.strip()

            from rapidfuzz import process
            match, score, _ = process.extractOne(query, latest_restaurants)
            if score > 80:
                await interaction.followup.send(f"✅ Matched: **{match}**. What date? (MM/DD/YYYY)")
            else:
                await interaction.followup.send("❌ No close match. Try again with `/request`.")
        except asyncio.TimeoutError:
            await interaction.followup.send("⏰ Timeout. Start again with `/request`.")

    await tree.sync()

    # ✅ Start the refresh loop once the bot is ready
    if not refresh_restaurants.is_running():
        refresh_restaurants.start()
