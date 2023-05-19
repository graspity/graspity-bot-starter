# graspity-bot-starter

Copy this repo and create a new one!   

**DO NOT PUSH TO THIS REPO** - this is a starter repo.

## Dependencies

- `websocket` - `pip3 install websocket-client`
- `rel` - `pip3 install rel`
- json
- requests

## Where to put my code?

Put your code in the `processPageAndReply` method in `bot.py` file

```python
def processPageAndReply(ws, channelId, originalMessage, page)
```

## Important

Please make sure that bot filters its own message in order not to get into a loop. Or it will be throttled.
