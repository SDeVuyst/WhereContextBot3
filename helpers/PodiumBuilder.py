from PIL import Image, ImageDraw, ImageFont

import discord
import io
import requests
import random

class PodiumBuilder:
    def __init__(self, bot) -> None:
        self.bot = bot

        self.definedPodiums = {
            "222415043550117888": "ba/BaPodium",
            "512256261459542019": "meng/MengPodium",
            "559715606014984195": "gible/GiblePodium",
            "339820557086228490": "jakob/JakobPodium",
            "756527409876041859": "zeb/ZebPodium"
        }

    async def getLeaderboard(self, leaderboard, command):
        # self.bot.logger.info(leaderboard)

        #  load background
        bg = Image.open('media/images/LeaderboardNoPod.png')

        # load fonts
        fontm = ImageFont.truetype("media/fonts/contm.ttf", size=120)
        fontb = ImageFont.truetype("media/fonts/contb.ttf", size=175)

        # create object for drawing
        draw = ImageDraw.Draw(bg)

        # add places 1-9
        for i, stat in enumerate(leaderboard, start=0):
            
            # get user info
            user_id, count = tuple(stat)
            user = await self.bot.fetch_user(int(user_id))
            
            # is podium
            if i < 3:
                pasteCoords = [(900, 900), (200, 900), (1700, 900)]
                
                p = self.getPodiumImage(user_id, i+1)
                bg.paste(p, pasteCoords[i], p)
            
            # is text
            else:
                # profile picture
                pfp = Image.open(requests.get(user.display_avatar.url, stream=True).raw)
                pfp = pfp.resize((230, 230))
                bg.paste(pfp, (525, 2200 + (i-3)*340))

                # username
                draw.text(
                    (1200, 2360 + (i-3)*340), 
                    text=user.display_name, 
                    align='center', font=fontm, anchor='mm', fill=(255, 104, 1)
                )
                # count
                draw.text(
                    (1960, 2365 + (i-3)*340), 
                    text=str(count), 
                    align='center', font=fontm, anchor='mm', fill=(255, 104, 1)
                )

        # draw title
        draw.text(
            (1285, 260),
            text=command,
            align='center', font=fontb, anchor='mm', fill=(255, 104, 1)
        )

        # create buffer
        buffer = io.BytesIO()

        # save PNG in buffer
        bg.save(buffer, format='PNG')    

        # move to beginning of buffer so `send()` it will read from beginning
        buffer.seek(0)

        return discord.File(buffer, 'leaderboard.png')
    

    def getPodiumImage(self, user_id, place, resize=True):
        location = self.definedPodiums.get(str(user_id), "default/DefaultPodium")

        if location == "GiblePodium":
            # 1/20 chance gible podium is shiny
            if random.randint(0, 20) == 20:
                location = "ShinyGiblePodium"
            
        image = Image.open(f'media/images/{location}{place}.png')

        if resize:
            new_height = 800 + (place-1)*200
            new_width  = int(new_height * image.size[0] / image.size[1])
            return image.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        return image

    
    def getAllPodiumsImage(self, user_id):
        p1 = remove_transparency(self.getPodiumImage(user_id, 1, False))
        p2 = remove_transparency(self.getPodiumImage(user_id, 2, False))
        p3 = remove_transparency(self.getPodiumImage(user_id, 3, False))

        dst = get_concat_h_multi_blank([p2, p1, p3], p1.height)
        # paste pods on correct location

        # create buffer
        buffer = io.BytesIO()

        # save PNG in buffer
        dst.save(buffer, format='PNG')    

        # move to beginning of buffer so `send()` it will read from beginning
        buffer.seek(0)

        return discord.File(buffer, 'podium.png')   
    

def get_concat_h_multi_blank(im_list, height):
    _im = im_list.pop(0)
    for im in im_list:
        _im = get_concat_h_blank(_im, im, height)
    return _im


def get_concat_h_blank(im1, im2, height, color=(44, 45, 47)):
    dst = Image.new('RGB', (im1.width + im2.width, height), color)
    dst.paste(im1, (0, 0))
    dst.paste(im2, (im1.width, 0))
    return dst


def remove_transparency(im, color=(44, 45, 47)):
    im = im.convert("RGBA")
    new_image = Image.new("RGBA", im.size, color)
    new_image.paste(im, mask=im)

    return new_image.convert("RGB")