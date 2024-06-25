from .MongoDB import MongoDB

end_point_collection = MongoDB("admin", "api_end_point")


class EndPoint:
    def __init__(self, email) -> None:
        self.__dict__["email"] = email

    async def get(self, key=None, value=None, query=None):
        if query:

            return await end_point_collection.get(query=query)
        if key:
            return await end_point_collection.get(query={key: value})
        return await end_point_collection.get(query={"email": self.__dict__["email"]})

    async def set(self, request, response):
        return await end_point_collection.set(
            {
                "email": self.__dict__["email"],
                "request": request,
                "response": response,
            }
        )
