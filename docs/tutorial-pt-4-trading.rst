Let's implement the second choise now, allowing the player to trade in 4:1 resources (or 2:1 if they are connected to a harbor).
PyCatan provides the very useful `get_possible_trades()` method: ::

    elif choice == 2:
        possible_trades = list(current_player.get_possible_trades())
        print("Choose a trade: ")
        for i in range(len(possible_trades)):
            print("%d:" % i)
            for res, amount in possible_trades[i].items():
                print("    %s: %d" % (res, amount))

The player should see something like this, assuming they have 4 grain: ::

    Choose a trade:
    0:
        Grain: -4
        Lumber: 1
    1:
        Grain: -4
        Wool: 1
    2:
        Grain: -4
        Brick: 1
    3:
        Grain: -4
        Ore: 1

Now we simply have them choose one: ::

    trade_choice = int(input('->  '))
    trade = possible_trades[trade_choice]
    current_player.add_resources(trade)

And now the player has the option to trade in 4:1 and 2:1 resources!
PyCatan handles checking which harbors they're connected to and which resources they have 4 of.
