# Contributing

## Before making a contribution

- Take a look over at the [issues](https://github.com/osu-Norge/osu-rank-tracker/issues) tab.
- If what you're planning to do is not listed, make an issue and ask about whether or not the feature you want to add is needed _before_ making a pull request.

## Code guidelines

- Code should meet the PEP8 standard, however with 120 characters as the max length per line instead of 80.
- Use single `'` quotes unless it's necessary to use double quotation marks `"`.
- Use double quotation marks `"` for multi-line comments.
- Variable names should be written in snake_case.
- Implement using slash commands

It is preferred that you also consider the following, however it is not required:

- Use embeds. Default embed color should be set to `interaction.client.user.color` unless there's a reason to use another color.

## Docstrings

Every function gets a docstring in this style, except functions nested inside other functions:

```python
def greet(self, name: str) -> str:
    """
    Greets the invoking user using the inputted name

    Parameters
    ----------
    name (str): The user's inputted name

    Returns
    ----------
    (str): A greeting
    """

    return f'Hello, {name}'
```

Leave out sections that would be empty. Write unions as `a | b`, and the return value as `(type): description`. Optional parameters should say what the default is, e.g. `Defaults to the invoking user`.

Some parameters appear everywhere, and are described the same way each time:

- `interaction (discord.Interaction): The slash command interaction`
- `ctx (commands.Context): The command context`
- `bot (commands.Bot): The bot instance`
