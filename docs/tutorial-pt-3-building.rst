Now it's easy to implement 1. Let's start with roads ::

    # We'll use this to determine if the player has enough resources to build a road
    from pycatan.board import BuildingType

    ...

    if choice == 1:
        print("What do you want to build? ")
        print("1 - Settlement")
        print("2 - City")
        print("3 - Road")
        building_choice = int(input("->  "))
        if building_choice == 1:
            pass
        elif building_choice == 2:
            pass
        elif building_choice == 3:
            # Check the player has enough resources
            if not current_player.has_resources(BuildingType.ROAD.get_required_resources()):
                print("You don't have enough resources to build a road")
                continue
            # Get the valid road coordinates
            valid_coords = game.board.get_valid_road_coords(current_player)
            # If there are none
            if not valid_coords:
                print("There are no valid places to build a road")
                continue
            # Have the player choose one
            path_coords = choose_path(valid_coords, "Where do you want to build a road?")
            game.build_road(current_player, path_coords)

Building settlements and cities is very similar: ::

     elif building_choice == 2:
        # Check the player has enough resources
        if not current_player.has_resources(BuildingType.CITY.get_required_resources()):
            print("You don't have enough resources to build a city")
            continue
        # Get the valid coords to build a city at
        valid_coords = game.board.get_valid_city_coords(current_player)
        # Have the player choose one
        coords = choose_intersection(valid_coords, "Where do you want to build a city?  ")
        # Build the city
        game.upgrade_settlement_to_city(current_player, coords)
    elif building_choice == 3:
        # Check the player has enough resources
        if not current_player.has_resources(BuildingType.ROAD.get_required_resources()):
            print("You don't have enough resources to build a road")
            continue
        # Get the valid road coordinates
        valid_coords = game.board.get_valid_road_coords(current_player)
        # If there are none
        if not valid_coords:
            print("There are no valid places to build a road")
            continue
        # Have the player choose one
        path_coords = choose_path(valid_coords, "Where do you want to build a road?")
        game.build_road(current_player, path_coords)

And voila! The players can now build roads, settlements and cities!
