<!-- prettier-ignore -->
!!! warning
    Connectors are currently in a beta stage.

## Connectors

Connectors are a powerful add-on component to Stillroom.
They allow for certain actions to be translated to api calls to external services.

<!-- prettier-ignore -->
!!! danger
    In order for this application to push data to external providers it needs to store authentication information.
    Please use read only/separate accounts or app passwords wherever possible.

for the configuration please see [Configuration](https://github.com/BrendenWalker/Stillroom/blob/develop/docs/system/configuration.md#connectors)

## Current Connectors

### HomeAssistant

The current HomeAssistant connector supports the following features:
1. Push newly created shopping list items.
2. Pushes all shopping list items if a recipe is added to the shopping list.
3. Removed todo's from HomeAssistant IF they are unchanged and are removed through Stillroom.

#### How to configure:

Step 1:
1. Generate a HomeAssistant Long-Lived Access Tokens
2. Get/create a todo list entry you want to sync too.
3. Create a connector
4. ???
5. Profit
