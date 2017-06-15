import os
import discord
import aiohttp
import geocoder
from discord.ext import commands


class Weather:
    """
    Bot commands to retrieve weather API data.
    """

    def __init__(self, bot):
        self.bot = bot

    async def weather_api_call(self, endpoint, zip_code):
        async with aiohttp.ClientSession() as session:
            url = 'http://api.wunderground.com/api/c80325c858abf20d/{}/q/{}.json'.format(
                endpoint,
                zip_code
            )
            async with session.get(url) as resp:
                if resp.status is not 200:
                    await self.bot.say('```Error: cannot fetch wunderground.com data.```')
                    raise aiohttp.errors.ClientConnectionError
                else:
                    return await resp.json()

    @commands.command(pass_context=True)
    async def weather(self, ctx, zip_code: int):
        """
        Return current weather conditions.
        """
        author = ctx.message.author
        try:
            data = await self.weather_api_call(endpoint='conditions', zip_code=zip_code)
        except Exception as e:
            await self.bot.say("The api threw an error, please try again later. Error is `{}`".format(e))
            print(e)
        # You also might want to send this error to your dedicated logging webhook if you have one.
            return

        try:
            cty = "{}".format( data['current_observation']['display_location']['full'] )
            wth = "{}".format( data['current_observation']['weather'] )
            tmp = "{}".format( data['current_observation']['temperature_string'] )
            wnd = "{}".format( data['current_observation']['wind_string'] )
            hmd = "{}".format( data['current_observation']['relative_humidity'] )
            rai = "{}".format( data['current_observation']['precip_today_string'] )
            e = discord.Embed(colour=author.colour)
            e.add_field(name="City:", value=cty )
            e.add_field(name="Weather:", value=wth )
            e.add_field(name="Tempature:", value=tmp )
            e.add_field(name="Wind:", value=wnd)
            e.add_field(name="Humidity:", value=hmd )
            e.add_field(name="Rain:", value=rai )
            await self.bot.say(embed=e)
        except Exception as e:
            await self.bot.say(e)

    @commands.command(pass_context=True)
    async def forecast(self, ctx, zip_code: int):
        """
        Return three day weather forecast.
        """
        author = ctx.message.author
        data = await self.weather_api_call(endpoint='forecast', zip_code=zip_code)

        try:
            """await self.bot.say(
                '```{}:\n\n{}\n\n{}:\n\n{}\n\n{}:\n\n{}\n\n{}:\n\n{}\n\n{}:\n\n{}\n\n{}:\n\n{}```'.format(
                    data['forecast']['txt_forecast']['forecastday'][0]['title'],
                    data['forecast']['txt_forecast']['forecastday'][0]['fcttext'],
                    data['forecast']['txt_forecast']['forecastday'][1]['title'],
                    data['forecast']['txt_forecast']['forecastday'][1]['fcttext'],
                    data['forecast']['txt_forecast']['forecastday'][2]['title'],
                    data['forecast']['txt_forecast']['forecastday'][2]['fcttext'],
                    data['forecast']['txt_forecast']['forecastday'][3]['title'],
                    data['forecast']['txt_forecast']['forecastday'][3]['fcttext'],
                    data['forecast']['txt_forecast']['forecastday'][4]['title'],
                    data['forecast']['txt_forecast']['forecastday'][4]['fcttext'],
                    data['forecast']['txt_forecast']['forecastday'][5]['title'],
                    data['forecast']['txt_forecast']['forecastday'][5]['fcttext']
                )
            )"""
            if author.colour:
                k = author.colour
            else:
                k = discord.Colour.blue()
            e = discord.Embed(colour=k)
            e.add_field(name=data['forecast']['txt_forecast']['forecastday'][0]['title'], value=data['forecast']['txt_forecast']['forecastday'][0]['fcttext'], inline=False)
            e.add_field(name=data['forecast']['txt_forecast']['forecastday'][1]['title'], value=data['forecast']['txt_forecast']['forecastday'][1]['fcttext'], inline=False)
            e.add_field(name=data['forecast']['txt_forecast']['forecastday'][2]['title'], value=data['forecast']['txt_forecast']['forecastday'][2]['fcttext'], inline=False)
            e.add_field(name=data['forecast']['txt_forecast']['forecastday'][3]['title'], value=data['forecast']['txt_forecast']['forecastday'][3]['fcttext'], inline=False)
            e.add_field(name=data['forecast']['txt_forecast']['forecastday'][4]['title'], value=data['forecast']['txt_forecast']['forecastday'][4]['fcttext'], inline=False)
            e.add_field(name=data['forecast']['txt_forecast']['forecastday'][5]['title'], value=data['forecast']['txt_forecast']['forecastday'][5]['fcttext'], inline=False)
            await self.bot.say(embed=e)
        except Exception as e:
            await self.bot.say(e)

    @commands.command(pass_context=True)
    async def radar(self, ctx, zip_code: int):
        """
        Display static radar image.
        """
        channel = ctx.message.channel

        try:
            data = await self.weather_api_call(endpoint='conditions', zip_code=zip_code)
            if data['current_observation']['display_location']['zip'] == str(zip_code):
                async with aiohttp.ClientSession() as session:
                    url = 'http://api.wunderground.com/api/c80325c858abf20d/radar/q/{}.png?newmaps=1&smooth=1&noclutter=1'.format(
                        zip_code
                    )
                    async with session.get(url) as resp:
                        if resp.status is not 200:
                            await self.bot.say('```Error: cannot fetch wunderground.com data.```')
                            raise aiohttp.errors.ClientConnectionError
                        else:
                            image_file = '{}.png'.format(zip_code)
                            with open(image_file, 'wb') as f:
                                while True:
                                    chunk = await resp.content.read()
                                    if not chunk:
                                        break
                                    f.write(chunk)
                                    await self.bot.send_file(channel, image_file)
                                    f.close()
                                    os.remove(image_file)
        except:
            await self.bot.say('```prolog\nError: invalid zip code. Or I dont have the attach_files permission.```')


def setup(bot):
    bot.add_cog(Weather(bot))
