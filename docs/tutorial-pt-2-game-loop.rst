Let's implement the actual game phase now. It will look something like: ::

    # Roll the dice
    # Distribute resources
    # Allow the player to perform actions

The first 2 are very easy to do: ::

    import random

    ...

    current_player_num = 0
    while True:
        current_player = game.players[current_player_num]
        print("Player %d, it is your turn now" % (current_player_num + 1))
        # Roll the dice
        dice = random.randint(1, 6) + random.randint(1, 6)
        print("Player %d rolled a %d" % (current_player_num + 1, dice))
        if dice == 7:
            # TBA
            pass
        else:
            game.add_yield_for_roll(dice)

Now let's show the player what resources they have.
Each player's resources is available as a dict of resource -> amount: ::

    print("Player %d, you have these resources:" % (current_player_num + 1))
    for res, amount in current_player.resources:
        print("    %s: %d" % (res, amount))

It'll look something like this: ::

    Player 1, you have these resources:
        Lumber: 0
        Brick: 0
        Wool: 1
        Grain: 1
        Ore: 0

Now in the final part of the game loop setup, let's have the player choose what they want to do.
We'll put it in a loop so they can choose as many things as they want: ::

    choice = 0
    while choice != 4:
        # Print the player's resources
        print("Player %d, you have these resources:" % (current_player_num + 1))
        for res, amount in current_player.resources:
            print("%s: %d" % (res, amount))
        # Prompt the player for an action
        print("Choose what to do:")
        print("1 - Build something")
        print("2 - Trade")
        print("3 - Play a dev card")
        choice = int(input("->  "))
        if choice == 1:
            pass
        elif choice == 2:
            pass
        elif choice == 3:
            pass
        current_player_num = (current_player_num + 1) % len(game.players)

Perfect! In the next part we'll implement the building choice that will allow the player to build new settlements, roads and cities.
