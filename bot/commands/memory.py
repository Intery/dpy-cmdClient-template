from cmdClient import cmd

from utils.ctx_addons import embedreply  # noqa


"""
A mini-module demonstrating usage of data storage and command metadata.
"""


@cmd("remember",
     group="Misc",
     desc="A simple command to remember some text.")
async def cmd_remember(ctx):
    """
    Usage``:
        remember <text>
    Description:
        Remember the provided text for later retrieval with `recall`.
    Arguments::
        text: Text to remember
    Examples``:
        remember Use meaningful commit messages.
    Related:
        recall
    """
    if not ctx.arg_str:
        return await ctx.error_reply("You must give me some text to remember!")

    ctx.client.data.users.set(ctx.author.id, "remember_text", ctx.arg_str)

    await ctx.reply("I will remember that!")


@cmd("recall",
     group="Misc",
     desc="Recall text stored with remember.")
async def cmd_recall(ctx):
    """
    Usage``:
        recall
    Description:
        Responds with the text stored using the `remember` command.
    Related:
        remember
    """
    text = ctx.client.data.users.get(ctx.author.id, "remember_text")

    if not text:
        await ctx.reply("You haven't given me anything to remember yet.")
    else:
        await ctx.embedreply("You asked me to remember the following:\n{}".format(text))
