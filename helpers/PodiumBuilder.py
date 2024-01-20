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
                    (300, 1050), (255, 1130), (255, 1320)
                ],  
            },
            "273503117348306944": {
                "podiumLocation": "arno/ArnoPodium",
                "badgePasteCoords": [(255, 1050), (255, 1130), (255, 1320)],  
            },
            "222415043550117888": {
                "podiumLocation": "ba/BaPodium",
                "badgePasteCoords": [(255, 1050), (255, 1130), (255, 1320)],  
            },
            "559715606014984195": {
                "podiumLocation": "gible/GiblePodium",
                "shinyPodiumLocation": "gible/ShinyGiblePodium",
                "shinyPodiums": [1, 2, 3],
                "poseLocation": "gible/GiblePose",
                "amountOfCustomPoses": 5,
                "badgePasteCoords": [(515, 1050), (480, 1130), (370, 1320)],  
            },
            "494508091283603462": {
                "podiumLocation": "jacko/JackoPodium",
                "badgePasteCoords": [(255, 1050), (255, 1130), (255, 1320)],  
            },
            "339820557086228490": {
                "podiumLocation": "jakob/JakobPodium",
                "badgePasteCoords": [(255, 1050), (255, 1130), (255, 1320)],  
            },
            "527916521754722315": {
                "podiumLocation": "leander/LeanderPodium",
                "badgePasteCoords": [(255, 1050), (255, 1130), (280, 1320)],  
            },
            "512256261459542019": {
                "podiumLocation": "meng/MengPodium",
                "badgePasteCoords": [(255, 1050), (255, 1130), (255, 1320)],  
            },
            "464400950702899211": {
                "podiumLocation": "pingy/PingyPodium",
                "badgePasteCoords": [(255, 1050), (255, 1130), (255, 1320)],  
            },
            "462932133170774036": {
                "podiumLocation": "silas/SolosPodium",
                "badgePasteCoords": [(415, 1050), (255, 1130), (255, 1320)],   # TODO 2 & 3
                "poseOffset": [(0, 100), (0, 200), (0, 340)]
            },
            "453136562885099531": {
                "podiumLocation": "wouter/WouterPodium",
                "badgePasteCoords": [(255, 1050), (255, 1130), (255, 1320)],  
            },
            "733845345225670686": {
                "podiumLocation": "yachja/YachjaPodium",
                "shinyPodiumLocation": "yachja/ShinyYachjaPodium",
                "shinyPodiums": [3],

                "badgePasteCoords": [(1070, 1340), (320, 1130), (300, 1310)],
                "poseOffset": [(0, 400), (0, 200), (0, 340)]
            },  
            "756527409876041859": {
                "podiumLocation": "zeb/ZebPodium",
                "badgePasteCoords": [(255, 1050), (255, 1130), (255, 1320)],  
            },
        }



    def userHasPodium(self, user_id):
        return str(user_id) in self.definedArt
    


    async def getTopLeaderboard(self, leaderboard, command):
        #  load background
        bg = Image.open('media/images/LeaderboardTop.png')

        # load fonts
        fontb = ImageFont.truetype("media/fonts/contb.ttf", size=150)

        # create object for drawing
        draw = ImageDraw.Draw(bg)

        podiums = []

        # add places 1-5
        for i, stat in enumerate(leaderboard):
            
            # get user info
            user_id, count = tuple(stat)

            # normalize count
            count = human_format(count)
            
            # is podium, save info for later
            if i < 3:       
                podiums.append((user_id, count))

        # add podium
        podiumImage = await self.getAllPodiumsImage([pod[0] for pod in podiums], False, color=(62,62,62), add_characters=True)
        podiumImage = resize_image(podiumImage, 2000, 1800)
        remaining_width = bg.width - podiumImage.width

        bg.paste(podiumImage, (remaining_width//2, bg.height - podiumImage.height - 150))
    
        # draw title    
        draw.text(
            (1330, 240),
            text=command,
            align='center', font=fontb, anchor='mm', fill=(255, 104, 1)
        )

        # create buffer
        buffer = io.BytesIO()

        # save PNG in buffer
        bg.save(buffer, format='PNG')    

        # move to beginning of buffer so `send()` it will read from beginning
        buffer.seek(0)

        return discord.File(buffer, 'leaderboardtop.png')
    

    async def getBottomLeaderboard(self, leaderboard, command):
        #  load background
        bg = Image.open('media/images/LeaderboardBottom.png')

        # load fonts
        fontm = ImageFont.truetype("media/fonts/contm.ttf", size=120)

        # create object for drawing
        draw = ImageDraw.Draw(bg)

        # add places 4-8
        for i, stat in enumerate(leaderboard):
            
            # get user info
            user_id, count = tuple(stat)
            user = await self.bot.fetch_user(int(user_id))
            # normalize count
            count = human_format(count)
            
            # profile picture
            pfp = Image.open(requests.get(user.display_avatar.url, stream=True).raw)
            pfp = pfp.resize((240, 240))
            bg.paste(pfp, (550, 400 + i*3750))

            # username
            name = user.display_name if len(user.display_name) <= 16 else user.display_name[:13] + '...'
            draw.text(
                (1275, 350 + i*375), 
                text=name, 
                align='center', font=fontm, anchor='mm', fill=(255, 104, 1)
            )
            # count
            draw.text(
                (2050, 350 + i*375), 
                text=str(count), 
                align='center', font=fontm, anchor='mm', fill=(255, 104, 1)
            )


        # create buffer
        buffer = io.BytesIO()

        # save PNG in buffer
        bg.save(buffer, format='PNG')    

        # move to beginning of buffer so `send()` it will read from beginning
        buffer.seek(0)

        return discord.File(buffer, 'leaderboardbottom.png')
    
    

    async def getPodiumImage(self, user_id, place, alwaysShiny = False):
        # get object that contains info about the arts done
        defined_art = self.definedArt.get(str(user_id), {})

        # get location of the podium
        location = defined_art.get("podiumLocation", "default/DefaultPodium")

        # check if podium can be shiny and if it should be
        if "shinyPodiumLocation" in defined_art and place in defined_art.get("shinyPodiums", []) and alwaysShiny:
            location = defined_art.get("shinyPodiumLocation")
        
        # load the selected image
        image = Image.open(f'media/images/{location}{place}.png')
        #image = Image.open(f'C:/Users/Silas/OneDrive/Documenten/GitHub/WhereContextBot3/media/images/{location}{place}.png')
        
        return image
    

    async def addCharacterToPodium(self, podiumImage, user_id, poseNumber, place):
        # get object that contains info about the arts done
        defined_art = self.definedArt.get(user_id, {})

        # get location of the character
        customCharacterLocation = defined_art.get("poseLocation", "default/DefaultPose")

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
            for i, user_id in enumerate(user_ids):
                defined_art = self.definedArt.get(str(user_id), {})
                if "shinyPodiumLocation" in defined_art and order[i] in defined_art.get("shinyPodiums", []):
                    
                    # TODO uncomment
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
        defined_art = self.definedArt.get(str(user_id), {})
        location = defined_art.get("poseLocation", "default/DefaultPose")
        poses = [
            #remove_transparency(Image.open(f"C:/Users/Silas/OneDrive/Documenten/GitHub/WhereContextBot3/media/images/{location}{i+1}.png"))
            remove_transparency(Image.open(f"media/images/{location}{i+1}.png"))
            for i in range(self.getAmountOfPoses(user_id))
        ]
        dst = get_concat_h_multi_blank(poses, 150)

        # add poses to bg image
        bg = Image.new('RGB', (dst.width, dst.height + 400), (44, 45, 47))
        bg.paste(dst, (0,0))

        draw = ImageDraw.Draw(bg)
        font = ImageFont.truetype("media/fonts/contb.ttf", size=200)

        offsetPerPose = int(bg.width / (len(poses)+1))
        yPaste = int(dst.height + (bg.height - dst.height) // 2)

        # add numbering of poses
        for i in range(len(poses)+1):
            draw.text(
                (450+(offsetPerPose*i), yPaste),
                text=str(i+1),
                align='center', font=font, anchor='mm', fill=(255, 104, 1)
            )

        # create buffer
        buffer = io.BytesIO()

        # save PNG in buffer
        bg.save(buffer, format='PNG')    

        # move to beginning of buffer so `send()` it will read from beginning
        buffer.seek(0)

        return discord.File(buffer, 'poses.png')   
    


# concat multiple images with overlap (only if all 3 podiums present)
def get_concat(main_image, left_image, right_image, color=(44, 45, 47)):
    # calculate padding
    padding = max(left_image.width, right_image.width, main_image.width)//3
    
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