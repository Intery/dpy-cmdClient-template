import imp
import sys
import os
import traceback
import logging
import discord

from logger import log
from config import conf


# Command dictionary of the form {cmdname: cmdfunc}
cmds = {}


# Command decorator for adding new commands to cmds
def cmd(name, **kwargs):
    def wrapper(func):
        cmds[name] = func
        return func
    return wrapper


class cmdClient(discord.Client):
    async def on_ready(self):
        """
        Client has logged into discord and completed initialisation.
        Log a ready message with some basic statistics and info.
        """
        ready_str = (
            "Logged in as {client.user}\n"
            "User id {client.user.id}\n"
            "Logged in to {guilds} guilds\n"
            "------------------------------\n"
            "Prefix is '{prefix}'\n"
            "Loaded {commands} commands\n"
            "------------------------------\n"
            "Ready to take commands!\n"
        ).format(
            client=self,
            guilds=len(self.guilds),
            prefix=conf['prefix'],
            commands=len(cmds)
        )
        log(ready_str)

    async def on_error(self, event_method, *args, **kwargs):
        """
        An exception was caught in one of the event handlers.
        Log the exception with a traceback, and continue on.
        """
        log("Ignoring exception in {}\n{}".format(event_method, traceback.format_exc()),
            level=logging.ERROR)

    async def on_message(self, message):
        """
        Handle incoming messages.
        If the message contains a valid command, pass the message to run_cmd
        """
        # Check whether the message starts with the set prefix
        content = message.content.strip()
        if not content.startswith(conf['prefix']):
            return

        # If the message starts with a valid command, pass it along to run_cmd
        content = content[len(conf['prefix']):].strip()
        cmdname = next((cmdname for cmdname in cmds if content[:len(cmdname)].lower() == cmdname), None)

        if cmdname is not None:
            await self.run_cmd(message, cmdname, content[len(cmdname):].strip())

    async def run_cmd(self, message, cmdname, arg_str):
        """
        Run a command and pass it the command message and the arg_str.

        Parameters
        ----------
        message: discord.Message
            The original command message.
        cmdname: str
            The name of the command to execute.
        arg_str: str
            The remaining content of the command message after the prefix and command name.
        """
        log(("Executing command '{cmdname}' "
             "from user '{message.author}' ({message.author.id}) "
             "in guild '{message.guild}' ({message.guild.id}).\n"
             "{content}").format(
                 cmdname=cmdname,
                 message=message,
                 content='\n'.join(('\t' + line for line in message.content.splitlines()))),
            context=message.id)
        cmdfunc = cmds[cmdname]

        try:
            await cmdfunc(self, message, arg_str)
        except Exception:
            log("The following exception encountered executing command '{}'.\n{}".format(cmdname, traceback.format_exc()),
                context=message.id,
                level=logging.ERROR)

    def load_dir(self, dir):
        """
        Import all modules in a directory.
        Primarily for the use of importing new commands.
        """
        loaded = 0
        initial_cmds = len(cmds)

        for fn in os.listdir(dir):
            path = os.path.join(dir, fn)
            if fn.endswith(".py"):
                sys.path.append(dir)
                imp.load_source("bot_module_" + str(fn), path)
                sys.path.remove(dir)
                loaded += 1
        log("Imported {} modules from '{}', with {} new commands!".format(loaded, dir, len(cmds)-initial_cmds))
