When moving the robber, we need to do 2 things
1. Move the robber to where the player says
2. Take a random resource from a player on the hex

Let's do 1 first: ::

    def choose_hex(hex_coords, prompt):
        # Label all the hexes with a letter
        hex_list = [game.board.hexes[i] for i in hex_coords]
        hex_list.sort(key = lambda h: get_coord_sort_by_xy(h.coords))
        hex_labels = {hex_list[i]: label_letters[i] for i in range(len(hex_list))}
        renderer.render_board(hex_labels = hex_labels)
        letter = input(prompt)
        letter_to_hex = {v: k for k, v in hex_labels.items()}
        return letter_to_hex[letter].coords

    ...

    def move_robber(player):
        # Don't let the player move the robber back onto the same hex
        hex_coords = choose_hex([c for c in game.board.hexes if c != game.board.robber], "Where do you want to move the robber? ")
        game.board.robber = hex_coords

Now the player can move the knight to any hex they choose! Now let's steal a card from someone: ::

    # Choose a player to steal a card from
    potential_players = list(game.board.get_players_on_hex(hex_coords))
    print("Choose who you want to steal from:")
    for p in potential_players:
        i = game.players.index(p)
        print("%d: Player %d" % (i + 1, i + 1))
    p = int(input('->  ')) - 1
    # If they try and steal from another player they lose their chance to steal
    to_steal_from = game.players[p] if game.players[p] in potential_players else None
    if to_steal_from:
        resource = to_steal_from.get_random_resource()
        player.add_resources({ resource: 1})
        to_steal_from.remove_resources({ resource: 1 })
        print("Stole 1 %s for player %d" % (resource, p + 1))

Perfect! Now the player can steal a random card form the player of their choice.
Now back at the top of our game loop: ::

    if dice == 7:
        move_robber(current_player)

 We're not going to implement checking for which players have over 7 resource, since it's difficult to let the players choose what cardsto get rid of through just text format.
 But it would be something like this: ::

    for i in range(len(game.players)):
        total_resources = sum[amount for res, amount in game.players[i].resources]
        if total_resources > 7:
            print("You need to lose %d resources" % (total_resources - 7))
            # Fancy-dancy UI stuff to let the player select 7 resources

We're almost done our text game! The last part is victory points!
