import aiohttp
from uuid import uuid4
from .exceptions import InvalidArgument, InvalidKey


class AsyncRSAP:
    def __init__(self, api_key: str, **kwargs) -> None:
        """The async class for interacting with the Random Stuff API. It uses the aioHTTP module to get the responses from the API..

        Args:
            api_key (str): The API key which you can get from https://api-info.pgamerx.com/register
            dev_name (str, optional): The name of the developer who coded the chatbot. Used in responses. Defaults to None.
            unique_id (str, optional): The Unique ID to create custom sessions for each user. Defaults to None.
            bot_name (str, optional): The name of the chatbot. Used in responses. Defaults to None.
            type (str, optional): The type of API to use. Stable is recommended but can also be `unstable`. Defaults to "stable".
            language (str, optional): The language to chat with the chatbot in. Defaults to "en".
        """
        self.key = api_key,
        self.dev = kwargs.get("dev_name", "Hunter"),
        self.bot = kwargs.get("bot_name", "PyChat"),
        self.type = kwargs.get("type", "stable"),
        self.language = kwargs.get("language", "en")
        self.headers = {"x-api-key": self.key[0]}
        self._jokes_types = ("any", "dev", "spooky", "pun")
        self._image_types = ("aww", "duck", "dog", "cat", "memes",
                             "dankmemes", "holup", "art", "harrypottermemes", "facepalm")
        self.ai_links = ("https://api.pgamerx.com/v3/pro/ai/response", "https://api.pgamerx.com/v3/ultra/ai/response",
                         "https://api.pgamerx.com/v3/biz/ai/response", "https://api.pgamerx.com/v3/mega/ai/response")
        self.working_ai_links = []

    async def ai_response(self, message: str, unique_id: str = None) -> str:
        """The async method to get the AI response to a given message

        Args:
            message (str): The message to get the response of
            unique_id (str): The Unique ID to create custom sessions for each user. Defaults to None.

        Raises:
            InvalidKey: The exception raised when a wrong key is provided and the API returns a 401 error code

        Returns:
            str: The response recieved from the API
        """
        params = {"unique_id": unique_id or str(uuid4()), "dev_name": self.dev or "Hunter",
                  "bot_name": self.bot or "PyChat", "language": self.language or "en", "message": message, "type": self.type or "stable"}
        async with aiohttp.ClientSession(headers=self.headers) as ses:
            for links in self.ai_links:
                if ses.get(links, params=params).status != 200:
                    raise InvalidKey("You passed in an Invalid API KEY")
                if ses.get(links, params=params).status == 200:
                    if await ses.get(links, params=params).json()[0]["message"] != "Unauthorized":
                        return
                    if await ses.get(links, params=params).json()[0]["message"] != "Unauthorized":
                        self.working_ai_links.append(links)
            if len(self.working_ai_links) == 0:
                async with ses.get("https://api.pgamerx.com/v3/ai/response", params=params) as response:
                    if response.status == 401:
                        raise InvalidKey("You passed in an Invalid API KEY")
                    if response.status == 200:
                        text = await response.json()
                        return text[0]["message"]
            if len(self.working_ai_links) != 0:
                async with ses.get(self.working_ai_links[0], params=params) as response:
                    if response.status == 401:
                        raise InvalidKey("You passed in an Invalid API KEY")
                    if response.status == 200:
                        text = await response.json()
                        return text[0]["message"]

    async def joke(self, type: str = "any") -> dict:
        f"""The async method to get a joke of a given category

        Args:
            type (str, optional): The type of the joke to get. The types supported are {self._jokes_types}. Defaults to "any".

        Raises:
            InvalidArgument: The exception raised when a non existing type is provided

            InvalidKey: The exception raised when a wrong key is provided and the API returns a 401 error code

        Returns:
            dict: The dict of the response recieved. It does not return str because the joke can be two way or one way. Though I will change it in the future to return the joke
        """
        if type.lower() not in self._jokes_types:
            raise InvalidArgument(
                "The arguments you specified is not a valid type")
        if type.lower() in self._jokes_types:
            async with aiohttp.ClientSession(headers=self.headers) as session:
                async with session.get(url=f'https://api.pgamerx.com/v3/joke/{type}') as response:
                    if response.status == 401:
                        raise InvalidKey("You passed in an Invalid API KEY")
                    if response.status == 200:
                        text = await response.json()
                        return text

    async def image(self, type: str = "memes") -> str:
        f"""The async method to get an image from the API

        Args:
            type (str): The type of image to return. The types supported are {self._image_types}. Defaults to memes

        Raises:
            InvalidArgument: The exception raised when a non existing type is provided

            InvalidKey: The exception raised when a wrong key is provided and the API returns a 401 error code

        Returns:
            str: The image URL
        """
        if type.lower() not in self._image_types:
            raise InvalidArgument(
                "The arguments you specified is not a valid type")
        if type.lower() in self._image_types:
            async with aiohttp.ClientSession(headers=self.headers) as session:
                async with session.get(url=f'https://api.pgamerx.com/v3/image/{type}') as response:
                    if response.status == 401:
                        raise InvalidKey("You passed in an Invalid API KEY")
                    if response.status == 200:
                        return await response.json()[0]
