import strawberry
from schema.schema import FavoriteLocation

# Define a mutation for saving a favorite location
@strawberry.type
class Mutation:
    @strawberry.mutation
    def save_favorite_location(
        self,
        city: str,
    ) -> FavoriteLocation:

        # Create a FavoriteLocation object with the input parameters
        favorite_location = FavoriteLocation(city=city)

        # Return the saved FavoriteLocation object
        return favorite_location
