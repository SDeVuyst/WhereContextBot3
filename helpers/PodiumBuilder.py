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
            "756527409876041859": "zeb/ZebPodium",
            "453136562885099531": "wouter/WouterPodium"
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


        podiums = []

        # add places 1-9
        for i, stat in enumerate(leaderboard):
            
            # get user info
            user_id, count = tuple(stat)
            user = await self.bot.fetch_user(int(user_id))
            
            # is podium, save info for later
            if i < 3:       
                podiums.append((user_id, count))
            
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

        # add podium
        podiumImage = self.getAllPodiumsImage([pod[0] for pod in podiums], False, color=(62,62,62))
        podiumImage = resize_image(podiumImage, 2000)
        remaining_width = bg.width - podiumImage.width

        bg.paste(podiumImage, (remaining_width//2, 1850 - podiumImage.height))

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
    

    def getPodiumImage(self, user_id, place):
        location = self.definedPodiums.get(str(user_id), "default/DefaultPodium")

        if location == "GiblePodium":
            # 1/20 chance gible podium is shiny
            if random.randint(0, 20) == 20:
                location = "ShinyGiblePodium"
            
        image = Image.open(f'media/images/{location}{place}.png')

        return image

    
    def getAllPodiumsImage(self, user_ids, return_file=True, padding=200, color=(44, 45, 47)):
        # create normalised images for every given podium
        if len(user_ids) == 1:
            order = [1]
        elif len(user_ids) == 2:
            order = [2, 1]
        else:
            order = [2, 1, 3]

        podiums = [remove_transparency(self.getPodiumImage(id, order[i]), color=color) for i, id in enumerate(user_ids)]
        
        # paste podiums on correct location
        dst = get_concat_h_multi_blank(podiums, padding, color=color)

        if not return_file:
            return dst
        
        # create buffer
        buffer = io.BytesIO()

        # save PNG in buffer
        dst.save(buffer, format='PNG')    

        # move to beginning of buffer so `send()` it will read from beginning
        buffer.seek(0)

        return discord.File(buffer, 'podium.png')   
    

def get_concat_h_multi_blank(im_list, padding, color=(44, 45, 47)):
    _im = im_list.pop(0)
    for im in im_list:
        _im = get_concat_h_blank(_im, im, padding, color)
    return _im


def get_concat_h_blank(im1, im2, padding, color=(44, 45, 47)):
    dst = Image.new('RGB', (im1.width + im2.width + padding, im1.height), color)
    dst.paste(im1, (0, 0))
    dst.paste(im2, (im1.width + padding, 0))
    return dst


def remove_transparency(im, color=(44, 45, 47)):
    im = im.convert("RGBA")
    new_image = Image.new("RGBA", im.size, color)
    new_image.paste(im, mask=im)

    return new_image.convert("RGB")


def resize_image(im, width, max_height=1000):
    wpercent = (width / float(im.size[0]))
    hsize = int((float(im.size[1]) * float(wpercent)))

    # calculated height exceedes max height
    if hsize > max_height:
        hsize = max_height
        hpercent = (hsize / float(im.size[1]))
        width = int((float(im.size[0]) * float(hpercent)))

    return im.resize((width, hsize), Image.Resampling.LANCZOS)