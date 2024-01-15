from PIL import Image, ImageDraw, ImageFont

import discord
import io
import requests
import random

from helpers import db_manager

class PodiumBuilder:
    def __init__(self, bot) -> None:
        self.bot = bot

        self.definedArt = {
            "334371900170043402": {
                "podiumLocation": "arion/ArionPodium",
                "badgePasteCoords": [
                    (255, 1050), (255, 1130), (255, 1320)
                ],  
            },
            "273503117348306944": {
                "podiumLocation": "arno/ArnoPodium",
                "badgePasteCoords": [
                    (255, 1050), (255, 1130), (255, 1320)
                ],  
            },
            "222415043550117888": {
                "podiumLocation": "ba/BaPodium",
                "badgePasteCoords": [
                    (255, 1050), (255, 1130), (255, 1320)
                ],  
            },
            "559715606014984195": {
                "podiumLocation": "gible/GiblePodium",
                "shinyPodiumLocation": "gible/ShinyGiblePodium",
                "badgePasteCoords": [
                    (255, 1050), (255, 1130), (255, 1320)
                ],  
            },
            "494508091283603462": {
                "podiumLocation": "jacko/JackoPodium",
                "badgePasteCoords": [
                    (255, 1050), (255, 1130), (255, 1320)
                ],  
            },
            "339820557086228490": {
                "podiumLocation": "jakob/JakobPodium",
                "badgePasteCoords": [
                    (255, 1050), (255, 1130), (255, 1320)
                ],  
            },
            "527916521754722315": {
                "podiumLocation": "leander/LeanderPodium",
                "badgePasteCoords": [
                    (255, 1050), (255, 1130), (255, 1320)
                ],  
            },
            "512256261459542019": {
                "podiumLocation": "meng/MengPodium",
                "badgePasteCoords": [
                    (255, 1050), (255, 1130), (255, 1320)
                ],  
            },
            "464400950702899211": {
                "podiumLocation": "pingy/PingyPodium",
                "badgePasteCoords": [
                    (255, 1050), (255, 1130), (255, 1320)
                ],  
            },
            "462932133170774036": {
                "podiumLocation": "silas/SolosPodium",
                #"poseLocation": "default/DefaultPose", # TODO
                #"amountOfCustomPoses": 5, #TODO
                "badgePasteCoords": [
                    (415, 1050), (255, 1130), (255, 1320) # TODO 2 & 3
                ],  
                "poseOffset": [
                    (0, 100), (0, 200), (0, 340)
                ]
            },
            "453136562885099531": {
                "podiumLocation": "wouter/WouterPodium",
                "badgePasteCoords": [
                    (255, 1050), (255, 1130), (255, 1320)
                ],  
            },
            "733845345225670686": {
                "podiumLocation": "yachja/YachjaPodium",
                "badgePasteCoords": [
                    (1070, 1340), (320, 1130), (300, 1310)
                ],
                "poseOffset": [
                    (0, 400), (0, 200), (0, 340)
                ]
            },  
            "756527409876041859": {
                "podiumLocation": "zeb/ZebPodium",
                "badgePasteCoords": [
                    (255, 1050), (255, 1130), (255, 1320)
                ],  
            },
        }

    def userHasPodium(self, user_id):
        return str(user_id) in self.definedArt

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
            # normalize count
            count = human_format(count)
            
            # is podium, save info for later
            if i < 3:       
                podiums.append((user_id, count))
            
            # is text
            else:
                # profile picture
                pfp = Image.open(requests.get(user.display_avatar.url, stream=True).raw)
                pfp = pfp.resize((232, 232))
                bg.paste(pfp, (525, 2250 + (i-3)*330))

                # username
                name = user.display_name if len(user.display_name) <= 16 else user.display_name[:13] + '...'
                draw.text(
                    (1200, 2375 + (i-3)*330), 
                    text=name, 
                    align='center', font=fontm, anchor='mm', fill=(255, 104, 1)
                )
                # count
                draw.text(
                    (1960, 2370 + (i-3)*330), 
                    text=str(count), 
                    align='center', font=fontm, anchor='mm', fill=(255, 104, 1)
                )

        # add podium
        podiumImage = await self.getAllPodiumsImage([pod[0] for pod in podiums], False, color=(62,62,62))
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
    

    async def getPodiumImage(self, user_id, place, alwaysShiny = False):
        # get object that contains info about the arts done
        defined_art = self.definedArt.get(str(user_id), {})

        # get location of the podium
        location = defined_art.get("podiumLocation", "default/DefaultPodium")

        # check if podium can be shiny and if it should be
        if "shinyPodiumLocation" in defined_art and alwaysShiny:
            location = defined_art.get("shinyPodiumLocation")
        
        # load the selected image
        image = Image.open(f'media/images/{location}{place}.png')
        #image = Image.open(f'C:/Users/Silas/OneDrive/Documenten/GitHub/WhereContextBot3/media/images/{location}{place}.png')
        
        return image
    

    async def addCharacterToPodium(self, podiumImage, user_id, poseNumber, place):
        # get object that contains info about the arts done
        defined_art = self.definedArt.get(user_id, {})

        # get location of the character
        customCharacterLocation = defined_art.get("characterLocation", "default/DefaultPose")

        # load the character image
        #characterImage = Image.open(f'C:/Users/Silas/OneDrive/Documenten/GitHub/WhereContextBot3/media/images/{customCharacterLocation}{poseNumber}.png')
        characterImage = Image.open(f'media/images/{customCharacterLocation}{poseNumber}.png')
        # resize it
        characterImage = resize_image(characterImage, 700)

        # create empty bg to add podium and character to
        bg = Image.new('RGBA', (podiumImage.width, podiumImage.height + characterImage.height))
        
        # paste podium
        bg.paste(podiumImage, (0, characterImage.height), podiumImage)

        # paste character
        offset = defined_art.get("poseOffset", [(0, 110), (0, 200), (0, 370)])[place-1]
        bg.paste(
            characterImage,
            ((bg.width - characterImage.width)//2 + offset[0], offset[1]), 
            characterImage
        )

        # paste badge to fix 3d realness of character standing on podium
        pasteCoords = defined_art.get("badgePasteCoords", [(255, 1050), (255, 1130), (255, 1320)])
        badgeImage = Image.open(f"media/images/Badge{place}.png")
        #badgeImage = Image.open(f"C:/Users/Silas/OneDrive/Documenten/GitHub/WhereContextBot3/media/images/Badge{place}.png")
        bg.paste(badgeImage, pasteCoords[place-1], badgeImage)

        # bg.show()
        return bg
    
    
    async def getAllPodiumsImage(self, user_ids, return_file=True, padding=200, color=(44, 45, 47), add_characters=True):
        # create normalised images for every given podium
        if len(user_ids) == 1:
            order = [1]
        elif len(user_ids) == 2:
            order = [2, 1]
        else:
            order = [2, 1, 3]
        
        # 1 in 12 chance that the podiums are shiny (if possible)
        alwaysShiny = random.randint(1, 12) == 2

        podiums = []
        # for every available user (top 3)
        for i, id in enumerate(user_ids):
            # get podium
            podiumImage = await self.getPodiumImage(id, order[i], alwaysShiny)

            if add_characters: 

                # get active pose and pick 1 at random
                poses = await db_manager.get_poses(str(id), i+1)
                if poses is not None:
                    pose = random.choice([int(pose) for pose in poses[0]])
                else:
                    pose = random.randint(1, self.getAmountOfPoses(str(id)))

                # add character
                podiumImage = await self.addCharacterToPodium(podiumImage, str(id), pose, order[i])

            podiums.append(podiumImage)

        
        # dm user if podium is shiny
        if alwaysShiny:
            for user_id in user_ids:
                if "shinyPodiumLocation" in self.definedArt.get(str(user_id), {}):
                
                    # await db_manager.increment_or_add_nword(int(user_id), 500)

                    embed = discord.Embed(
                        title='🎉 Congratulations!',
                        description=f"A shiny version of your podium has been pulled! You have been awarded 500 n-words.",
                        color=self.bot.succesColor,
                    )

                    user = self.bot.get_user(int(user_id))
                    # TODO uncomment 
                    # await user.send(embed=embed)


        # paste podiums on correct location
        if len(podiums) == 3:
            dst = get_concat(podiums[1], podiums[0], podiums[2], color=color)
        else:
            dst = get_concat_h_multi_blank(podiums, padding, color)

        # return as image if necessary
        if not return_file:
            return dst
        
        # create buffer
        buffer = io.BytesIO()

        # save PNG in buffer
        dst.save(buffer, format='PNG')    

        # move to beginning of buffer so `send()` it will read from beginning
        buffer.seek(0)

        return discord.File(buffer, 'podium.png')   
    


    def getAmountOfPoses(self, user_id):
        user_art = self.definedArt.get(str(user_id), {})
        return user_art.get("amountOfCustomPoses", 5)
    


    async def getAllPosesImage(self, user_id):
        location = self.definedArt.get("poseLocation", "default/DefaultPose")
        poses = [
            #remove_transparency(Image.open(f"C:/Users/Silas/OneDrive/Documenten/GitHub/WhereContextBot3/media/images/{location}{i+1}.png"))
            remove_transparency(Image.open(f"media/images/{location}{i+1}.png"))
            for i in range(self.getAmountOfPoses(user_id))
        ]
        dst = get_concat_h_multi_blank(poses, 150)

        # create buffer
        buffer = io.BytesIO()

        # save PNG in buffer
        dst.save(buffer, format='PNG')    

        # move to beginning of buffer so `send()` it will read from beginning
        buffer.seek(0)

        return discord.File(buffer, 'poses.png')   
    


# concat multiple images with overlap (only if all 3 podiums present)
def get_concat(main_image, left_image, right_image, color=(44, 45, 47)):
    # calculate padding
    padding = max(left_image.width, right_image.width)//3
    padding = min(200, padding)
    
    # create bg image with correct dimensions
    dst = Image.new(
        'RGBA', 
        (min(left_image.width, right_image.width) *3 + padding*2,
        max(left_image.height, main_image.height, right_image.height)),
        color
    )

    # paste the podiums onto the bg
    pasteWidth = (dst.width - main_image.width)//2
    dst.paste(main_image, (pasteWidth, 0), main_image)
    dst.paste(left_image, (0, dst.height - left_image.height), left_image)
    dst.paste(right_image, (dst.width - right_image.width, dst.height - left_image.height), right_image)
    
    return dst


# concat multiple images
def get_concat_h_multi_blank(im_list, padding, color=(44, 45, 47)):
    _im = im_list.pop(0)
    for im in im_list:
        _im = get_concat_h_blank(_im, im, padding, color)
    return _im


# concat 2 images
def get_concat_h_blank(im1, im2, padding, color=(44, 45, 47)):
    im1, im2 = remove_transparency(im1, color), remove_transparency(im2, color)
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


# get number in human format
def human_format(num):
    num = float('{:.3g}'.format(num))
    magnitude = 0
    while abs(num) >= 1000:
        magnitude += 1
        num /= 1000.0
    return '{}{}'.format('{:f}'.format(num).rstrip('0').rstrip('.'), ['', 'K', 'M', 'B', 'T'][magnitude])