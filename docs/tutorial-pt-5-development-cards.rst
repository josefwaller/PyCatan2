Let's go back to the building section of our game and add the ability to build a development card: ::

    from pycatan import Game, DevelopmentCard

    ...

    if choice == 1:
        print("What do you want to build? ")
        print("1 - Settlement")
        print("2 - City")
        print("3 - Road")
        print("4 - Development Card")

        building_choice = int(input('->  '))

        ...

        elif building_choice == 4:
            # Check the player has the resources to build a development card
            if not current_player.has_resources(DevelopmentCard.get_required_resources()):
                print("You do not have the resources to build a development card")
                continue
            # Build a card and tell the player what they build
            dev_card = game.build_development_card(current_player)
            print("You built a %s card" % dev_card)

Now the player can build a development card! Let's list the development cards the player has with the resources: ::

    print("and you have these development cards")
    for dev_card, amount in current_player.development_cards.items():
        print("    %s: %d" % (dev_card, amount))

Perfect! Now for the hard part - implementing these development cards.
PyCatan doesn't implement playing development cards, but provides many utility methods that makes implementing them easier.
First let's have the player choose a dev card to play: ::

    elif choice == 3:
        # Choose a development card
        print("What card do you want to play?")
        dev_cards = [card for card, amount in current_player.development_cards.items() if amount > 0 and card is not DevelopmentCard.VICTORY_POINT]
        for i in range(len(dev_cards)):
            print("%d: %s" % (i, dev_cards[i]))
        card_to_play = dev_cards[int(input('->  '))]

Now let's implement each of the development card types: ::

    # We'll implement this later
    def move_robber(player):
        pass

    ...

    # Doesn't actually do anything but remove the card from the player's hand and recalculate largest army
    game.play_development_card(current_player, card_to_play)

    if card_to_play is DevelopmentCard.KNIGHT:
        move_robber(current_player)

    elif card_to_play is DevelopmentCard.YEAR_OF_PLENTY:
        # Have the player choose 2 resources to receive
        for _ in range(2):
            resource = choose_resource("What resource do you want to receive?")
            # Add that resource to the player's hand
            current_player.add_resources({resource: 1})

    elif card_to_play is DevelopmentCard.ROAD_BUILDING:
        # Allow the player to build 2 roads
        for _ in range(2):
            valid_path_coords = game.board.get_valid_road_coords(current_player)
            path_coords = choose_path(valid_path_coords, "Choose where to build a road: ")
            game.build_road(current_player, path_coords, cost_resources = False)

    elif card_to_play is DevelopmentCard.MONOPOLY:
        # Choose a resource
        resource = choose_resource("What resource do you want to take?")
        # Remove that resource from everyone else's hands and add it to the current player's hand
        for i in range(len(game.players)):
            player = game.players[i]
            if player is not current_player:
                amount = player.resources[resource]
                player.remove_resources({ resource: amount })
                current_player.add_resources({ resource: amount })
                print("Took %d from player %d" % (amount, i + 1))

And done! The player can now play any development card they want, except knights, which we'll do next.
